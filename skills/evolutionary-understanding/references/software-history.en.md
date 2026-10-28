# Software history evidence

[中文](software-history.md)

Use only when the learning object is a software project and actual code or version history is needed. Find changes that explain present behavior rather than exhaustively listing commits or conducting a code review.

## Scope the investigation from a current task

Inspect the environment and changed files under the repository's instructions. Check `git status --short` before Git operations and preserve uncommitted work. Identify the version or working tree being read. Default to read-only investigation: do not switch branches, roll back, install dependencies, or execute unfamiliar historical code merely to inspect history.

Use one user-visible task to locate entry points, state changes, key modules, and external interactions. Read the current implementation and relevant documentation, then formulate questions to verify, such as why task state moved from memory to a database. Directory names do not prove implemented guarantees.

## Narrow from an overview to evidence

- Start with relevant release points and a bounded commit overview, then narrow by path, keyword, or time range. Adapt the search to evidence density rather than reading all Git history by default.
- Use `git log --oneline -- <path>` to find candidates. For a single renamed file, `git log --follow -- <file>` can help. Neither guarantees complete history.
- Inspect changes with `git show <commit> -- <path>` and, when needed, the full historical file with `git show <commit>:<path>`. Check the parent version or corresponding earlier implementation to establish old behavior; added lines alone are insufficient.
- For a known symbol, `git log -S '<literal>' -- <path>` or `git log -G '<regex>' -- <path>` can locate changes. Confirm the actual diff before identifying a transition. `blame` identifies the last commit touching a line, not the origin of a design.
- PRs, issues, design records, and tests can supply rationale, intended behavior, and failure scenarios. Test files show what they check; without running them, do not claim they passed. Offline checks do not establish real external-service behavior.

## Organize by semantic change

Prioritize changes to user behavior, interfaces or data models, state ownership, recovery, trust boundaries, core abstractions, and important tradeoffs. Directory moves, formatting, and generated code usually remain background; include them when they materially change use.

Group scattered commits into an evidenced design transition and separate distinct motives within bulk migrations. Follow relevant fixes, reversals, and branches after introduction so “once merged” does not become “still in use.” Release titles and commit messages are leads, not independent proof of behavior or benefits.

Squashed merges, shallow clones, imported repositories, file moves, and missing discussions can obscure history. Identify the gaps and their effects, then consult accessible primary records. If a gap remains, narrow the claim instead of supplying an invented motive.

## Separate behavior, rationale, and inference

Retain a locatable version or commit and path for each key transition. Link the relevant discussion or local material when a claim depends on it. Provide enough citation detail to inspect the claim without dumping full logs.

For example, adding `task_id` proves that a request gained an identifier. Its intended use for deduplication needs supporting evidence. Whether it prevents repeated external effects also depends on the receiver's protocol and behavior. A symbol, comment, or retrospective preference cannot alone establish a complete architecture or authorial intent.

Finally, follow the current execution path once more. Check that the discussed mechanisms still exist, how their responsibilities connect, and which failure windows remain. Distinguish historical facts, behavior inferred from current code, executed validation, and unverified claims.
