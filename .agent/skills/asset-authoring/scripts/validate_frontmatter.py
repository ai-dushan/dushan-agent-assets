"""
AI Agent 资产校验脚本（全量 Lint）。
职责：扫描 MD 文件，校验 YAML frontmatter + 内容结构 + 目录完整性。
依赖：无（纯标准库）
被调用：asset-authoring Skill / CI 流水线
"""

import json
import re
import sys
from enum import StrEnum
from pathlib import Path


class Severity(StrEnum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class AssetCategory(StrEnum):
    SKILLS = "skills"
    RULES = "rules"


# ── 有效值常量 ──
VALID_PROJECTS = frozenset(
    {
        "dushan-admin-backend",
        "dushan-admin-frontend",
        "dushan-agent-assets",
        "dushan-devops",
        "dushan-codegen-mcp",
        "dushan-graph-mcp",
    }
)

VALID_SCOPES = frozenset({"backend", "frontend", "universal", "devops"})

VALID_TRIGGERS = frozenset({"always_on", "on_demand"})

FRONTMATTER_ALLOWED_KEYS = frozenset(
    {
        "description",
        "name",
        "trigger",
        "scope",
        "author",
        "project",
        "license",
    }
)

# ── Skills 内容结构常量 ──
SKILL_REQUIRED_SECTIONS = (
    "何时使用",
    "何时不使用",
)

SKILL_DESCRIPTION_PREFIX = "【技能】"
RULE_DESCRIPTION_PREFIX = "【规则】"

SKILL_MAX_LINES = 600
SKILL_MAX_H2_SECTIONS = 15

# Rules MCP 指针关键词
RULE_MCP_KEYWORDS = (
    "codegen-mcp",
    "cli rules",
    "python -m cli",
)


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


def _extract_body(text: str) -> str:
    """提取 frontmatter 之后的正文内容。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text

    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[i + 1 :])
    return text


def _extract_h2_headings(body: str) -> list[str]:
    """提取正文中所有 ## 标题。"""
    return [
        match.group(1).strip()
        for match in re.finditer(r"^##\s+(.+)$", body, re.MULTILINE)
    ]


def _detect_category(file_path: Path) -> AssetCategory | None:
    """根据文件路径推断资产分类。"""
    parts = file_path.parts
    for part in parts:
        lower = part.lower()
        if lower == AssetCategory.SKILLS:
            return AssetCategory.SKILLS
        if lower == AssetCategory.RULES:
            return AssetCategory.RULES
    return None


def _detect_skill_dir_name(file_path: Path) -> str:
    """从 SKILL.md 路径推断技能目录名。"""
    return file_path.parent.name


# ── Frontmatter 校验 ──


def _validate_frontmatter(
    meta: dict,
    category: AssetCategory | None,
    file_path: Path,
) -> list[dict]:
    """校验 frontmatter 字段合规性。"""
    issues: list[dict] = []

    def _add(severity: Severity, rule: str, msg: str):
        issues.append(
            {
                "file": str(file_path),
                "severity": severity.value,
                "rule": rule,
                "message": msg,
            }
        )

    # FM-2: description 必须存在
    if "description" not in meta:
        _add(Severity.ERROR, "FM-2", "缺少 `description` 字段")

    # FM-3: project 值合法性
    project_val = meta.get("project", "")
    if project_val and project_val not in VALID_PROJECTS:
        _add(
            Severity.WARNING,
            "FM-3",
            f"`project: {project_val}` 不在已知项目列表中，"
            f"有效值: {', '.join(sorted(VALID_PROJECTS))}",
        )
    if not project_val:
        _add(Severity.INFO, "FM-4", "未设置 `project` 字段（将归类为通用资产）")

    # FM-5: scope 值合法性
    scope_val = meta.get("scope", "")
    if scope_val and scope_val not in VALID_SCOPES:
        _add(
            Severity.WARNING,
            "FM-5",
            f"`scope: {scope_val}` 无效，有效值: {', '.join(sorted(VALID_SCOPES))}",
        )

    # Skills 专属
    if category == AssetCategory.SKILLS:
        name_val = meta.get("name", "")
        dir_name = _detect_skill_dir_name(file_path)
        if name_val and name_val != dir_name:
            _add(
                Severity.ERROR,
                "FM-6",
                f"`name: {name_val}` 与目录名 `{dir_name}` 不一致",
            )
        if not name_val:
            _add(Severity.WARNING, "FM-7", "Skills 建议设置 `name` 字段")

    # Rules 专属
    if category == AssetCategory.RULES:
        trigger_val = meta.get("trigger", "")
        if trigger_val and trigger_val not in VALID_TRIGGERS:
            _add(
                Severity.WARNING,
                "FM-8",
                f"`trigger: {trigger_val}` 无效，有效值: {', '.join(sorted(VALID_TRIGGERS))}",
            )
        if not trigger_val:
            _add(Severity.INFO, "FM-9", "Rules 建议设置 `trigger` 字段")

    # FM-10: 未知字段
    unknown_keys = set(meta.keys()) - FRONTMATTER_ALLOWED_KEYS
    if unknown_keys:
        _add(
            Severity.INFO,
            "FM-10",
            f"发现未知 frontmatter 字段: {', '.join(sorted(unknown_keys))}",
        )

    return issues


# ── Skills 内容结构校验 ──


def _validate_skill_content(
    body: str,
    meta: dict,
    file_path: Path,
) -> list[dict]:
    """校验 SKILL.md 正文的内容结构。"""
    issues: list[dict] = []

    def _add(severity: Severity, rule: str, msg: str):
        issues.append(
            {
                "file": str(file_path),
                "severity": severity.value,
                "rule": rule,
                "message": msg,
            }
        )

    full_text_lines = body.splitlines()
    line_count = len(full_text_lines)

    # SK-1: description 必须以【技能】开头
    desc = meta.get("description", "")
    if desc and not desc.startswith(SKILL_DESCRIPTION_PREFIX):
        _add(
            Severity.WARNING,
            "SK-1",
            f"Skill `description` 建议以 `{SKILL_DESCRIPTION_PREFIX}` 开头，"
            f"当前: `{desc[:40]}...`",
        )

    # SK-2: 必须包含"何时使用"和"何时不使用"章节
    headings = _extract_h2_headings(body)
    heading_texts = [h.lower().replace(" ", "") for h in headings]
    for required in SKILL_REQUIRED_SECTIONS:
        normalized = required.lower().replace(" ", "")
        if not any(normalized in h for h in heading_texts):
            _add(
                Severity.WARNING,
                "SK-2",
                f"缺少 `## {required}` 章节",
            )

    # SK-3: 文件长度检查
    if line_count > SKILL_MAX_LINES:
        _add(
            Severity.WARNING,
            "SK-3",
            f"SKILL.md 共 {line_count} 行，超过建议上限 {SKILL_MAX_LINES} 行，"
            f"建议拆分到 reference/ 子目录",
        )

    # SK-4: H2 章节数量检查
    if len(headings) > SKILL_MAX_H2_SECTIONS:
        _add(
            Severity.WARNING,
            "SK-4",
            f"共 {len(headings)} 个 `##` 章节，超过建议上限 {SKILL_MAX_H2_SECTIONS}，"
            f"建议合并或拆分",
        )

    # SK-5: 必须有 H1 标题
    h1_matches = re.findall(r"^#\s+(.+)$", body, re.MULTILINE)
    if not h1_matches:
        _add(Severity.ERROR, "SK-5", "缺少 `# 标题`（H1 级标题）")

    # SK-6: 不应包含 TODO / FIXME / HACK 标记
    todo_pattern = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b", re.IGNORECASE)
    for i, line in enumerate(full_text_lines, start=1):
        if todo_pattern.search(line):
            _add(
                Severity.INFO,
                "SK-6",
                f"第 {i} 行包含待处理标记: `{line.strip()[:60]}`",
            )
            break  # 只报第一个

    # SK-7: 检查死链接（引用 scripts/ 但文件不存在）
    skill_dir = file_path.parent
    script_refs = re.findall(r"scripts/(\S+)", body)
    for ref in script_refs:
        # 去除 markdown 尾缀
        ref_clean = ref.rstrip(")`\"'")
        ref_path = skill_dir / "scripts" / ref_clean
        if not ref_path.exists() and not (skill_dir / "scripts").exists():
            pass  # 无 scripts 目录时不报，避免误报
        elif not ref_path.exists() and (skill_dir / "scripts").exists():
            _add(
                Severity.WARNING,
                "SK-7",
                f"引用了 `scripts/{ref_clean}` 但文件不存在",
            )

    # SK-8: 检查空的代码块
    code_block_pattern = re.compile(r"```(\w*)\n\s*```", re.MULTILINE)
    empty_blocks = code_block_pattern.findall(body)
    if empty_blocks:
        _add(
            Severity.WARNING,
            "SK-8",
            f"发现 {len(empty_blocks)} 个空代码块",
        )

    return issues


# ── Rules 内容结构校验 ──


def _validate_rule_content(
    body: str,
    meta: dict,
    file_path: Path,
) -> list[dict]:
    """校验 Rule 正文的内容结构。"""
    issues: list[dict] = []

    def _add(severity: Severity, rule: str, msg: str):
        issues.append(
            {
                "file": str(file_path),
                "severity": severity.value,
                "rule": rule,
                "message": msg,
            }
        )

    # RL-1: description 应以【规则】开头
    desc = meta.get("description", "")
    if desc and not desc.startswith(RULE_DESCRIPTION_PREFIX):
        _add(
            Severity.INFO,
            "RL-1",
            f"Rule `description` 建议以 `{RULE_DESCRIPTION_PREFIX}` 开头",
        )

    # RL-2: 必须包含 MCP 指针关键词
    body_lower = body.lower()
    has_mcp_ref = any(kw in body_lower for kw in RULE_MCP_KEYWORDS)
    if not has_mcp_ref:
        _add(
            Severity.WARNING,
            "RL-2",
            "Rule 正文未引用 MCP CLI 指令（codegen-mcp / cli rules / python -m cli），"
            "Rules 应作为 MCP 指针而非硬编码规则",
        )

    # RL-3: 不应过长（指针应轻量）
    line_count = len(body.splitlines())
    if line_count > 50:
        _add(
            Severity.WARNING,
            "RL-3",
            f"Rule 正文共 {line_count} 行，超过建议上限 50 行，"
            f"Rules 应保持轻量，具体逻辑下沉到 Skills",
        )

    # RL-4: 不应包含代码块（规则是指针，不是实现）
    code_blocks = re.findall(r"```\w+\n", body)
    # 允许 yaml/bash 配置块（常用于展示 CLI 命令），禁止 python/ts 等实现块
    impl_blocks = [
        b
        for b in code_blocks
        if not any(lang in b for lang in ("```yaml", "```bash", "```text", "```json"))
    ]
    if impl_blocks:
        _add(
            Severity.INFO,
            "RL-4",
            f"Rule 正文包含 {len(impl_blocks)} 个实现代码块，"
            f"Rules 应仅包含配置/命令块，具体实现下沉到 Skills",
        )

    return issues


# ── 目录结构校验 ──


def _validate_skill_directory(skill_dir: Path) -> list[dict]:
    """校验 Skill 目录的结构完整性。"""
    issues: list[dict] = []

    def _add(severity: Severity, rule: str, msg: str):
        issues.append(
            {
                "file": str(skill_dir),
                "severity": severity.value,
                "rule": rule,
                "message": msg,
            }
        )

    # DIR-2: 检查是否有孤立文件（非 SKILL.md、非子目录、非 __pycache__）
    allowed_children = {
        "SKILL.md",
        "scripts",
        "templates",
        "examples",
        "reference",
        "__pycache__",
        ".gitkeep",
    }
    for child in skill_dir.iterdir():
        if child.name in allowed_children:
            continue
        if child.name.startswith("."):
            continue
        _add(
            Severity.INFO,
            "DIR-2",
            f"Skill 目录中发现非标准文件/目录: `{child.name}`，"
            f"建议放入 scripts/ / templates/ / reference/",
        )

    # DIR-3: scripts/ 目录存在但为空
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        script_files = [
            f
            for f in scripts_dir.iterdir()
            if f.is_file() and not f.name.startswith(".")
        ]
        if not script_files:
            _add(
                Severity.INFO,
                "DIR-3",
                "scripts/ 目录存在但为空，建议删除或添加脚本",
            )

    return issues


# ── 主校验入口 ──


def validate_file(file_path: Path) -> list[dict]:
    """校验单个 MD 文件的 frontmatter + 内容结构，返回问题列表。"""
    issues: list[dict] = []

    def _add(severity: Severity, rule: str, msg: str):
        issues.append(
            {
                "file": str(file_path),
                "severity": severity.value,
                "rule": rule,
                "message": msg,
            }
        )

    text = file_path.read_text(encoding="utf-8")
    category = _detect_category(file_path)

    # FM-1: frontmatter 存在性
    meta = _extract_frontmatter(text)
    if meta is None:
        _add(Severity.ERROR, "FM-1", "缺少 YAML frontmatter（文件必须以 `---` 开头）")
        return issues

    # Frontmatter 字段校验
    issues.extend(_validate_frontmatter(meta, category, file_path))

    # 内容结构校验
    body = _extract_body(text)

    if category == AssetCategory.SKILLS:
        issues.extend(_validate_skill_content(body, meta, file_path))
        issues.extend(_validate_skill_directory(file_path.parent))
    elif category == AssetCategory.RULES:
        issues.extend(_validate_rule_content(body, meta, file_path))

    return issues


def scan_directory(root: Path) -> list[dict]:
    """递归扫描目录中所有资产 MD 文件。"""
    all_issues: list[dict] = []

    for category in (
        AssetCategory.SKILLS,
        AssetCategory.RULES,
    ):
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
                        all_issues.append(
                            {
                                "file": str(child),
                                "severity": Severity.ERROR,
                                "rule": "DIR-1",
                                "message": f"Skill 目录 `{child.name}` 缺少 SKILL.md",
                            }
                        )
        else:
            for md_file in sorted(cat_dir.glob("*.md")):
                if md_file.name == "README.md":
                    continue
                all_issues.extend(validate_file(md_file))

    return all_issues


def scan_workspace(workspace_root: Path) -> list[dict]:
    """扫描工作区中所有 .agent/skills/ 目录下的 Skill。"""
    all_issues: list[dict] = []

    # 扫描 .agent/skills/ 下的每个 Skill
    agent_skills = workspace_root / ".agent" / "skills"
    if agent_skills.is_dir():
        for child in sorted(agent_skills.iterdir()):
            if child.is_dir():
                skill_md = child / "SKILL.md"
                if skill_md.exists():
                    all_issues.extend(validate_file(skill_md))
                else:
                    all_issues.append(
                        {
                            "file": str(child),
                            "severity": Severity.ERROR,
                            "rule": "DIR-1",
                            "message": f"Skill 目录 `{child.name}` 缺少 SKILL.md",
                        }
                    )

    # 扫描 .agents/rules/ 下的 Rule
    agents_rules = workspace_root / ".agents" / "rules"
    if not agents_rules.is_dir():
        agents_rules = workspace_root / ".agents" / "_rules"
    if agents_rules.is_dir():
        for md_file in sorted(agents_rules.glob("*.md")):
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

    lines.append(
        f"扫描完成: {error_count} ERROR / {warn_count} WARNING / {info_count} INFO\n"
    )

    # 按规则分类统计
    rule_counts: dict[str, int] = {}
    for issue in issues:
        rule_counts[issue["rule"]] = rule_counts.get(issue["rule"], 0) + 1
    if rule_counts:
        lines.append("规则命中统计:")
        for rule_id, count in sorted(rule_counts.items()):
            lines.append(f"  {rule_id}: {count} 次")
        lines.append("")

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
        print(
            f"用法: python {sys.argv[0]} <文件或目录> [--format summary|json] [--workspace]"
        )
        print()
        print("模式:")
        print("  默认         扫描 dushan-agent-assets 的 skills/ + rules/ 目录")
        print("  --workspace  扫描任意项目工作区的 .agent/skills/ + .agents/rules/")
        print()
        print(f"示例: python {sys.argv[0]} ../../rules/backend-global.md")
        print(f"示例: python {sys.argv[0]} ../../../dushan-agent-assets")
        print(f"示例: python {sys.argv[0]} ../../../dushan-admin-backend --workspace")
        sys.exit(1)

    target = Path(sys.argv[1])
    output_format = "summary"
    workspace_mode = "--workspace" in sys.argv

    if "--format" in sys.argv:
        idx = sys.argv.index("--format")
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]

    if not target.exists():
        print(f"❌ 路径不存在: {target}")
        sys.exit(1)

    if target.is_file():
        issues = validate_file(target)
    elif workspace_mode:
        issues = scan_workspace(target)
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
