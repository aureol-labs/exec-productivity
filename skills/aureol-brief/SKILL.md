---
name: aureol-brief
user-invocable: false
description: Write today's Daily brief for the executive: the day strip from the calendar with double bookings designed for, the calls to make (three, each asked with its options, the one fact it is on the page for under it: a precedent, a knock-on, a pattern or a history), the jobs to do before a wall on the strip, no advice anywhere, every line opening on its sources and an Ask Claude briefing. Reads the Super Context store first, then calendar, mail, chat and meetings. Load from the morning task, from install for the first brief, or when the exec asks for their day.
---

# Daily brief

One page, read in two minutes, expired by 18:00. The template is `references/daily-brief.html`, rendered from one
JSON document (shape in its head comment and `references/example.json`). Design rules are the plan's, and the
ones that bite are below.

**Voice.** Every word the exec reads, on the page, in a notification or a briefing, follows
`../aureol-context/references/voice.md`. Read it before you write.

## Rules that override anything you infer

1. **The line is the call, never the answer.** A decision line names the topic (the same word the day strip uses
   for that block) and asks the call with its options: "Halden Mutual: grant 19% off, or hold the price?". Under
   it, one line: the fact the call is on the page for (rule 3). No recommendation on the page or in a briefing:
   the call is the exec's, and an answer is the part most likely to be wrong. Jobs stay imperative, with their
   fact under them. One topic, one line: a call and the job it implies are the call, and check-page refuses two
   lines on one ref.
2. **A decision has a counterpart and a room. A job you produce alone.** Nothing that starts with "Decide" goes
   in the jobs list.
3. **No type, no line.** Every decision and job is on the page because it has a PRECEDENT, a KNOCK-ON, a PATTERN
   or a HISTORY, and the line under it states that fact in 12 words at most ("Bergen asked the same in July: you
   held, it closed at 79k."). `type` names it in the data; the page never prints it. A line you cannot type is
   holding a slot something else has earned. Inventing a type is the one thing you may not do.
4. **The right column is a time on the strip, never a number you worked out.** On a decision, the bare time it
   lands on the exec. On a job, "Before HH:MM" and that time is a block on today's strip; no block, the date it
   was asked; neither, empty. Brick only once the time has gone by, with the word: "Was due 10:00". Never "6 days
   late".
5. **Caps.** `preferences.caps`, three and three by default. The day is whatever the calendar says.
6. **Three sources per line.** Your own summary in the briefing, never a message body. A briefing on a call asks
   Claude for the case on each side, never for an answer. Every briefing that drafts something ends "do not
   send".
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
   unless it carries one fact the page cannot show, never a line already on it. A line and its fact are 12 words
   each at most: check-page warns past that and refuses past 16 and 20, and a refused page is shortened and checked
   again, never cut off.

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
- **Meeting cards**: the title with who (from `people.role`); TO LAND, the call this meeting settles, as a link
  to its decision line (`to_land.go`, its text the call); TO KNOW (`in_mind.text`), one fact, 12 words at most. No
  WHO or BEFORE cells. A clash: each column ends on what moving that meeting costs; TO LAND says which call, and by
  when.
- **Decisions**: the cap, ranked against the priorities; `say` the call with its options; `argument` one entry,
  the fact; `type`; sources; briefing. No `lede`, `plain` or `go`: the page shows none of them.
- **Jobs**: the cap; the wall on the strip; `argument` one entry, the fact; type. A job whose briefing would only
  summarise the thing it asks the exec to read has no Ask Claude.
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
