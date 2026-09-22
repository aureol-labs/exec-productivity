# exec-productivity

A Claude plugin that runs a time-poor executive's daily operating routines in Claude Cowork and produces three
pages: a Super Context the assistant starts every conversation from, a Daily brief every weekday morning, and a
Priority inbox through the day. A review at the end of each weekday looks at the last seven days for the work
Claude could do instead of the exec, and proposes only what can be added, a connection, a ready-made plugin, a
routine or a skill, staying silent when there is nothing new. Built by [Aureol](https://aureol.co).

Not a dashboard. Not a task manager. A notebook that arrives already written, and gets better the longer it runs:
the brief asks for decisions, Super Context records them with what they were decided against, and tomorrow's brief
says "you refused this exact shape in July".

## Install, three gestures

In the Claude desktop app:

1. Plugins, add a marketplace from the repo `aureol-labs/exec-productivity`, install **Exec productivity**.
2. Type `/`, choose **make-me-productive**, and answer its questions. About ten minutes. It ends on your first
   brief.
3. Pin the three pages.

The guide with screenshots, in French: [guide/guide-fr.md](guide/guide-fr.md).

## What it reads, what it writes

Reads, through your own connections: mail, calendar, internal chat, documents, meetings (a notetaker such as
Granola). Writes only its three pages and their store. Where your mailbox allows it and only from rules you
wrote, it applies labels, each one listed on the inbox page with its rule. It never sends, deletes, moves,
archives or marks as read.

## The habits

| Habit | When | Page |
|---|---|---|
| morning | weekdays, at the time chosen at install (proposed from the calendar: 30 minutes before the usual first meeting) | Super Context refreshed, the Daily brief, the day's first Priority inbox |
| inbox | weekdays, 11:30, 13:30 and 16:30 by default (the morning run is the fourth pass); hourly as an option | Priority inbox, and what it learned into Super Context |
| review | weekdays 17:30 | the review, on Super Context; silent when nothing new |

Each habit runs in the cloud, so it runs with the laptop shut. Its result is the pinned page. How the exec is
told is their choice at install, per habit, after a test notification: a one-line notification (desktop, and
phone when the Claude app is there), an email to their own address where their mailbox can send, or nothing. The
inbox can notify only when something is urgent. Nothing is automatic: each run decides from that choice.

## How the habits fit together

One store, three habits, one order. Super Context is built first, inside the install, because everything else
ranks against it. Then:

1. **Morning, at the chosen time**: the deep harvest. `aureol-context` reads the night and the last seven days across every
   connection, meetings first, rewrites the live topics, the people and organisations and the summary, proposes
   decisions, republishes Super Context. Then `aureol-brief` reads that store and today's calendar and writes the
   Daily brief. Then `aureol-inbox` once, so the three pages are fresh together. One session, one message.
2. **Inbox, three more times a day, 11:30, 13:30 and 16:30** (or hourly, or the rhythm chosen at install): the light pass. `aureol-inbox` reads
   what arrived since the last run, ranks what needs the exec, publishes the Priority inbox, and writes what it
   learned into the store: a reply from the exec, a new fact on a topic, a decision taken in a thread. It never
   adds a topic or touches the priorities; that judgement stays with the morning. Nothing new, nothing
   published.
3. **End of day, 17:30**: `aureol-review` looks at the last seven days for the work Claude could do instead of
   the exec and proposes what to add on Super Context; nothing new, one line and no notification.

The exec's writes come from the page: priorities in the editor, keep and drop on decisions, decline on a
suggestion. The routines propose; the exec decides.

## Skills

| Skill | Does |
|---|---|
| `make-me-productive` | the guided setup, ending on the first brief and the three habits |
| `aureol-context` | Super Context: topics, people, entities, proposed decisions, the summary, the page |
| `aureol-brief` | the Daily brief |
| `aureol-inbox` | the Priority inbox |
| `aureol-review` | the end-of-day review: where Claude would do the work, and what to add for it |
| `help` | the assistant explaining and fixing itself |

The store every skill reads and writes: [skills/aureol-context/references/store.md](skills/aureol-context/references/store.md).
The design system: `design/`, inlined into every page template by `tools/build-templates.py`. Every generated page
is checked by `tools/check-page.py`.

## Updating

Plugin card, Check for updates, keep Sync automatically on. Skills and templates apply on the next run. A habit's
prompt is stored on the scheduled task at creation, so a release that changes one says so, and `help` recreates
the tasks.

## Rules of this repo

- Skills, templates and docs are in English. Everything the exec reads is in the language they chose.
- No em dashes, anywhere, in any language. Numerals for counts. The most meaning in the fewest words.
- Never document a value that lives in the store. Docs describe shapes and reasons.
- No client data, no real person's data, no secrets. The example data is fictional (Meridian, a 120-person B2B
  SaaS, and its invented cast).
