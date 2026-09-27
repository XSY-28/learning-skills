# Learning Skills

Three independent Codex skills for learning from courses, understanding difficult concepts, and writing lectures that readers can follow on their own.

[中文说明](README.zh-CN.md) · [MIT License](LICENSE) · [Validation](docs/validation.md)

These are agent instructions and small supporting tools, not a standalone app. Skill instructions are primarily in Chinese; each skill respects the requested output language. They do not require one another.

## Choose a skill

| Skill | Use it for | Example request |
| --- | --- | --- |
| [course-to-notes](skills/course-to-notes/SKILL.md) | Choosing a suitable video course or turning a specified lecture into illustrated notes with timestamps, teaching context, and evidence-based learning markers | “Turn this lecture into Chinese Markdown notes; preserve the derivations and meaningful questions.” |
| [explain-for-understanding](skills/explain-for-understanding/SKILL.md) | Building conceptual understanding through motivation, concrete examples, object roles, and connected reasoning | “I can follow the algebra, but why would we try this proof?” |
| [obsidian-lecture-writing](skills/obsidian-lecture-writing/SKILL.md) | Writing or substantially revising self-contained lecture chapters, with concept dependencies, chapter reviews, and reader checks | “Write an introductory chapter that teaches the objects before using them.” |

Quick formula lookup, translation, formatting fixes, and ordinary code debugging should stay focused on those tasks. Mentioning a subject or an Obsidian path alone should not activate a teaching workflow.

## Install in Codex

Ask Codex to use its skill installer:

```text
Use $skill-installer to install the following skills from XSY-28/learning-skills:
- skills/course-to-notes
- skills/explain-for-understanding
- skills/obsidian-lecture-writing
```

Select just one path if you only want one skill. If your Codex installation includes the bundled installer at the standard location, the equivalent command is:

```sh
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo XSY-28/learning-skills \
  --path skills/course-to-notes skills/explain-for-understanding skills/obsidian-lecture-writing
```

The installer refuses existing destination folders. Back up any locally customized version before deliberately replacing it. Restart Codex after installation. The skills allow implicit selection, but actual automatic routing depends on the host and has not been verified across clients. Explicit invocation is useful when you want to select a particular workflow.

Alternatively, download this repository and copy the desired folder from `skills/` into your configured skills directory. Preserve the whole folder, including `references/`, `agents/`, `scripts/` when present, and `LICENSE`.

## Try it

**Course notes**

```text
Use $course-to-notes to organize the first 10 minutes of the lecture I provide.
Write Chinese Markdown in ./course-notes. Keep the teaching sequence, important
repetition, derivations, timestamps, and useful images. Distinguish source
content from editorial additions and tell me what could not be verified.
```

If you have not chosen a course, ask for a few candidates based on your background and goals first. If no learning history is available, the skill continues with “unknown” markers instead of inferring mastery.

**Conceptual understanding**

```text
Use $explain-for-understanding to explain why regularization changes the
optimization objective. I know derivatives but am new to machine learning.
Use a small numerical example and explain what each quantity represents.
```

**Self-contained lecture writing**

```text
Use $obsidian-lecture-writing to write an introductory chapter on conditional
expectation. Assume basic probability only. Build the objects and motivation
before the formulas, and check whether a reader can solve a small variation
using only the chapter. Deliver it here; do not write to a vault yet.
```

Specify your actual vault and output path when you want files written. No skill assumes a private vault location or a fixed learner profile.

## Requirements and boundaries

- The two explanation/writing skills have no script dependencies. File access and Obsidian UI checks depend on tools available in your agent environment.
- Course helper scripts use Python 3.10+ and its standard library. Frame extraction also requires `ffmpeg` and `ffprobe` on `PATH`.
- Course discovery, media access, transcription, visual inspection, and Word/PDF rendering require corresponding tools in the host environment. This repository does not bundle an ASR model, downloader, or document converter.
- Use course materials with the appropriate permissions and preserve source attribution. The MIT license covers this repository's original instructions, code, and synthetic fixtures; it does not grant rights to third-party course media or generated derivatives.
- Structure checks do not establish factual correctness, complete lecture coverage, teaching effectiveness, or a learner's mastery.

## Development and verification

From the repository root:

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/check_package.py
python3 -m unittest discover -s tests/course-to-notes -v
```

PyYAML is used only for development validation. The 28 course tests cover subtitle parsing, synthetic video frame extraction, and output-contract checks. Frame tests explicitly skip when FFmpeg tools are missing. CI installs FFmpeg so these tests run there.

See [validation scope](docs/validation.md) for evidence and limitations. Behavioral acceptance cases are included in the course skill; they are review tasks, not claims that every scenario has passed.

Contributions should preserve task boundaries, learning-evidence distinctions, and manual edits. Describe a concrete failure or use case and run the relevant checks. Keep course media, personal learning records, credentials, and generated private notes out of contributions.
