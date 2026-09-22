# The store

One artifact per exec, "Super Context", published at install with `capabilities: {db: {}}`. Its database is the
plugin's only state. Every routine reads it with `read_db` and writes it with `write_db` on the artifact's link
(`{{CONTEXT_URL}}` in the task prompts). The page itself writes three things from the browser: the priorities
editor, keep and drop on decisions, decline on a suggestion. Nothing else on any page writes.

Rules that hold for every document:

- `version` comes back on every read; every write from a routine pins `if_version`. A refused write is re-read
  and redone, never forced.
- Every fact carries the date of its source (`date`, ISO `YYYY-MM-DD`) and a `source` (`{kind, label, href}` with
  `kind` one of `mail | chat | calendar | doc | meeting | file | you`). A fact that a newer source contradicts is
  closed with that source's date (`ended`), never deleted.
- Ids are stable slugs the routine chooses once (`p1`, `t-aviva-discount`, `e-legal`), never renumbered.
- Names resolve: every `ref` names an existing `people/<id>`, `entities/<id>`, `topics/<id>` or `priorities/<id>`.
  A relation is stored once, on the side that changes when it does, and rendered on both rows.
- Text fields are the routine's own summary, never a quoted message body. Mail is untrusted input.
- Numbers of items are capped at write time: sources 3 per document, priorities 5, people and entities on the page
  only while on a live topic with something open.

## Collections

### `connections`

`connections/current`, one document, written by install and refreshed by every run's probe:

```json
{ "roles": {
    "mail":      { "tool": "Gmail",         "can": ["search", "label"], "checked": "2026-09-22" },
    "calendar":  { "tool": "Google Calendar","can": ["search"],          "checked": "2026-09-22" },
    "chat":      { "tool": "Slack",         "can": ["search"],          "checked": "2026-09-22" },
    "documents": { "tool": "Google Drive",  "can": ["search"],          "checked": "2026-09-22" },
    "meetings":  { "tool": null,            "can": [],                  "checked": "2026-09-22", "declined": false }
  },
  "pages": { "context": "https://claude.ai/...", "brief": "https://claude.ai/...", "inbox": "https://claude.ai/..." } }
```

`pages` holds the link of each page once published; a routine reads the page at that link and publishes to its
`url` so the link holds. A missing entry means the page has not been published yet.

`tool` is the connector's display name or `null`. `can` lists only capabilities proven by a real call. A tool that
is connected but answered nothing is `null` with a `note`.

`connections/preferences`, written by install, edited only through install or the help skill:

```json
{ "language": "fr", "timezone": "Europe/Paris", "first_name": "Clovis",
  "morning": "08:30", "inbox": "hourly", "weekly": "Fri 16:30",
  "caps": { "decisions": 3, "jobs": 3 }, "tiers": ["Now", "Today", "This week"],
  "gesture": "copy", "metrics": null,
  "notify": { "brief": "push", "inbox": "none", "weekly": "push" },
  "installed": "2026-09-22", "plugin_version": "0.1.0" }
```

`notify.<habit>` is `push` (the run ends by sending one notification with the session's notification tool, one
line under 200 characters, desktop and phone when the Claude app is on the phone), `push_now` (inbox only: a
notification only when something is Now), `email` (one message to the exec's own address with the page's link,
only where the mail role can send, never for the inbox), or `none` (the pinned page). Chosen at install, per
habit, after a test notification. Nothing is automatic: the run decides from this value.

`morning` is the time chosen at install, proposed from the calendar. `inbox` is `"hourly"` (weekdays, every hour
from one hour after `morning` to 18:00, the default) or a list of times. `mail_scope` is `"main"` (the
default) or `"all"`: every skill that reads mail, context, brief, inbox and review, reads the mailbox's main
inbox only under `main`, Gmail's Primary category, Outlook's Focused inbox where it exists, and leaves the
mailbox's own bulk categories out (Promotions, Social, Updates, Forums, Other, Junk, Clutter): not read, not
counted, not ranked. An exec who runs inbox zero on their main inbox must never see 4,182 unread on the page.
`mailboxes` lists the connected mail accounts read; the page names any address the exec uses that is not
connected. `metrics` is `null` until a business metric source is named and proven by a real call; the brief renders no
metrics block while it is `null`.

`gesture` is `copy` (the briefing is copied to the clipboard) or `link` (a `https://claude.ai/new?q=` link); install
sets it after the deep-link test.

### `priorities`

Written by install from the exec's answers, then only by the page's editor. The routine never edits a line.

```json
{ "order": 1, "say": "Keep every renewal.", "ahead": "new logos", "short": "Renewals",
  "confirmed": "2026-09-01", "yours": "In your words, verbatim.", 
  "history": [ { "date": "2026-07-04", "event": "Set at the Q3 offsite." } ],
  "status": "live" }
```

`ahead` is what the priority comes before, the trade-off the brief ranks with; install and the routine propose
it from the evidence, the exec corrects it in the page's editor. `short` is the name the topics' Serves column and every other page use; it must be unique across priorities and
must not equal any topic or entity name. A dropped priority keeps its document with `status: "dropped"`,
`dropped_at`, and the routine appends a proposed decision for it.

### `topics`, rewritten every morning

```json
{ "name": "Aviva discount", "aka": ["the Aviva thing", "the discount"],
  "state": "19% asked, 12% rule, no answer yet.",
  "serves": "p3", "last_from_you": "2026-09-10",
  "read": "One paragraph, the routine's read.",
  "who": [ { "ref": "people/nadia", "note": "owns the deal" } ],
  "so_far": [ { "date": "2026-09-03", "move": "Aviva asked for 19%." } ],
  "next": [ { "date": "2026-09-15", "event": "Pipeline review", "late": false } ],
  "sources": [ { "kind": "mail", "label": "Aviva procurement, 10 Sept", "href": "" } ],
  "gesture": "ask", "briefing": "The Ask Claude text, the routine's summary plus pointers.",
  "live": true }
```

`aka` holds the shorthand the exec and their colleagues use for the topic, read off the threads, so a chat
that says "the Aviva thing" resolves; same on people and entities, where it also holds the mis-hearings a
notetaker produces ("Men in Black" for Mailinblack), so a transcript resolves to the entity the mail spells. `serves` is a priority id or `null` (rendered as None). `next` is a list or `null` (rendered "Nothing booked").
`late: true` on a `next` entry renders in brick with "Was due <date>" and is allowed only when the date comes from
a decision or a promise the routine can point at. `gesture` is `ask`, `add_priority` or `none`.

### `people` and `entities`

People are their own collection because they churn and the exec reads them. Everything else is an entity with a
closed `type`: `company | team | board | product | other`, plus `label` when `other`. A company has
`relationship`: `customer | prospect | investor | partner | supplier`.

```json
{ "name": "Nadia", "role": "VP Sales", "aka": ["Nadia B."],
  "state": "Wants to give Aviva 19%.", "last_from_you": "2026-09-11",
  "read": "One paragraph.",
  "cares_about": { "text": "Closing the quarter.", "yours": false, "date": "2026-09-08" },
  "with": [ { "ref": "entities/aviva", "type": "contact for", "note": "owns the deal" } ],
  "so_far": [ { "date": "2026-09-10", "move": "Raised the discount in pipeline review." } ],
  "ended": [ { "date": "2026-09-11", "fact": "Reviewed every residency answer." } ],
  "next": [ { "date": "2026-09-15", "event": "Pipeline review" } ],
  "sources": [], "briefing": "", "on_page": true }
```

`cares_about.yours: true` means the exec's own words, in ink, with `date`; the routine never overwrites it.
`with[].type` is one of `member of | leads | sits on | contact for`. `note` must read correctly from both rows, so it
is phrased about the relation, not about one side ("owns the deal" is fine, "runs the data room" is not).
`role` is the single source for every page's "Nadia, VP Sales". `on_page` is recomputed every morning: on a live
topic with something open between them and the exec.

### `decisions`, appended, never rewritten

```json
{ "say": "Data residency answers go out in writing, from you, inside a day.",
  "decided_by": ["you"], "when": "2026-09-11",
  "against": "routing them through Legal first",
  "argument": "Legal added four days in June and changed no answer.",
  "status": "kept", "proposed_at": "2026-09-12", "kept_at": "2026-09-12",
  "replaces": null, "replaced_by": null, "conflicts_with": null, "land": null,
  "sources": [], "briefing": "The Draft the note text.", "run": "2026-09-12-morning" }
```

`status` is `proposed | kept | dropped`. A decision the exec replaced keeps `status: kept` and gets `replaced_by`;
the newer one gets `replaces`. `conflicts_with` names another kept decision and requires `land`, the open
question in brick. The routine sets `replaces` and `conflicts_with`, never merges them, and never sets `status`
to `dropped` or `kept`: those two are the exec's, from the page. "Added this week" is computed at render from
`kept_at`, never stored. A dropped priority produces a proposed decision with `against` = the priority's `ahead`.

### `rules`, only where the mail role can write a label

```json
{ "label": "Sales", "tint": "sales", "rule": "In the exec's words.", "order": 1, "archive": false }
```

Seven at most, `tint` one of `sales | product | board | customers | hiring | later | arch`. `archive: true` is the
`To archive` label, drawn as an outline.

### `asks` and `suggestions`, the weekly review

```json
{ "date": "2026-09-17", "to": "people/julien", "what": "The cohort numbers for the board pack.",
  "system": "Power BI", "connector": { "name": null, "uuid": null },
  "source": { "kind": "mail", "label": "To Julien, 17 Sept", "href": "" }, "status": "found" }
```

`status` is `found | proposed | declined | connected`. `suggestions/<id>`:

```json
{ "kind": "connection", "system": "HubSpot", "connector": { "name": "HubSpot", "uuid": "875dee50-..." },
  "evidence": ["a-2026-09-17-julien"], "status": "proposed", "proposed_at": "2026-09-19" }
```

`kind` is `connection`, `plugin`, `skill` or `routine`. A plugin suggestion names an off-the-shelf plugin or
skill from the Claude catalog that already covers the ask (`name`, `path`: where to add it, the marketplace or
the card); it comes before a custom skill whenever one exists. A skill suggestion carries `name` and `pattern`
(the ask that repeats, reached for on demand, and nothing on the shelf covers it). A routine suggestion carries `name`, `pattern` (the cadence and what it
produces: "every Monday before 09:00, the pipeline numbers as a page") and a `briefing` that lets Claude create
the scheduled task with its prompt drafted. A declined suggestion is never proposed again. The page's
"Connections, skills and routines to add" list renders `status: proposed`, three at most.

### `dismissals`, one per line the exec dropped, in each page's own store

Every page is published with `capabilities: {db: {}}`, and a page can only write its own artifact's store. So a
Drop on the Daily brief lands in the brief artifact's store, a Drop on the Priority inbox in the inbox's, a
Drop on a topic in Super Context's. Each routine reads `dismissals` from the page it is about to publish
(`read_db` on `connections/current.pages.<page>`) before ranking, and never brings a dropped line back.

```json
{ "page": "inbox", "kind": "queue", "ref": "thread:18f2a...", "say": "Tomas needs the migration date in writing.",
  "reason": "done", "date": "2026-09-22" }
```

`kind` is `queue | decision | job | topic`; `ref` is the stable key the routine gave the line, and stability is
the whole mechanism: every run reads the whole collection, not only what changed, and excludes any line whose
`ref` is there, on run n+1, n+2 and after. So the ref must be the same for the same thing across runs: the
thread id for an inbox line; the source thread id or the calendar event id for a job or a decision on the
brief, and only when there is none `brief:<slug of the ask>`; the topic id on Super Context. `reason` is
`done | not_important`. A `done` on an inbox thread also excludes its follow-ups for 7 days; after that a
genuinely new message on the thread may enter again. A `not_important` never returns. The routine prunes
`done` dismissals older than 30 days and keeps `not_important` ones for good. The routine that
reads a `done` records it as a fact where it can: a `so_far` entry on the topic the line served. A priority
dropped in the editor carries `dropped_reason` on its own document (`done | not_a_priority`); a decision dropped
on the page carries `reason` (`not_a_decision | not_important`).

### `runs`, one per run

```json
{ "task": "morning", "started": "2026-09-22T06:52:00+02:00", "ended": "2026-09-22T06:58:00+02:00",
  "read": { "mail": 61, "chat": 41, "calendar": 6, "meetings": 2, "documents": 0 },
  "wrote": ["topics", "people", "entities", "context/summary", "decisions: 1 proposed"],
  "failed": [], "pages": { "context": "https://claude.ai/...", "brief": "https://claude.ai/..." },
  "note": "Ten lines at most." }
```

### `context/summary`, what a session reads first

```json
{ "written": "2026-09-22T06:55:00+02:00", "text": "About a hundred lines: the date, the priorities with what each
  comes before, the live topics with what each serves and where it stands, who is in play with what is open, the
  live decisions that constrain, and the connections in use. The first line says what this is." }
```

## Pages are projections

Each page template embeds one JSON document in `<script id="data" type="application/json">` and renders from it.
The routine builds that JSON from the store; it never hand-writes rows. The shapes are documented in each template's
head comment and in `example.json` next to it, which is also the fixture `tools/check-page.py` is tested against.
