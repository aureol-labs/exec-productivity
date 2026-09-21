---
name: review
description: The Friday review, and the same scan at install: read the executive's own asks to colleagues (sent mail, sent messages, meetings), keep the ones a connection would have answered directly, check which systems have a connection, and propose them on the Super Context page with the asks as evidence; an ask that repeats becomes a skill candidate. Writes asks and suggestions, never proposes a declined one twice, renders nothing of its own. Load from the weekly task, from install, or when the exec asks what could be automated.
---

# The review

The exec keeps asking colleagues for data, figures, a status, an extract, an analysis. Someone opens a system,
pulls it, sends it back, sometimes with their own analysis on top. With the right connection the exec could have
asked their assistant. This skill finds those asks and turns them into three lines on Super Context, with the
evidence. It renders no page: the `context` skill's render mode republishes Super Context.

## Rules that override anything you infer

1. **Evidence or nothing.** A suggestion carries the asks that justify it, in the exec's words, with who was
   asked and when. Three lines on the page at most, ranked by how often the ask came back.
2. **Only systems with a connection.** Check the catalog (`search_mcp_registry`) for every system named. No
   connection, no suggestion; the ask is still recorded with `connector.name: null` so a later catalog can
   find it. Without the catalog tools in a scheduled run, record `connector: unknown` and let the next
   interactive `help` session resolve it.
3. **Declined is final.** Read `suggestions` with `status: declined` before proposing; never propose the same
   system or the same skill again.
4. **A skill candidate is a pattern**, the same ask three times in the window to the same person or on the same
   system, and its line says the pattern in one sentence with "Draft the skill" as the gesture.
5. **The exec's own asks only.** Sent mail, sent messages, the exec's own action items in meeting notes. Never
   what colleagues asked the exec; that is the inbox's job.

## Modes

Install mode: the last 30 days, called by install, silent unless something is found. Weekly mode: the last 7
days, called by the Friday task.

## Steps

0. Read `connections/current`, `asks`, `suggestions`, `people`, `entities`, `topics`. Probe mail, chat and
   meetings with one real call each.
1. Read the exec's sent mail and sent messages in the window, and their action items in meeting notes when a
   recorder is connected.
2. Detect asks: a request to a named colleague for something that lives in a system (numbers, a list, a report,
   a status, an extract, an analysis of data). Not a scheduling request, not an opinion, not a decision.
   For each: `to` (a `people` ref when it resolves), `what` in the exec's words, `system` (named in the ask, or
   inferred from `entities` and documents, or the generic name the exec used), `source`. Write `asks`,
   deduplicated on the same what and to within the window.
3. Group by system. For each system with two or more asks in the window (one in install mode counts when the
   ask is recurring by its own wording, "as every month"), search the catalog; with a connection, write a
   `suggestions` document `kind: connection` with the ask ids as `evidence`. For each repeated ask (rule 4),
   write `kind: skill` with `name` and `pattern`. Skip anything declined. Cap at three proposed, the rest stay
   `found`.
4. Load the `context` skill in render mode so Super Context shows the list. In install mode also return the
   proposed systems and their connector ids to install, which shows the card.
5. Write a `runs` document. The task prompt says how the run ends: the counts, the topics reading "Not yet"
   (from `topics.last_from_you`), and the link on its own line.
