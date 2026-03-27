"""
AI Agent 资产 frontmatter 校验脚本。
职责：扫描 MD 文件，校验 YAML frontmatter 的完整性和合规性。
依赖：无（纯标准库）
被调用：asset-authoring Skill / CI 流水线
"""

import json
import sys
from enum import StrEnum
from pathlib import Path


class Severity(StrEnum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class AssetCategory(StrEnum):
    SKILLS = "skills"
    WORKFLOWS = "workflows"
    RULES = "rules"


# ── 有效值常量 ──
VALID_PROJECTS = frozenset({
    "dushan-admin-backend",
    "dushan-admin-frontend",
    "dushan-agent-assets",
    "dushan-devops",
    "dushan-codegen-mcp",
    "dushan-devops-mcp",
})

VALID_SCOPES = frozenset({"backend", "frontend", "universal"})

VALID_TRIGGERS = frozenset({"always_on", "on_demand"})

FRONTMATTER_ALLOWED_KEYS = frozenset({
    "description", "name", "trigger", "scope", "author", "project", "license",
})


def _extract_frontmatter(text: str) -> dict | None:
    """从文本中提取 YAML frontmatter 为字典，失败返回 None。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    meta: dict = {}
    current_key = ""
    in_multiline = False

    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break

        # 多行值的续行（以空格缩进开头）
        if in_multiline and (line.startswith("  ") or line.startswith("\t")):
            existing = meta.get(current_key, "")
            meta[current_key] = (existing + " " + stripped).strip()
            continue

        in_multiline = False

        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            current_key = key
            # YAML 多行 `>` 语法：后续缩进行会拼接
            if val == ">":
                meta[key] = ""
                in_multiline = True
                continue
            # 去除引号包裹
            if val.startswith('"') and val.endswith('"'):
                val = val[1:-1]
            meta[key] = val
    else:
        # 没有找到闭合的 `---`
        return None

    return meta


def _detect_category(file_path: Path) -> AssetCategory | None:
    """根据文件路径推断资产分类。"""
    parts = file_path.parts
    for part in parts:
        lower = part.lower()
        if lower == AssetCategory.SKILLS:
            return AssetCategory.SKILLS
        if lower == AssetCategory.WORKFLOWS:
            return AssetCategory.WORKFLOWS
        if lower == AssetCategory.RULES:
            return AssetCategory.RULES
    return None


def _detect_skill_dir_name(file_path: Path) -> str:
    """从 SKILL.md 路径推断技能目录名。"""
    return file_path.parent.name


def validate_file(file_path: Path) -> list[dict]:
    """校验单个 MD 文件的 frontmatter，返回问题列表。"""
    issues: list[dict] = []

    def _add(severity: Severity, rule: str, msg: str):
        issues.append({
            "file": str(file_path),
            "severity": severity.value,
            "rule": rule,
            "message": msg,
        })

    text = file_path.read_text(encoding="utf-8")
    category = _detect_category(file_path)

    # ── FM-1: frontmatter 存在性 ──
    meta = _extract_frontmatter(text)
    if meta is None:
        _add(Severity.ERROR, "FM-1", "缺少 YAML frontmatter（文件必须以 `---` 开头）")
        return issues

    # ── FM-2: description 必须存在 ──
    if "description" not in meta:
        # Skills 的 description 可能是多行 `>`，此时值为空但 key 存在
        _add(Severity.ERROR, "FM-2", "缺少 `description` 字段")

    # ── FM-3: project 值合法性 ──
    project_val = meta.get("project", "")
    if project_val and project_val not in VALID_PROJECTS:
        _add(
            Severity.WARNING, "FM-3",
            f"`project: {project_val}` 不在已知项目列表中，"
            f"有效值: {', '.join(sorted(VALID_PROJECTS))}",
        )
    if not project_val:
        _add(Severity.INFO, "FM-4", "未设置 `project` 字段（将归类为通用资产）")

    # ── FM-5: scope 值合法性 ──
    scope_val = meta.get("scope", "")
    if scope_val and scope_val not in VALID_SCOPES:
        _add(
            Severity.WARNING, "FM-5",
            f"`scope: {scope_val}` 无效，有效值: {', '.join(sorted(VALID_SCOPES))}",
        )

    # ── Skills 专属校验 ──
    if category == AssetCategory.SKILLS:
        # FM-6: name 与目录名一致
        name_val = meta.get("name", "")
        dir_name = _detect_skill_dir_name(file_path)
        if name_val and name_val != dir_name:
            _add(
                Severity.ERROR, "FM-6",
                f"`name: {name_val}` 与目录名 `{dir_name}` 不一致",
            )
        if not name_val:
            _add(Severity.WARNING, "FM-7", "Skills 建议设置 `name` 字段")

    # ── Rules 专属校验 ──
    if category == AssetCategory.RULES:
        trigger_val = meta.get("trigger", "")
        if trigger_val and trigger_val not in VALID_TRIGGERS:
            _add(
                Severity.WARNING, "FM-8",
                f"`trigger: {trigger_val}` 无效，有效值: {', '.join(sorted(VALID_TRIGGERS))}",
            )
        if not trigger_val:
            _add(Severity.INFO, "FM-9", "Rules 建议设置 `trigger` 字段")

    # ── FM-10: 未知字段检测 ──
    unknown_keys = set(meta.keys()) - FRONTMATTER_ALLOWED_KEYS
    if unknown_keys:
        _add(
            Severity.INFO, "FM-10",
            f"发现未知 frontmatter 字段: {', '.join(sorted(unknown_keys))}",
        )

    return issues


def scan_directory(root: Path) -> list[dict]:
    """递归扫描目录中所有资产 MD 文件。"""
    all_issues: list[dict] = []

    for category in (AssetCategory.SKILLS, AssetCategory.WORKFLOWS, AssetCategory.RULES):
        cat_dir = root / category
        if not cat_dir.exists():
            continue

        if category == AssetCategory.SKILLS:
            for child in sorted(cat_dir.iterdir()):
                if child.is_dir():
                    skill_md = child / "SKILL.md"
                    if skill_md.exists():
                        all_issues.extend(validate_file(skill_md))
                    else:
                        all_issues.append({
                            "file": str(child),
                            "severity": Severity.ERROR,
                            "rule": "DIR-1",
                            "message": f"Skill 目录 `{child.name}` 缺少 SKILL.md",
                        })
        else:
            for md_file in sorted(cat_dir.glob("*.md")):
                if md_file.name == "README.md":
                    continue
                all_issues.extend(validate_file(md_file))

    return all_issues


def _format_summary(issues: list[dict]) -> str:
    """输出人类可读的摘要报告。"""
    if not issues:
        return "✅ 全部通过，未发现问题"

    lines: list[str] = []
    error_count = sum(1 for i in issues if i["severity"] == Severity.ERROR)
    warn_count = sum(1 for i in issues if i["severity"] == Severity.WARNING)
    info_count = sum(1 for i in issues if i["severity"] == Severity.INFO)

    lines.append(f"扫描完成: {error_count} ERROR / {warn_count} WARNING / {info_count} INFO\n")

    # 按文件分组
    by_file: dict[str, list[dict]] = {}
    for issue in issues:
        by_file.setdefault(issue["file"], []).append(issue)

    for filepath, file_issues in by_file.items():
        lines.append(f"📄 {filepath}")
        for issue in file_issues:
            icon = {"ERROR": "❌", "WARNING": "⚠️", "INFO": "ℹ️"}[issue["severity"]]
            lines.append(f"   {icon} [{issue['rule']}] {issue['message']}")
        lines.append("")

    return "\n".join(lines)


def main():
    """CLI 入口。"""
    if len(sys.argv) < 2:
        print(f"用法: python {sys.argv[0]} <文件或目录> [--format summary|json]")
        print(f"示例: python {sys.argv[0]} ../../rules/backend-global.md")
        print(f"示例: python {sys.argv[0]} ../../../dushan-agent-assets")
        sys.exit(1)

    target = Path(sys.argv[1])
    output_format = "summary"

    if "--format" in sys.argv:
        idx = sys.argv.index("--format")
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]

    if not target.exists():
        print(f"❌ 路径不存在: {target}")
        sys.exit(1)

    if target.is_file():
        issues = validate_file(target)
    else:
        issues = scan_directory(target)

    if output_format == "json":
        print(json.dumps(issues, ensure_ascii=False, indent=2))
    else:
        print(_format_summary(issues))

    # 退出码：有 ERROR 返回 1
    has_errors = any(i["severity"] == Severity.ERROR for i in issues)
    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
