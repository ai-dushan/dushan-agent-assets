---
name: brand-guidelines
description: 将 Anthropic 的官方品牌色彩和排版规范应用到任何可能受益于 Anthropic 外观和风格的材料组件上。当涉及品牌色彩或样式指南、视觉排版或公司设计标准时使用此技能。
license: Complete terms in LICENSE.txt
scope: universal
author: Anthropic
---

# Anthropic 品牌样式指南

## 概述

若需访问和使用 Anthropic 的官方品牌标识和样式资源，请使用此技能。

**关键字**：品牌推广（branding）、企业标志（corporate identity）、视觉标识（visual identity）、后处理（post-processing）、样式设置（styling）、品牌色彩（brand colors）、排版（typography）、Anthropic 品牌（Anthropic brand）、视觉排版（visual formatting）、视觉设计（visual design）

## 品牌指南

### 颜色

**主色调：**

- 深色（Dark）：`#141413` - 主要文本和深色背景
- 浅色（Light）：`#faf9f5` - 浅色背景和深色背景上的文字
- 中度灰（Mid Gray）：`#b0aea5` - 次要元素
- 浅灰（Light Gray）：`#e8e6dc` - 柔和的背景

**强调色（Accent Colors）：**

- 橙色（Orange）：`#d97757` - 首要强调色
- 蓝色（Blue）：`#6a9bcc` - 次要强调色
- 绿色（Green）：`#788c5d` - 第三强调色

### 排版字体

- **标题（Headings）**：Poppins（Arial 作为后备字体）
- **正文（Body Text）**：Lora（Georgia 作为后备字体）
- **注意**：为了获得最佳效果，字体应预先安装在您的环境中

## 功能特性

### 智能字体应用

- 将 Poppins 字体应用于标题（24pt 及以上）
- 将 Lora 字体应用于正文文本
- 如果自定义字体不可用，将自动降级退回到 Arial/Georgia
- 在所有系统上保持可读性

### 文本样式

- 标题（24pt+）：Poppins 字体
- 正文：Lora 字体
- 基于背景执行智能颜色选择
- 保留文本的层级结构和格式

### 形状与强调色

- 非文本形状使用强调色
- 在橙色、蓝色和绿色强调色之间循环使用
- 在保持符合品牌调性的同时维持视觉吸引力

## 技术细节

### 字体管理

- 优先使用系统安装的 Poppins 和 Lora 字体（如果有）
- 提供自动后备方案：Arial（标题）和 Georgia（正文）
- 无需强制安装字体 - 可与现有的系统默认字体配合使用
- 想获得最佳渲染效果，请在您的环境中预先安装 Poppins 和 Lora 字体

### 颜色应用

- 使用 RGB 颜色值以实现精准的品牌色彩匹配
- 通过 `python-pptx` 的 `RGBColor` 类进行应用
- 跨不同系统维持一致的色彩保真度
