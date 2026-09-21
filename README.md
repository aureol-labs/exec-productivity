# aureol-exec-productivity

A Claude plugin that runs a time-poor executive's daily operating routines in Claude Cowork and produces three
pages: a Super Context the assistant starts every conversation from, a Daily brief every weekday morning, and a
Priority inbox twice a day. A Friday review reads the exec's own asks to colleagues and proposes the connections
and skills that would have answered them. Built by [Aureol](https://aureol.co).

Not a dashboard. Not a task manager. A notebook that arrives already written, and gets better the longer it runs:
the brief asks for decisions, Super Context records them with what they were decided against, and tomorrow's brief
says "you refused this exact shape in July".

## Install, three gestures

In the Claude desktop app:

1. Plugins, add a marketplace from the repo `paul-r-92/aureol-exec-productivity`, install **Aureol exec
   productivity**.
2. Type `/aureol-exec-productivity:install` and answer its questions. About ten minutes. It ends on your first
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
| morning | weekdays 06:50 | Super Context refreshed, then the Daily brief |
| inbox | weekdays 12:30 and 16:30 | Priority inbox |
| weekly | Friday 16:30 | the review, on Super Context |

Each habit runs in the cloud, so it runs with the laptop shut, and its message arrives by email with the link.

## Skills

| Skill | Does |
|---|---|
| `install` | the guided setup, ending on the first brief and the three habits |
| `context` | Super Context: topics, people, entities, proposed decisions, the summary, the page |
| `brief` | the Daily brief |
| `inbox` | the Priority inbox |
| `review` | the Friday review: asks, connections, skill candidates |
| `help` | the assistant explaining and fixing itself |

The store every skill reads and writes: [skills/context/references/store.md](skills/context/references/store.md).
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
