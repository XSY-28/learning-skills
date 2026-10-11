# 在 DeepSeek Harness 中使用 Learning Skills

[English](dsh.md)

`dsh-learning-skills` 插件向 DSH 技能注册表提供三个技能。它们保留各自的名称、正文、参考文件和辅助脚本，与 Codex 安装共用源码目录。

## 安装和调用

已安装 DSH 后，将插件添加到实际使用的 profile；使用其他 profile 时替换 `web`：

```sh
dsh plugin --profile web add github:XSY-28/learning-skills
```

启动或重启该 profile。它需要包含 `dsh-skill` 注册表与 `dsh-tool-skill` 消费方；Standard 模式包含技能支持。本包添加技能提供方，不替换 Agent preset 或权限设置。

在 DSH 中使用斜杠形式，而不是 Codex 的 `$名称`：

```text
/explain-for-understanding 解释正则化。我会求导，但不明白为什么要在损失函数中加入惩罚项。

/course-to-notes 把我提供的课程视频和同版本字幕的前 10 分钟整理成中文 Markdown 阅读稿，保存到 ./course-notes。

/obsidian-lecture-writing 给只学过基础概率的读者写一章条件期望的入门讲义。先在当前对话中交付。
```

模型也可以通过 DSH 的 `skill` 工具加载适用技能。加载结果包含技能目录，供它定位相对引用和脚本。`agents/openai.yaml` 保留为 Codex 元数据；DSH 使用从 `SKILL.md` 文件头生成的插件目录。

## 依赖与限制

- 已测试 SDK：DSH `0.1.7-rc.2`、Cordis `4.0.4`；Node.js `^22.19.0 || >=24.0.0`。peer 版本范围显式允许已测的预发布系列，后续预发布系列需重新核对兼容性。
- 讲解和讲义技能没有辅助脚本依赖。课程脚本需要 Python 3.10+，抽帧需要 `PATH` 中的 `ffmpeg` 和 `ffprobe`。
- 视频获取、转录、图像理解、文档导出与 Obsidian 界面检查取决于 DSH 中实际可用的工具和模型。本插件不提供这些能力，也不扩大权限。
- 同一注册表 scope 中，项目或用户目录里的同名技能优先于本包默认值。希望使用本包版本时，注意是否保留了同名旧副本。
- 包内直接提供 JavaScript 和资源，没有安装期构建；本包不需要批准 `prepare` 脚本。

实际执行的检查见[验证范围](validation.md)。注册和加载测试不能证明模型自动选对技能、教学质量或完整的视频处理会话。

## 更新与移除

使用同一 profile 的 DSH 插件管理功能。使用 `dsh plugin --profile web update dsh-learning-skills` 更新 GitHub 依赖，重启 profile，再检查实际加载的技能。移除命令为：

```sh
dsh plugin --profile web remove dsh-learning-skills
```

Codex 中复制安装的技能有独立更新流程；更新 DSH 插件不会替换那些副本。
