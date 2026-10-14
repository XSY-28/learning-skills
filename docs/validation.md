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

## DSH plugin checks

The DSH package was locally checked on macOS with Node.js 24.19.0, DSH skill registry 0.1.7-rc.2, and Cordis 4.0.4. All four Node tests passed:

- Discover, load, and render all three skills through the real DSH registry, including their referenced files.
- Remove skills on plugin disposal and restore them on remount.
- Preserve a same-name runtime customization and restore the bundled default when that customization is removed.
- Pack and extract the plugin into a new directory, load it without a dependency symlink, and run the packaged course helper's CLI help.

The actual DSH CLI also installed the tarball in an isolated temporary profile. Its composed configuration contained the plugin row, and the installed provider loaded all three skills through the real registry. No user profile or model request was used. The runtime adapter imports only Node built-ins; its optional DSH peer documents the tested host API without requiring a second host SDK inside the installed package.

To reproduce the repository checks:

```sh
python3 scripts/build_dsh_catalog.py --check
npm ci --ignore-scripts
npm test
```

The catalog is generated from the shared skill headers; after changing a header, run `python3 scripts/build_dsh_catalog.py` and commit the updated catalog. PyYAML is a development dependency, not a plugin runtime dependency. The package explicitly includes required resource types and excludes Python caches.

These checks establish installation and instruction/resource loading, not a Web UI conversation, reliable model selection, teaching quality, or whole-course processing. The DSH CI job executes the registry and packed-artifact tests; its actual result must be read from the workflow run.

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

## Transcript-first workflow checks (2026-10-14)

The course instructions now prefer reading the complete available transcript, mapping semantic units to source times, discovering visual changes, and seeking to material that needs checking. Necessary playback may use a supported faster speed, with slower review for unclear or dense material. Subtitle gaps, silent board work, transient conditions, corrections, questions, and meaningful repetitions remain part of the coverage review. Playback speed does not change source timestamps. Existing scripts and the v1 output schema are unchanged.

- Local macOS checks: all 28 course-tool tests and all 4 DSH registry/relocated-package tests passed, with no skips. Package, skill-creator structure, and generated-catalog checks passed. The initial DSH test caught a reference link with a section fragment being treated as a file path; the instructions now use whole-file links, and the actual loading tests passed after that correction.
- A separate parser probe preserved all 2,000 synthetic subtitle cues, repeated text, and source times. A recheck of 638 previously cached real course cues reproduced the earlier parsed text and times. These exercise subtitle parsing, not model reading, live acquisition, or whole-lecture coverage; parser throughput cannot be reported as end-to-end speedup.
- New behavioral cases B33–B38 cover transcript-first processing, truncated long reads, silent/transient board work, supported playback speed, source-time preservation, and unavailable media. Adding cases is not evidence that all of them passed.
- An independent local execution processed a wholly synthetic video over the requested 0–24 seconds, read all 11 cues, inspected eight visual stages, and checked adjacent frames in a subtitle gap. The parent review confirmed retention of the transient positive-integer condition, the incorrect denominator and its correction, three separate emphases, the example, and the question/answer. The actual video was 24.2 seconds with no audio; the last 0.2 seconds were outside the requested range. Structure validation returned 0 errors and 7 disclosed warnings. A ZIP unpacked in a new directory had all 15 local reading links/anchors intact; actual Markdown-reader display was not tested. The artifact remains drafted with its evidence limits.
- Three additional offline decisions covered visible captions without audio access, 2x playback with source time 120 seconds, and a truncated subtitle read. They retained incomplete-content disclosure, source timestamps, and the need to read the missing middle, respectively. These are scenario decisions, not live playback or long-input model tests.

Real player speed controls, audio transcription, full-length course processing, automatic routing, and a measured end-to-end acceleration remain unverified in this update. Video access does not establish audio access; a filled coverage timeline does not establish that all teaching content was retained. CI results must be read for the published commit rather than inferred from local checks.

本轮优化优先完整字幕与按需定位，必要时允许已核实的倍速，不减少教学范围。本地脚本/加载测试、字幕解析和独立合成素材整理已执行，正文保留字幕外短暂条件、试错/纠正、三次强调及问答；真实播放器倍速、完整真实讲次、ASR 和整项处理提速尚未验证，不作“零遗漏”或固定提速倍数保证。
