---
name: brief
description: Write today's Daily brief for the executive: the day strip from the calendar with double bookings designed for, the decisions to land (three, each with a precedent, a knock-on, a pattern or a history), the jobs to do before a wall on the strip, every reveal ending on its sources and an Ask Claude briefing. Reads the Super Context store first, then calendar, mail, chat and meetings. Load from the morning task, from install for the first brief, or when the exec asks for their day.
---

# Daily brief

One page, read in two minutes, expired by 18:00. The template is `references/daily-brief.html`, rendered from one
JSON document (shape in its head comment and `references/example.json`). Design rules are the plan's, and the
ones that bite are below.

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
7. **Ranking is against the priorities.** Left alone you rank by mail volume, which is always new business.
   Rank against `priorities` in their order, and take topic names and roles from the store so every page says
   the same words.

## 0. Read the store, then probe

`connections/current`, `connections/preferences`, `priorities`, `topics`, `people`, `entities`, kept
`decisions`, `context/summary`. Probe calendar, mail, chat and meetings with one real call each. A failed role
is a missing section and one line in `data.notices`.

## 1. Read the day

Calendar: today from 00:00 to 24:00 in the exec's timezone, and tomorrow for context (a prep item today can come
from tomorrow's meeting). Mail and chat since yesterday 18:00 (48 hours on the first run), from the exec's side.
Meetings of yesterday when a recorder is connected. Only today's events are drawn.

## 2. Build

- **Metrics**: only when `preferences.metrics` names a source that answered; otherwise the block is absent.
  Never fill it with something adjacent.
- **The strip**: 08:00 to 18:00 by default, widened to the first and last event of the day. Every event is a
  block with `left` and `width` in percent of the strip. Filled means a decision is waiting in that meeting.
  Overlapping events are one block with stacked lanes and one clash brief whose columns each end on what it costs
  to move that one. Free stretches of an hour or more are named.
- **Meeting briefs**: WHO (from `people.role`), BEFORE, TO LAND, IN MIND; sources; briefing.
- **Decisions to land**: the cap, ranked against the priorities; type; reveal that opens on the answer; a
  PRECEDENT links to the decision it cites on Super Context, carrying the decision's words as its link text.
- **Jobs to do**: the cap; the wall on the strip; type. A job whose reveal would only summarise the thing it asks
  the exec to read has no Ask Claude.
- **Footer**: what the assistant did this morning, in numerals ("29 mails read, 0 written").
- **h1**: numerals only. "6 meetings, 1 clash, 3 decisions, 3 jobs." `sub`: the one thing the page cannot show.

## 3. Check, publish, record

Run `tools/check-page.py brief` on the JSON when a shell exists, else apply its list by hand. Fill
`{{DATA_JSON}}`, read the page at `connections/current.pages.brief` then publish to its `url`; no link yet,
publish new and write the link. Write a `runs` document. The task prompt says how the run ends: the link on its
own line, and the counts.
