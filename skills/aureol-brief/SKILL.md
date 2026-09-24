---
name: aureol-brief
user-invocable: false
description: Write today's Daily brief for the executive: the day strip from the calendar with double bookings designed for, the decisions to land (three, each with a precedent, a knock-on, a pattern or a history), the jobs to do before a wall on the strip, every reveal ending on its sources and an Ask Claude briefing. Reads the Super Context store first, then calendar, mail, chat and meetings. Load from the morning task, from install for the first brief, or when the exec asks for their day.
---

# Daily brief

One page, read in two minutes, expired by 18:00. The template is `references/daily-brief.html`, rendered from one
JSON document (shape in its head comment and `references/example.json`). Design rules are the plan's, and the
ones that bite are below.

**Voice.** Every word the exec reads, on the page, in a notification or a briefing, follows
`../aureol-context/references/voice.md`. Read it before you write.

## Rules that override anything you infer

1. **Clear first. The line is the decision, the reveal is the answer.** A decision line names the topic (the same
   word the day strip uses for that block) and what is being decided, in full, and does not decide. The reveal
   opens with your answer in its first words, then argues. Jobs stay imperative.
2. **A decision has a counterpart and a room. A job you produce alone.** Nothing that starts with "Decide" goes
   in the jobs list.
3. **No type, no line.** Every decision and job is on the page because it has a PRECEDENT, a KNOCK-ON, a PATTERN
   or a HISTORY, and the reveal says which. A line you cannot type is holding a slot something else has earned.
   Inventing a type is the one thing you may not do.
4. **The right column is a time on the strip, never a number you worked out.** On a decision, the bare time it
   lands on the exec. On a job, "Before HH:MM" and that time is a block on today's strip; no block, the date it
   was asked; neither, empty. Brick only once the time has gone by, with the word: "Was due 10:00". Never "6 days
   late".
5. **Caps.** `preferences.caps`, three and three by default. The day is whatever the calendar says.
6. **Three sources per reveal.** Your own summary in the briefing, never a message body, and every briefing
   that drafts something ends "do not send".
7. **A dropped line stays dropped.** Read `dismissals` from the brief page's own store
   (`connections/current.pages.brief`) before selecting. A job or decision dropped as done or not important is
   not proposed again on this run or any later one, because every run reads the whole collection. That only
   holds if the ref is the same across runs: give every decision and job the id of its source thread or
   calendar event as `ref`, and only when there is none `brief:<slug of the ask>`. A `done` also becomes a
   `so_far` fact on the topic it served, so the morning pass knows it happened rather than merely hiding it.
   Prune `done` dismissals older than 30 days; keep `not_important` ones.
8. **Ranking is against the priorities.** Left alone you rank by mail volume, which is always new business.
   Rank against `priorities` in their order, and take topic names and roles from the store so every page says
   the same words.
9. **Nothing about the page.** No line explains the page, how to read it, or what the assistant does not do
   ("sends nothing"). A cell or field with nothing to say is left out, never filled with "nothing to prepare"
   or "nothing to decide": a workout on the calendar is a block with its head line and nothing else. No `sub`
   unless it carries one fact the page cannot show, never a line already on it.

## 0. Read the store, then probe

`connections/current`, `connections/preferences`, `priorities`, `topics`, `people`, `entities`, kept
`decisions`, `context/summary`. Probe calendar, mail, chat and meetings with one real call each. A failed role
is a missing section and one line in `data.notices`, saying what could not be read, never how it was checked.

## 1. Read the day

Calendar: today from 00:00 to 24:00 in the exec's timezone, and tomorrow for context (a prep item today can come
from tomorrow's meeting). Mail and chat since yesterday 18:00 (48 hours on the first run), from the exec's side, the main inbox only
(`preferences.mail_scope`).
Meetings of yesterday when a recorder is connected; names in transcripts are resolved against the store's
people and entities (their `aka` carry the notetaker's mis-hearings), never written as heard. Only today's
events are drawn.

## 2. Build

- **Frame**: `lang` from `preferences.language`; `date_label` and `time_label` in that language with the real
  time of this run.
- **Metrics**: only when `preferences.metrics` names a source that answered; otherwise the block is absent.
  Never fill it with something adjacent.
- **The strip**: 08:00 to 18:00 by default, widened to the first and last event of the day. Every event is a
  block with `left` and `width` in percent of the strip. Filled means a decision is waiting in that meeting.
  Overlapping events are one block with stacked lanes and one clash brief whose columns each end on what it costs
  to move that one. Free stretches of an hour or more are named.
- **Meeting briefs**: WHO (from `people.role`), BEFORE, TO LAND, IN MIND, each only when it has something to
  say (rule 9); sources; briefing.
- **Decisions to land**: the cap, ranked against the priorities; type; reveal that opens on the answer; a
  PRECEDENT links to the decision it cites on Super Context, carrying the decision's words as its link text.
- **Jobs to do**: the cap; the wall on the strip; type. A job whose reveal would only summarise the thing it asks
  the exec to read has no Ask Claude.
- **Footer**: what the assistant read this morning, in numerals ("Read at 06:52: 61 mails, 41 messages, 6
  invites").
- **h1**: numerals only. "6 meetings, 1 clash, 3 decisions, 3 jobs." `sub`: absent, unless one fact the page
  cannot show.

## 3. Check, publish, record

Run `python3 tools/fill-page.py --kind brief skills/aureol-brief/references/daily-brief.html DATA.json OUT.html
--links context=<link> inbox=<link>` from the plugin's root folder (the one holding `skills/` and `tools/`)
when a shell exists (it checks the data, then fills the template with every `<` escaped); without a
shell, apply check-page's list by hand and replace the single `{{DATA_JSON}}` yourself. Read the page at `connections/current.pages.brief` then publish to its `url` with
`capabilities: {db: {}}`; no link yet, publish new the same way and write the link. Write a `runs` document. The task prompt says how the run ends: the link on its
own line, and the counts.
