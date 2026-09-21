---
name: aureol-review
user-invocable: false
description: The Friday review, and the same scan at install: read the executive's own asks to colleagues (sent mail, sent messages, meetings), keep the ones a connection would have answered directly, check which systems have a connection, and propose them on the Super Context page with the asks as evidence; an ask that repeats becomes a skill candidate, an ask on a cadence becomes a routine candidate, and an off-the-shelf plugin is proposed first when one covers the ask. Writes asks and suggestions, never proposes a declined one twice, renders nothing of its own. Load from the weekly task, from install, or when the exec asks what could be automated.
---

# The review

The exec keeps asking colleagues for data, figures, a status, an extract, an analysis. Someone opens a system,
pulls it, sends it back, sometimes with their own analysis on top. With the right connection the exec could have
asked their assistant. This skill finds those asks and turns them into three lines on Super Context, with the
evidence. It renders no page: the `aureol-context` skill's render mode republishes Super Context.

## Rules that override anything you infer

1. **Evidence or nothing.** A suggestion carries the asks that justify it, in the exec's words, with who was
   asked and when. Three lines on the page at most, ranked by how often the ask came back.
2. **Only systems with a connection.** Check the catalog (`search_mcp_registry`) for every system named. No
   connection, no suggestion; the ask is still recorded with `connector.name: null` so a later catalog can
   find it. Without the catalog tools in a scheduled run, record `connector: unknown` and let the next
   interactive `help` session resolve it.
3. **Declined is final.** Read `suggestions` with `status: declined` before proposing; never propose the same
   system or the same skill again.
4. **The shelf before the workshop.** Before proposing a skill or a routine, search the Claude plugin catalog
   with the session's plugin search tool (the one the app's own setup uses) for the system or the task in the
   pattern: sales, data analysis, project tracking, documents, meetings. A plugin or a shipped skill that covers
   the ask is proposed as `kind: plugin`, with its name and the sentence that says where to add it, and the card
   in an interactive session. Only when nothing on the shelf covers it does the pattern become a custom skill
   or routine. In a scheduled run without the catalog tools, record `plugin: unknown` on the suggestion and let
   the next `help` session resolve it.
5. **A skill candidate is a pattern**, the same ask three times in the window to the same person or on the same
   system, reached for at no fixed time, and its line says the pattern in one sentence with "Draft the skill" as
   the gesture. **A routine candidate is a pattern with a clock**: the same ask or the same piece of work on a
   cadence (every Monday, before each board or pipeline meeting, at month end, the day after a release). Its line
   says the cadence and what the routine would produce, and its gesture is "Create the routine", seeded with the
   habit's prompt drafted in the plugin's shape: language, timezone, the connections to read, what to publish,
   send nothing. A recurring ask that a connection would answer is proposed as a routine, not only as a
   connection: the connection is the means, the routine is the habit.
6. **The exec's own asks only.** Sent mail, sent messages, the exec's own action items in meeting notes. Never
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
   write `kind: skill` with `name` and `pattern`; for each pattern with a clock (rule 4), write `kind: routine`
   with `name`, `pattern` (cadence and output) and `briefing`; for each pattern the shelf covers (rule 4), write
   `kind: plugin` with `name` and `path` instead. Skip anything declined. Cap at three proposed across the four
   kinds, routines and plugins first when they exist, the rest stay `found`.
4. Load the `aureol-context` skill in render mode so Super Context shows the list. In install mode also return the
   proposed systems and their connector ids to install, which shows the card.
5. Write a `runs` document. The task prompt says how the run ends: one line of counts, one table with a row
   per finding (what was asked, who and how often, what would answer it, what it would change), the topics
   reading "Not yet" (from `topics.last_from_you`), and the link on its own line. The table is the whole
   finding, proposed rows and the rest; the page carries only the three proposed with their gestures.
