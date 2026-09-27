# Learning Skills：学习与讲义技能

三个可独立安装的 Codex 技能，分别用于课程阅读稿、深入理解式讲解和自足讲义写作。

[English](README.md) · [MIT 许可证](LICENSE) · [验证范围](docs/validation.md)

这是供智能体使用的指令与辅助工具，不是独立应用。技能正文主要使用中文，输出语言服从当前请求；三个技能互不依赖。

## 选择技能

| 技能 | 适用场景 | 核心做法 |
| --- | --- | --- |
| [course-to-notes](skills/course-to-notes/SKILL.md) | 选择视频课程；将指定讲次整理成有时间定位和配图的阅读稿 | 保留实际讲授的动机、推导、例子、问答与强调性重复；区分原讲、编者补充和推断；依据证据标记学习衔接，独立判断课程重点 |
| [explain-for-understanding](skills/explain-for-understanding/SKILL.md) | 系统学习新概念，或修复具体理解卡点 | 先建立对象与动机，用具体例子串起推导，解释为何想到这种方法及结论何时成立 |
| [obsidian-lecture-writing](skills/obsidian-lecture-writing/SKILL.md) | 编写或实质改写可独立阅读的讲义正文 | 按概念依赖组织内容，提供章首引导、章末回顾，并从读者视角检查连接和迁移 |

公式速查、翻译、纯格式修复和普通编码排错应保持原任务范围。仅出现学科关键词、Obsidian 路径，或此前进行过教学，都不应自动变成长篇讲解。

## 安装到 Codex

在 Codex 中请求：

```text
使用 $skill-installer，从 XSY-28/learning-skills 安装以下技能：
- skills/course-to-notes
- skills/explain-for-understanding
- skills/obsidian-lecture-writing
```

只需要一个时，仅保留对应路径。如果 Codex 的标准位置已有内置安装脚本，也可运行：

```sh
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo XSY-28/learning-skills \
  --path skills/course-to-notes skills/explain-for-understanding skills/obsidian-lecture-writing
```

安装器遇到已有同名目录会拒绝覆盖。如果需要更新，先备份本地修改，再明确替换。安装完成后重启 Codex。技能允许自动选择，但不同客户端的实际自动路由尚未验证；需要指定工作流时，可显式使用技能名称。

也可以下载仓库，将 `skills/` 下所需的完整技能文件夹复制到配置的技能目录，保留其中的 `references/`、`agents/`、存在时的 `scripts/` 以及 `LICENSE`。

## 使用示例

**课程阅读稿**

```text
使用 $course-to-notes 整理我提供的课程前 10 分钟。
用中文 Markdown，输出到当前项目的 course-notes。
保留教学顺序、强调性重复、推导、时间定位和有用的配图；
区分原讲与编者补充，说明无法核对的内容。
```

尚未选课时，可以先给目标与基础，请技能比较少量候选，选定后再处理。没有学习记录时继续整理并标为“待确认”，不因生成了笔记就认定已经学会。

**深入理解式讲解**

```text
使用 $explain-for-understanding 讲清楚正则化为什么改变了优化目标。
我会求导，但刚接触机器学习。请用一个能手算的例子，
说明每个量是什么、为什么这样构造，以及结论的适用条件。
```

**Obsidian 深入理解式讲义**

```text
使用 $obsidian-lecture-writing 写一章条件期望的入门讲义。
假设读者只学过基础概率；先建立对象和动机，再引入公式。
每章有开头引导和结尾回顾，检查读者能否只用正文完成一个小变式。
先在对话中交付，不写入知识库。
```

需要写入 Obsidian 时，指定实际 vault 与输出位置。技能不预设私人路径，也不内置某个用户的学科背景。

## 依赖与边界

- 讲解与讲义技能没有脚本依赖。文件操作和 Obsidian 阅读视图检查取决于智能体环境中的工具。
- 课程辅助脚本使用 Python 3.10+ 标准库；抽帧另外需要 `PATH` 中可用的 `ffmpeg` 与 `ffprobe`。
- 选课搜索、媒体获取、语音识别、视觉检查、Word/PDF 生成与渲染，需要宿主环境提供对应能力；仓库不内置 ASR 模型、下载器或文档转换器。
- 使用有适当授权的课程素材并保留来源署名。MIT 许可证适用于本仓库原创指令、代码及合成测试材料，不授予第三方课程媒体或其衍生内容的使用权。
- 结构通过不等于内容正确、整讲覆盖、教学有效或学习者已经掌握。

## 开发与验证

在仓库根目录运行：

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/check_package.py
python3 -m unittest discover -s tests/course-to-notes -v
```

PyYAML 仅用于开发期结构校验。28 项课程测试涵盖字幕解析、合成视频抽帧与输出契约；缺少 FFmpeg 工具时抽帧测试明确跳过，不能算作通过。CI 会安装 FFmpeg 后执行。

[验证范围说明](docs/validation.md) 区分当前可复现检查与未验证能力。课程技能中的行为验收表是待执行任务，不表示所有场景都已通过。

欢迎基于具体失败案例或使用需求贡献修改，保留技能触发边界、学习证据区分及手动修改保护，并运行相关检查。请勿提交课程媒体、私人学习记录、凭据或生成的私人笔记。
