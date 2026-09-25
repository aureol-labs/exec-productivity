---
name: aureol-review
user-invocable: false
description: The end-of-day review, every weekday: find what Claude could have done for the executive this week, from what they asked colleagues for, the documents and decks they built, the analyses they ran across tools, what they prepare every time, and show how, so they learn to do it alone: the prompt they could have typed, what to attach, the connections it needs, and the one thing to add first when something is missing (a connection, a ready-made plugin, a routine or a skill), each with its evidence. Writes asks and suggestions, never proposes a declined one twice, renders nothing of its own, and notifies only on a day it found something worth it, in plain words. Load from the end-of-day task, or when the exec asks what could be automated.
---

# The review

One question, at the end of every weekday: where, in the last seven days, could Claude have done the work,
and how would the exec have asked for it. Daily because cadence beats completeness: a
proposal the day after the pattern showed is worth more than a fuller one on Friday, and a run that finds
nothing new says one line and costs nothing. The answer is a short list of use cases, each with its how: the prompt, what to attach, the connections,
and anything to add first. The point is that the exec does it alone next time; how a finding was found stays
inside this file. It renders no page: the `aureol-context` skill's render mode republishes Super Context with the
proposals.

**Voice.** The run's message, the notification and every proposal the exec reads follow
`../aureol-context/references/voice.md`. Read it before you write.

## Rules that override anything you infer

1. **Something Claude could have done, and how.** A finding is a moment of the week where Claude could have
   done the work, with the way to have it done. Most often a prompt the exec could have typed that day:
   `kind: prompt`, every connection it needs already there. Else one thing to add first: a connection that
   exists in the catalog, or a ready-made plugin or skill (`connection`, `plugin`). When the same prompt comes
   back on a clock, a `routine`; on demand, a `skill`. Something that would stay a human chase is not a
   finding; it is not shown, not even as "nothing covers it". Nothing found means one line, never a table of
   what did not qualify.
2. **Value, then how.** `say` is the use case as value: "Your churn by cohort in one ask, instead of a
   request to Julien", never "an ask a connection would have answered". Then the how, on every finding, so the
   exec learns to do it: `prompt`, the words they could have typed, first person, 40 words at most; `attach`,
   what to give it (a file, a thread, a page), left out when nothing; `needs`, each connection it uses, with
   `connected` true or false. The table's columns: what you did, what Claude could have done, the prompt, what
   to attach, the connections. No minute counts: the value is the work Claude does, never a time saved.
3. **A prompt before anything to add, the shelf before the workshop.** When the connections are there, the
   finding is a prompt. When something is missing, search the Claude plugin catalog (the session's plugin search tool) for
   the system or the task before proposing anything custom; a plugin or a shipped skill that covers it is
   proposed as `kind: plugin`. Only then a routine (a pattern with a clock) or a skill (a pattern reached for
   on demand). A recurring ask that a connection would answer is a routine with the connection as its means.
4. **Evidence or nothing.** Every finding carries the two or three moments it comes from, dated, in the exec's
   words. Ranked by how much work it takes off the exec: how often, times how long.
5. **Declined is final.** Read `suggestions` with `status: declined` before proposing; never the same system,
   plugin, routine or skill twice.
6. **Three on the page, all new ones in the message.** The Super Context list shows the three strongest; the run's
   message shows every finding that qualified, and nothing that did not.

## The signals, all of them, the exec's side only

- **Asks to colleagues** for data, figures, a status, an extract, an analysis that lives in a system: sent
  mail, sent messages, the exec's own action items in meeting notes. The system named or inferred.
- **Work the exec does themselves again and again**: the same kind of mail drafted, the same document
  assembled, the same numbers compiled, the same reply written. Sent mail and documents authored.
- **Documents and decks the exec builds by hand**: a deck, a memo, a one-pager assembled from other
  documents, a section rewritten from last quarter's.
- **Analyses across documents and tools**: figures from a sheet checked against a system, a summary across
  several threads or files, two versions compared.
- **What the exec prepares every time**: a recurring meeting with the same preparation (the pipeline numbers
  before the Monday review, the pack before the board).
- **What the exec forwards or summarises for others**: a thread relayed, a digest written, a status sent
  upward or downward on a rhythm.
- **What the exec reads to decide**: documents opened before a recurring decision, dashboards checked.
- **What the inbox habit keeps ranking**: a class of message that comes back every week and always waits on
  the exec for the same reason.

Never what colleagues asked the exec; that is the inbox's job.

## Modes

One pass: a rolling 7 days, called by the weekday task at the end of the day, or in a session when the exec
asks what could be automated. It proposes only what is new since the last run (not in `suggestions` as
proposed, found or declined), so the same pattern never comes back day after day. The install does not run it.

## Steps

**Release steps.** Before anything else, read `../aureol-context/references/releases.md` and apply what it says for the `review` task.

0. Read `connections/current`, `asks`, `suggestions`, `people`, `entities`, `topics`, the last `runs` of this
   task. Probe mail, chat, meetings and documents with one real call each.
1. Read the window from the exec's side across the signals above. Record each ask in `asks` (deduplicated on
   the same what and to), and note the other patterns in the run.
2. For each pattern, write the prompt that would have done it, then what it needs: the connections, there or
   not (catalog check with `search_mcp_registry` for a missing one), a shipped plugin or skill (plugin catalog
   check), a clock (routine), a recipe reached for on demand (skill). Nothing can do it: the pattern is dropped
   from the findings and stays in the run's notes only.
   Without the catalog tools in a scheduled run, record `connector: unknown` or `plugin: unknown` and let the
   next `exec-productivity-help` session resolve it; do not show the pattern as a finding until it is resolved.
3. Write `suggestions` for what qualified: `kind` prompt, connection, plugin, routine or skill; the use case
   in one sentence as `say`; the evidence ids; `prompt`, `attach` and `needs` on every finding; `pattern`
   (cadence and output for a routine, the repeated ask for a skill); `briefing`, the prompt itself for a prompt,
   the habit's prompt drafted for a routine, the skill's outline for a skill; `path` for a connection or a
   plugin. Skip anything declined. Cap at three `proposed`, the rest `found`.
4. Load the `aureol-context` skill in render mode so Super Context shows the proposals. In a session the exec
   opened, also return the connections and plugins with their catalog ids, which shows the cards.
5. Write a `runs` document. The task prompt says how the run ends: one line, then a table with a row per
   qualified finding (what you did, what Claude could have done, the prompt, what to attach, the
   connections), then the cards for anything to add, then "Try a prompt now, or say which ones you want and I
   add them." Nothing qualified: one line, "Nothing new today." No table, no notification: silence is the right
   answer most days.
6. **The notification is the value, not the report.** Only on a day something qualified, and only for a finding
   worth the exec's attention: it recurs (two moments at least in the window) and it takes real work off them,
   not a nicety. One line under 200 characters, in the exec's language: what Claude would do for them, in their
   own words from the evidence, then the prompt's place or what to add, then the link. "Your churn by cohort
   was one prompt away, it is on your Super Context: <link>"; "Claude could prepare your Monday pipeline
   numbers itself. Connect HubSpot: <link>". Never a count, never how it was found, never the words use case,
   finding, suggestion or signal. Nothing clears the bar: no notification, even when something was recorded.
