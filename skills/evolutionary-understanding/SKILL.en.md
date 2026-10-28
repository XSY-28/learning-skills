---
name: evolutionary-understanding
description: "Use when the user invokes ‘How an Aircraft Carrier Is Built’ (航母是怎样建成的), wants evolutionary understanding (演化式理解) of a project, technology, theory, institution, or field, asks how it developed from a simpler starting point, or wants to learn a system through major Git changes. Do not automatically activate for ordinary conceptual questions, fact lookups, timelines or changelogs alone, code review, debugging, translation, or skill authoring. For mixed requests, apply only to the evolutionary-learning portion."
---

# How an Aircraft Carrier Is Built

[中文](SKILL.md)

Start from basic objects, the original problem, and the constraints of the time. Reconstruct the changes that produced the present structure so learners can explain why mechanisms exist, what they cost, and what might need to change under different conditions. Evidence constrains historical claims; conceptual dependencies determine the teaching order.

## Establish the scope

- Infer the object, learning goal, prior knowledge, available material, and length from the current request. Proceed when there is enough information; clarify only ambiguities that materially change the result. Default to Chinese unless the user requests another language, and deliver in chat. Do not automatically create learning records or modify the project.
- Introduce the target through a concrete task or problem, then provide a minimal map of its present form. For a large project, select a key execution path. For a field, identify its main problems and branches; one project's trajectory is not the history of the whole field.
- Choose a simple starting point relevant to the goal, without tracing every origin. The easiest teaching starting point need not be the first historical version.
- This method organizes explanations of how the object took its present form. Preserve existing teaching or coaching agreements instead of adding another questionnaire, mode, summary, or quiz. Explicit invocation still respects local scope, length limits, and requests for no exercises.

## Select evidence and an explanatory route

Choose from the problem and evidence, combining routes when useful. Do not require the user to select a mode first.

| Route | Appropriate situation | Evidence boundary |
| --- | --- | --- |
| Historical reconstruction | Versions, discussions, original papers, or archives are available, and actual changes matter. | Treat only supported events and motives as historical facts. Temporal order alone does not prove causation. |
| Teaching reconstruction | History is incomplete, or a shorter conceptual path would help. | Explicitly label the account as a teaching reconstruction, not the actual history of invention. Reorder concepts without inventing dates, people, commits, or quotations. |
| Reasoning backward from the present | A known mechanism needs an explanation. | Consider removing it or changing the conditions that make it useful, then check the history. A plausible function does not establish its actual origin. |

When the user explicitly requests real history and evidence is incomplete, identify the missing segment, what was inspected, and how the gap limits the conclusion. Continue with supported portions. Label any teaching substitute separately; it does not complete the historical investigation.

Use primary materials proportionate to the claim: code and versions, contemporaneous discussions and design records, papers, experiments, or archives. Present behavior, performance, and recent conclusions require matching versions or evidence; period labels and recollections do not replace verification. For software projects, read [Software history evidence](references/software-history.en.md). Other domains need not load it.

## Reconstruct meaningful transitions

Select transitions by their explanatory value: changes to the problem, constraints, assumptions, core structure, applicability, or important tradeoffs. Group small commits into one decision when appropriate, and separate distinct decisions within a large change. Preserve branches, failures, reversals, and continuing alternatives that matter. Do not assume that most changes are minor for every object.

Stage and section titles name the concrete change directly, using concise declarative phrases such as “Session persistence” or “Separation of tool interfaces and execution.” Avoid questions, rhetorical prompts, instructional wording, and narrative preambles such as “First, go back to…” or “How can we…”. Add dates when useful.

For each selected transition, develop this reasoning chain naturally rather than filling out a fixed table:

> The problem at the time → the conditions under which the old solution became inadequate, or the reason the goal changed → feasible alternatives then → the actual change and its rationale → gains and costs → consequences still visible today.

- Demonstrate a concrete limitation of the old solution before introducing the new mechanism. Develop the same example progressively rather than introducing several unexplained abstractions at once.
- Compare materially different options at important forks. If only one option is documented, label other possibilities as analytical counterfactuals, not alternatives known to have been discussed. Feasibility depends on the knowledge, resources, and technology available at the time.
- Distinguish what was reasonable then, what is necessary now, and what would be universally optimal. Compatibility costs, institutional interests, accidents, and mistakes can shape outcomes; attribute them only with evidence. Do not turn every change into inevitable progress or an optimal solution.
- Distinguish direct source support, inference from evidence, and teaching assumptions at important points. Participants' accounts establish their reported reasons; effects require separate evidence. A claimed performance improvement is not a measured improvement. Preserve material source conflicts rather than smoothing them into a coherent story.

A teaching reconstruction: a sequential task loses progress after restart, so task records are persisted; several workers compete, so claiming rules are added; an external action succeeds before its completion record is saved, so recovery can still repeat the action. Each layer addresses a different problem. Recovery does not imply exactly-once external effects. This example explains mechanisms, not any actual project's history.

## Preserve domain-specific standards

Engineering and institutional accounts can discuss design decisions, but distinguish participants' goals: a benefit for one group does not establish overall improvement. In theories and scientific fields, trace problems, assumptions, explanatory scope, and evidence, retaining parallel approaches and conditions of applicability. Historical narrative cannot replace proof or experiment. Explain natural evolution and other non-intentional processes through mechanisms, conditions, and evidence, without attributing purposeful design decisions to them.

When using an analogy, explain its correspondence and limits. If the object has no useful evolutionary path, or the immediate obstacle is a definition, derivation, or operation, address that gap directly instead of inventing developmental stages.

## Reconnect to the present and assess understanding

- Map the selected changes back to current structure or conceptual relationships. Follow one real task or phenomenon to show how the parts work together. Examine interactions: individually coherent changes can create new complexity in combination.
- Identify constraints that remain, parts that may survive only for compatibility, current disputes, and unknowns. State conclusions only where supported, and what evidence would change important judgments. For a quick introduction, prioritize the explanatory thread and expand side branches only as needed instead of exhausting the history.
- When appropriate under the learning agreement, offer one short task involving removal of a mechanism, a changed constraint, comparison of branches, or transfer. Leave room for the user's answer rather than answering it in the same turn. Recognize only the ability the response demonstrates; no response means no evidence of mastery. Do not add exercises to a pure delivery request or after the user declines them.
- Before delivery, check that the account explains changes rather than merely listing events; separates history from reconstruction; does not equate later with better; connects present structure to its limits; and provides locatable key sources. Use a compact transition table or branching diagram when helpful, without a fixed section count.

Finishing an explanation does not establish learning effectiveness or faster learning. Those claims require corresponding learner performance and comparative evidence, not fluent prose, complete materials, or passing agent trials.
