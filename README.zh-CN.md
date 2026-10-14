# Learning Skills

[English](README.md)

三个可用于 Codex 和 DeepSeek Harness 的技能：把课程视频整理成阅读稿，讲清楚理解卡点，以及写出脱离聊天也能读懂的讲义。

每个技能是一份供 Agent 读取的指令。`course-to-notes` 还附带字幕解析、视频抽帧和输出检查脚本。三个技能可以独立安装；指令主要用中文，输出语言由你的请求决定。

## 选哪个技能

| 你想做的事 | 技能 |
| --- | --- |
| 按自己的基础选课，或把指定讲次整理成带时间定位和配图的阅读稿 | [course-to-notes](skills/course-to-notes/SKILL.md) |
| 弄明白一个定义、方法或证明步骤为什么这样写 | [explain-for-understanding](skills/explain-for-understanding/SKILL.md) |
| 编写或实质改写讲义，把读者需要的背景和推理连接补齐 | [obsidian-lecture-writing](skills/obsidian-lecture-writing/SKILL.md) |

## 安装

### DeepSeek Harness

在实际使用的 profile 中，将三个技能作为一个 DSH 插件安装：

```sh
dsh plugin --profile web add github:XSY-28/learning-skills
```

在 DSH 中调用 `/course-to-notes`、`/explain-for-understanding` 或 `/obsidian-lecture-writing`。前提、示例与更新方式见 [DSH 使用说明](docs/dsh.zh-CN.md)。

### Codex

在 Codex 中发送：

```text
使用 $skill-installer，从 XSY-28/learning-skills 安装以下路径：
- skills/course-to-notes
- skills/explain-for-understanding
- skills/obsidian-lecture-writing
```

只保留你需要的路径。安装后，发送一条新消息，用下面的示例调用技能；如果 Codex 找不到已安装的技能，再重启。

安装器不会覆盖已有的同名技能目录。替换旧版本前，先备份自己的修改。

<details>
<summary>从终端安装，或手动复制文件夹</summary>

如果你的 Codex 在标准位置提供了内置安装器，可以运行：

```sh
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo XSY-28/learning-skills \
  --path skills/course-to-notes skills/explain-for-understanding skills/obsidian-lecture-writing
```

也可以下载本仓库，将 `skills/` 下需要的技能文件夹复制到你配置的技能目录。请复制整个文件夹，包括参考材料、脚本、元数据和许可证。

</details>

## 使用

以下示例使用 Codex 语法；在 DSH 中将 `$技能名称` 换成 `/技能名称`，见 [DSH 使用说明](docs/dsh.zh-CN.md)。

### 讲清楚一个概念

```text
使用 $explain-for-understanding 解释正则化。
我会求导，但不明白为什么要在损失函数里加一项惩罚。
先用一个能手算的小例子讲起。
```

技能会要求 Codex 说明每个量的作用，把例子接到推导上，并交代结论的适用条件。

### 把课程整理成阅读稿

```text
使用 $course-to-notes，把我提供的课程前 10 分钟
整理成中文 Markdown 阅读稿，放到 ./course-notes。
```

工作流要求保留老师的讲授顺序、推导、问答和强调性重复，根据可用素材标注时间、选取配图，并说明缺失或无法核对的内容。提供学习记录后，还会给每章标注学习衔接和阅读建议；没有记录时标为待确认。

默认先读取完整可用字幕，建立讲授顺序与时间索引，再按需定位核对画面。必须播放时可用实际支持的倍速，密集推导和动态演示暂停或降速复查；字幕空档、未口述板书仍要补查，少量截图不能证明完整覆盖。这是处理流程优化，不保证固定提速倍数。

尚未选课时，可以先提供自己的基础和目标，请它推荐课程。

### 写一章讲义

```text
使用 $obsidian-lecture-writing，给只学过基础概率的读者
写一章条件期望的入门讲义。先在当前对话中交付。
```

技能会要求 Codex 在使用新概念前先把它讲清楚，解释关键步骤的理由，再从读者的基础出发检查正文。需要保存到 Obsidian 时，指定知识库和目标文件。

这些工作流用于学习和教学。公式速查、翻译和格式修复可以保持简短。自动选择技能取决于客户端；希望明确指定时，用 `$技能名称` 调用。

## 依赖

讲解和讲义技能没有脚本依赖。课程辅助脚本使用 Python 3.10+ 标准库；抽帧还需要 `PATH` 中可用的 `ffmpeg` 和 `ffprobe`。

获取视频、音频转写和 Word/PDF 导出取决于 Agent 环境中可用的工具。本仓库不附带视频下载器、转写模型或文档转换器。

## 验证与贡献

开发命令、测试范围和未验证能力见 [validation.md](docs/validation.md)。打包和辅助脚本检查通过，不代表生成的阅读稿内容正确，也不能证明读者已经掌握。

报告问题或贡献修改时，请提供具体请求、实际结果和预期结果。不要把私人笔记、学习记录、凭据或第三方课程媒体提交到仓库。

采用 [MIT 许可证](LICENSE)，覆盖本仓库原创的指令、代码和测试材料；课程素材仍受其自身条款约束。
