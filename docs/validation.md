# Validation scope

This public repository contains three skill packages and wholly synthetic course-tool fixtures. It contains no real course media, transcripts, or personal learning records. An example learner profile in a fixture is synthetic, not a record about a real person.

## Reproducible checks

Run from the repository root:

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/check_package.py
python3 -m unittest discover -s tests/course-to-notes -v
```

- **Package validation:** skill names and descriptions, UI metadata, invocation policy, bundled licenses, and local Markdown link targets outside fenced examples. This checks packaging, not model behavior.
- **Subtitle parsing:** repeated text, overlapping cues, multiline cues, timestamps, invalid inputs, and refusal to overwrite existing output. Supports UTF-8 SRT and WebVTT only.
- **Frame extraction:** a synthetic red/blue video, requested seek times, output pixel checks, invalid times, missing dependencies, and overwrite protection. Requires FFmpeg/ffprobe; missing tools cause an explicit skip. Requested timestamps are not measured presentation timestamps.
- **Output validation:** coverage gaps, section identifiers, missing assets, learner-evidence references, stale annotations, section/index markers, manual-edit hash warnings, and invalid data. The validator does not modify the course files.

The initial publication was locally checked on macOS with Python 3.13.14 and FFmpeg/ffprobe 9.0.1: all 28 course-tool tests passed with no skips. All three packages also passed the locally available Codex skill-creator structural validator. The repository checker is self-contained apart from its PyYAML development dependency.

The GitHub Actions workflow runs package checks and the same tests on Ubuntu with Python 3.10 and 3.13. Consult the actual [workflow runs](https://github.com/XSY-28/learning-skills/actions) for their status; configuration alone is not a successful run.

## Not established by this release

These tests do not establish:

- Reliable automatic skill routing in a new client session.
- Model-generated explanation quality, factual correctness, or actual learner mastery.
- Whole-lecture or whole-course coverage and long-running continuation.
- YouTube/Bilibili acquisition, real audio transcription, or reconstruction of unclear audience questions.
- Accurate recognition of a real learner's history.
- Word/PDF/HTML export or Obsidian/Microsoft Word application rendering.
- Cross-client or cross-platform compatibility beyond checks actually reported by CI.

The two instruction-only skills have packaging checks in this release, not a newly executed teaching-effectiveness study. The course skill's [behavioral acceptance cases](../skills/course-to-notes/references/acceptance-cases.md) define useful future evaluation tasks; their presence does not mean they all passed.

## 中文说明

本次开源验证聚焦可复现的脚本与打包：本地 28 项测试全部通过、无跳过，三个技能通过结构检查。合成视频和合成档案只验证对应脚本行为，不能推广为真实课程端到端效果或真实学习成效。

仓库不包含课程原视频、字幕、截图或私人学习记录。自动触发、整讲/整课覆盖、真实 ASR、模糊问答还原、真实学习档案判断、Word/PDF/HTML 导出及 Obsidian/Microsoft Word 应用内显示，均不属于本次发布已验证能力。CI 的实际结果以工作流页面为准。
