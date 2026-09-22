---
name: aureol-review
user-invocable: false
description: The end-of-day review, every weekday, and the same look at install: find where the executive's assistant would take work off their hands this week, from what they asked colleagues for, what they did themselves again and again, what they prepare every time, what they forward or summarise, and propose only what can be added, a connection, a ready-made plugin, a routine or a skill, each as a use case with its evidence. Writes asks and suggestions, never proposes a declined one twice, renders nothing of its own. Load from the weekly task, from install, or when the exec asks what could be automated.
---

# The review

One question, at the end of every weekday: where, in the last seven days, would the assistant have done the
work, and what has to be added for it to do so tomorrow. Daily because cadence beats completeness: a
proposal the day after the pattern showed is worth more than a fuller one on Friday, and a run that finds
nothing new says one line and costs nothing. The answer is a short list of use cases, each with the thing to add. The
mechanics that find them stay inside this file; the exec reads use cases and value, never how they were
found. It renders no page: the `aureol-context` skill's render mode republishes Super Context with the
proposals.

## Rules that override anything you infer

1. **Only what can be added.** A finding is a use case plus the thing that makes it possible: a connection
   that exists in the catalog, a ready-made plugin or skill from the Claude catalog, a routine, or a custom
   skill. Something that would stay a human chase is not a finding; it is not shown, not even as "nothing
   covers it". Nothing found means one line, never a table of what did not qualify.
2. **A use case is written as value, not as mechanism.** "Your Qonto charges, read by your assistant when you
   ask, instead of asking someone with billing access", not "an ask a connection would have answered". The
   table's columns are: what you do today, how often, what Claude would do instead, what to add. No minute
   counts: the value is the work Claude does, never a time saved.
3. **The shelf before the workshop.** Search the Claude plugin catalog (the session's plugin search tool) for
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
- **What the exec prepares every time**: a recurring meeting with the same preparation (the pipeline numbers
  before the Monday review, the pack before the board).
- **What the exec forwards or summarises for others**: a thread relayed, a digest written, a status sent
  upward or downward on a rhythm.
- **What the exec reads to decide**: documents opened before a recurring decision, dashboards checked.
- **What the inbox habit keeps ranking**: a class of message that comes back every week and always waits on
  the exec for the same reason.

Never what colleagues asked the exec; that is the inbox's job.

## Modes

Install mode: the last 30 days, called by install, silent unless something qualified. Daily mode: a rolling 7
days, called by the weekday task at the end of the day; it proposes only what is new since the last run (not
in `suggestions` as proposed, found or declined), so the same pattern never comes back day after day.

## Steps

0. Read `connections/current`, `asks`, `suggestions`, `people`, `entities`, `topics`, the last `runs` of this
   task. Probe mail, chat, meetings and documents with one real call each.
1. Read the window from the exec's side across the signals above. Record each ask in `asks` (deduplicated on
   the same what and to), and note the other patterns in the run.
2. For each pattern, decide what would make the assistant do it: the system's connection (catalog check with
   `search_mcp_registry`), a shipped plugin or skill (plugin catalog check), a routine (a clock), a skill (no
   clock). No such thing exists: the pattern is dropped from the findings and stays in the run's notes only.
   Without the catalog tools in a scheduled run, record `connector: unknown` or `plugin: unknown` and let the
   next `help` session resolve it; do not show the pattern as a finding until it is resolved.
3. Write `suggestions` for what qualified: `kind` connection, plugin, routine or skill, the use case in one
   sentence as `say`, the evidence ids, `pattern` (cadence and output for a routine, the repeated ask for a
   skill), `briefing` for a routine or a skill (the habit's prompt drafted, or the skill's outline), `path` for
   a connection or a plugin. Skip anything declined. Cap at three `proposed`, the rest `found`.
4. Load the `aureol-context` skill in render mode so Super Context shows the proposals. In install mode also
   return the connections and plugins with their catalog ids to install, which shows the cards.
5. Write a `runs` document. The task prompt says how the run ends: one line, then a table with a row per
   qualified finding (what you do today, how often, what Claude would do instead, what to add), then
   the cards, then "Say which ones you want and I add them." Nothing qualified: one line, "Nothing this
   new today." No table, no notification: silence is the right answer most days.
