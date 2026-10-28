# Use Learning Skills in DeepSeek Harness

[中文](dsh.zh-CN.md)

The `dsh-learning-skills` plugin supplies all four skills to DSH's skill registry. Each keeps its own name, instructions, references, and helper scripts. It uses the same source folders as the Codex installation.

The skill displayed as **航母是怎样建成的** keeps `/evolutionary-understanding` as its invocation name.

## Install and invoke

With DSH installed, add the plugin to the profile you actually use (replace `web` for another profile):

```sh
dsh plugin --profile web add github:XSY-28/learning-skills
```

Start or restart that profile. It must include the `dsh-skill` registry and `dsh-tool-skill` consumer; Standard mode includes skill support. This bundle adds a provider, and does not replace your agent preset or permission settings.

In DSH, use the slash form rather than Codex's `$name` syntax:

```text
/evolutionary-understanding Explain DSH through its major Git design changes, distinguishing recorded history from inference.

/explain-for-understanding Explain regularization. I know derivatives but do not understand why we add a penalty to the loss.

/course-to-notes Turn the first 10 minutes of the lecture and matching subtitles I provide into Chinese Markdown notes in ./course-notes.

/obsidian-lecture-writing Write an introductory chapter on conditional expectation for someone who knows basic probability. Deliver it here first.
```

The model can also load a matching skill through DSH's `skill` tool. A successful load includes the skill directory so it can resolve relative references and scripts. `agents/openai.yaml` remains Codex metadata; DSH discovery uses the plugin's catalog generated from the `SKILL.md` headers.

## Requirements and limitations

- Tested SDK: DSH `0.1.7-rc.2`, Cordis `4.0.4`; Node.js `^22.19.0 || >=24.0.0`. The peer range explicitly includes the tested prerelease series. Later prerelease series need a new compatibility check.
- The explanation, lecture-writing, and evolutionary-understanding skills have no helper dependencies. Course helpers require Python 3.10+; frame extraction needs `ffmpeg` and `ffprobe` on `PATH`.
- Video acquisition, transcription, image understanding, document export, and Obsidian UI checks depend on tools and models in your DSH environment. The plugin does not supply them or grant extra permissions.
- Project/user filesystem skills with the same names take precedence over these bundled defaults in the same registry scope. Avoid retaining an old same-name copy when you intend to use the bundled version.
- The package ships JavaScript and its resources directly, without an install-time build. GitHub installation does not require approving a `prepare` script for this package.

See [validation scope](validation.md) for executed checks. Registry/loading tests do not establish model routing, teaching quality, or a complete video-processing session.

## Update or remove

Use DSH's plugin management for the same profile. Update the GitHub dependency with `dsh plugin --profile web update dsh-learning-skills`, restart the profile, and verify the loaded skill before relying on an update. Remove the package with:

```sh
dsh plugin --profile web remove dsh-learning-skills
```

Codex's copied skill folders have a separate update lifecycle. Updating this DSH plugin does not replace those copies.
