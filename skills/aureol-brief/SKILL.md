---
name: aureol-brief
user-invocable: false
description: Write today's Daily brief for the executive: the day strip from the calendar with double bookings designed for, the calls to make (three, each asked with its options, the one fact it is on the page for under it: a precedent, a knock-on, a pattern or a history), the jobs to do before a wall on the strip, no advice anywhere, every line opening on its sources and a briefing for Claude that hands over what the brief found as a starting point. Reads the Super Context store first, then calendar, mail, chat and meetings. Load from the morning task, from install for the first brief, or when the exec asks for their day.
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
6. **Three sources per line.** Your own summary in the briefing, never a message body. What the brief found is
   the starting point, never the frame (voice). A meeting's briefing (Prepare with Claude): the meeting, who and
   their role, what the exec knows so far in two or three facts, then an open ask: the topics likely to come up,
   the decisions to make, what each person wants from the exec, the context to have in mind, anything the brief
   did not see, from the recent exchanges, the documents and the past meetings looked at with fresh eyes; it ends
   asking where the exec wants to go deeper, and never narrows to the one call the page found. A call's briefing
   (Decide with Claude) asks for the case on each side and anything else that bears on it, options the page did
   not list included, never for an answer. A job's (Think it through with Claude) asks for the work and for anything the
   brief missed. Every briefing that drafts something ends "do not send".
7. **A dropped line stays dropped, a settled call stays settled.** Read `dismissals` and `decided` from the brief
   page's own store (`connections/current.pages.brief`) before selecting. A call the exec settled on the page is
   never proposed again: Super Context logs it. A job or decision dropped as done or not important is
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
   unless it carries one fact the page cannot show, 20 words at most, never a line already on it. A line and its fact are 12 words
   each at most: check-page warns past that and refuses past 16 and 20, and a refused page is shortened and checked
   again, never cut off.

## 0. Read the store, then probe

`connections/current`, `connections/preferences`, `priorities`, `topics`, `people`, `entities`, kept
`decisions`, `context/summary`. Probe calendar, mail, chat and meetings with one real call each. A failed role
is a missing section and one line in `data.notices`, saying what could not be read, never how it was checked:
two at most, twelve words each. A tool that was never connected is not a notice.

## 1. Read the day

Calendar: today from 00:00 to 24:00 in the exec's timezone, and tomorrow for context (a prep item today can come
from tomorrow's meeting), on every calendar `connections/current.roles.calendar.calendars` lists, merged as the store
says. Mail and chat since yesterday 18:00 (48 hours on the first run), from the exec's side, the main inbox only
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
  the fact; `type`; sources; briefing. No `lede`, `plain` or `go`: the page shows none of them. For the live page
  (section 3), also `context`: what the brief knows about the call in 70 words at most, your own facts (who holds
  which option, the figures, the rule, the deadline), never a quoted message; `to`: who the message that acts it
  goes to, by first name ("Claire et Hugo"); and `live`, where it sits (section 3).
- **Jobs**: the cap; the wall on the strip; `argument` one entry, the fact; type. A job whose briefing would only
  summarise the thing it asks the exec to read has no Claude button.
- **Footer**: what the assistant read this morning, in numerals ("Read at 06:52: 61 mails, 41 messages, 6
  invites"). Its second span, only when a newer version of the assistant is published, in the exec's language:
  "A new version of your assistant is ready: type /exec-productivity:exec-productivity-update". Where the session
  can fetch a web page, compare the `version` in
  `https://raw.githubusercontent.com/aureol-labs/exec-productivity/main/.claude-plugin/plugin.json` with the
  newest heading of `../aureol-context/references/releases.md`, and write both to `connections/current.plugin`.
  Without web fetch, nothing: never a notice, never a guess.
- **h1**: numerals only. "6 meetings, 1 clash, 3 decisions, 3 jobs." `sub`: absent, unless one fact the page
  cannot show.

## 3. Check, publish, record

**What the live page needs**, written into the same document. Opened in Claude, the page keeps the day current
and works the lines where they stand: it reads today's calendar again (a meeting added, moved or cancelled since
the run redraws the strip; what has gone by dims; a call or a wall whose time passed says so), greys a line the
exec answered since the run, opens a call on its options as the sources state them, records the one the exec
settles and drafts the message that acts it, and drafts a job that is a message.

- `generated`: this run's time, ISO with the hour and the offset.
- `live.me`: `{name, role}`, the exec's first name and their role in a line ("CEO de Halden, 180 personnes"), from
  `connections/preferences`: who Claude writes for.
- `live.mail`, `live.calendar`, `live.chat`, from `connections/current.roles`: `Aureol Connect` is `{server:
  "Aureol Connect", api: "aureol"}` for mail and for the calendar; the Gmail connector `{server: "Gmail", api:
  "gmail"}`; the Google Calendar connector `{server: "Google Calendar", api: "gcal"}`; Slack `{server: "Slack", api:
  "slack"}`. Any other tool, or none: `null`.
- On every decision and job that has one, `live`: `{thread, account}` (the mail thread and the mailbox's alias or
  address), or `{channel_id}` for a chat conversation, or `{to, subject, account}` for a mail that does not exist
  yet (plain addresses). A double booking carries `live.account` and, on each of its meetings, `organizer` and
  `event_id`.
- On every block of the strip, `live: {event_id, account}`: the calendar event it was drawn from, so the page finds
  it again.
- `draft: true` on a job that is a message to write (a reply, a mail to someone, a chat answer), with its `live`
  and `to` (who it goes to, by first name). Claude drafts it on the page; it is never sent.

| `api` | Tools to declare |
|---|---|
| `aureol` | mail: `gmail_search`, `gmail_get_thread`, `gmail_create_draft`, `gmail_update_draft`; calendar: `calendar_list_events` |
| `gmail` | `search_threads`, `get_thread`, `create_draft`, `update_draft` |
| `gcal` | `list_events` |
| `slack` | `slack_search_public_and_private`, `slack_read_channel` |

Run `python3 tools/fill-page.py --kind brief skills/aureol-brief/references/daily-brief.html DATA.json OUT.html
--links context=<link> inbox=<link>` from the plugin's root folder (the one holding `skills/` and `tools/`)
when a shell exists (it checks the data, then fills the template with every `<` escaped); without a
shell, apply check-page's list by hand and replace the single `{{DATA_JSON}}` yourself. Read the page at `connections/current.pages.brief` then publish to its `url` with
`capabilities: {db: {}, sample: {}, mcp: {servers: [{server, tools}]}}` from the table above, one entry per server
(`{db: {}, sample: {}}` when every connection is `null`); no link yet, publish new the same way and write the link. Write a `runs` document. The task prompt says how the run ends: the link on its
own line, and the counts.
