# Learning Skills

[中文](README.zh-CN.md)

Three Codex skills for turning lectures into notes, working through confusing concepts, and writing chapters that can be read without the original chat.

Each skill is a folder of agent instructions. `course-to-notes` also includes scripts for subtitles, video frames, and output checks. You can install any of them on its own. The instructions are mainly in Chinese; you choose the output language.

## Choose a skill

| What you want to do | Skill |
| --- | --- |
| Find a course that fits your background, or turn a lecture into notes with timestamps and relevant images | [course-to-notes](skills/course-to-notes/SKILL.md) |
| Understand why a definition, method, or step in a proof makes sense | [explain-for-understanding](skills/explain-for-understanding/SKILL.md) |
| Write or substantially revise a lecture chapter, including the background needed to follow it | [obsidian-lecture-writing](skills/obsidian-lecture-writing/SKILL.md) |

## Install

In Codex, send:

```text
Use $skill-installer to install these paths from XSY-28/learning-skills:
- skills/course-to-notes
- skills/explain-for-understanding
- skills/obsidian-lecture-writing
```

Keep only the paths you want. After installation, send a new message using one of the prompts below. If Codex cannot find the installed skill, restart it.

The installer refuses to overwrite an existing skill folder. Back up any local changes before replacing an older copy.

<details>
<summary>Install from the terminal or copy the folders manually</summary>

If your Codex installation has the bundled installer at the standard location:

```sh
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo XSY-28/learning-skills \
  --path skills/course-to-notes skills/explain-for-understanding skills/obsidian-lecture-writing
```

Or download this repository and copy the skill folders you want from `skills/` into your configured skills directory. Copy each whole folder, including its references, scripts, metadata, and license.

</details>

## Use

### Work through a concept

```text
Use $explain-for-understanding to explain regularization.
I can take derivatives, but I don't understand why we add a penalty to the loss.
Start with a small example I can calculate by hand.
```

The skill asks Codex to explain what each quantity represents, connect the example to the derivation, and state when the conclusion applies.

### Turn a lecture into notes

```text
Use $course-to-notes to turn the first 10 minutes of the lecture I provide
into Chinese Markdown notes in ./course-notes.
```

The workflow preserves the lecture's teaching sequence, derivations, questions, and meaningful repetition. Notes include source timestamps and relevant images where the material is available; missing or unclear material is reported. You can supply learning records to get chapter-level reading suggestions; without records, prior learning stays unconfirmed.

If you have not chosen a course, give your background and goal and ask for course recommendations first.

### Write a chapter

```text
Use $obsidian-lecture-writing to write an introductory chapter on conditional
expectation for someone who knows basic probability. Deliver it in this chat.
```

The skill asks Codex to introduce concepts before relying on them, explain the reasons behind key steps, and review the chapter from a reader's position. To save it in Obsidian, specify your vault and destination file.

These workflows are for learning and teaching. A formula lookup, translation, or formatting fix can stay brief. Automatic skill selection depends on the client; use `$skill-name` when you want to choose explicitly.

## Requirements

The explanation and chapter-writing skills have no script dependencies. The course helpers use Python 3.10+ and the standard library; extracting video frames also needs `ffmpeg` and `ffprobe` on `PATH`.

Video access, audio transcription, and Word/PDF export depend on tools available to Codex. This repository does not include a video downloader, transcription model, or document converter.

## Checks and contributions

See [validation.md](docs/validation.md) for development commands, test coverage, and what has not been verified. Package and helper-script checks do not establish that generated notes are correct or that a learner has mastered the material.

For a bug report or contribution, include a concrete request, what happened, and what you expected. Keep private notes, learning records, credentials, and third-party course media out of commits.

[MIT licensed](LICENSE). The license covers this repository's original instructions, code, and test fixtures; course materials retain their own terms.
