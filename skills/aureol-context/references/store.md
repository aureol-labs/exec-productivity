# The store

One artifact per exec, "Super Context", published at install with `capabilities: {db: {}}`. Its database is the
plugin's only state. Every routine reads it with `read_db` and writes it with `write_db` on the artifact's link
(`{{CONTEXT_URL}}` in the task prompts). The page itself writes three things from the browser: the priorities
editor, keep and drop on decisions, decline on a suggestion. Nothing else on any page writes.

Rules that hold for every document:

- `version` comes back on every read; every write from a routine pins `if_version`. A refused write is re-read
  and redone, never forced.
- Every fact carries the date of its source (`date`, ISO `YYYY-MM-DD`) and a `source` (`{kind, label, href}` with
  `kind` one of `mail | chat | calendar | doc | meeting | file | you | web`). A `web` source is a public page
  (`href` is its address, `label` the site and what it says) used to enrich organisations and the public
  professional information of the people on the page, the exec's working contacts; it never overrides a
  written source and never creates a person. A fact that a newer source contradicts is
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
    "mail":      { "tool": "Gmail",         "can": ["search", "label"], "checked": "2026-09-22",
                   "main": { "clovis@example.com": "primary" } },
    "calendar":  { "tool": "Google Calendar","can": ["search"],          "checked": "2026-09-22" },
    "chat":      { "tool": "Slack",         "can": ["search"],          "checked": "2026-09-22" },
    "documents": { "tool": "Google Drive",  "can": ["search"],          "checked": "2026-09-22" },
    "meetings":  { "tool": null,            "can": [],                  "checked": "2026-09-22", "declined": false }
  },
  "pages": { "context": "https://claude.ai/...", "brief": "https://claude.ai/...", "inbox": "https://claude.ai/..." } }
```

`plugin`, `{ "installed": "0.8.0", "published": "0.8.0", "checked": "2026-09-29" }`, is written by the morning
brief and by `exec-productivity-update` when the session can fetch the published manifest; `installed` is the
newest heading of `releases.md`. Absent, nobody could check.

`pages` holds the link of each page once published; a routine reads the page at that link and publishes to its
`url` so the link holds. A missing entry means the page has not been published yet.

`tool` is the connector's display name or `null`. `can` lists only capabilities proven by a real call. A tool that
is connected but answered nothing is `null` with a `note`. `send` is the one capability never proven by a call:
it is listed when the mail tool has a send call, and nothing is ever sent to prove it. `calendar.calendars`,
optional, lists calendar ids when the exec uses more than one through the one connection (a second address shared
into the first): every calendar read then covers each id and merges them, one event per event id and one for the
same title at the same start, double bookings counted across them. A probe rewrites `tool`, `can` and `checked`
and keeps every other field.

`connections/preferences`, written by install, edited only through install or the `exec-productivity-help` skill:

```json
{ "language": "fr", "timezone": "Europe/Paris", "first_name": "Clovis",
  "morning": "08:15", "inbox": ["12:45", "18:45"], "review": "18:00",
  "rhythm": { "read": "2026-10-01", "first_meeting": "08:45", "mail_peaks": ["13:00", "19:00"],
              "day_end": "18:30", "source": "inferred" },
  "key_people": ["people/nadia", "people/tomas", "people/julien"],
  "caps": { "decisions": 3, "jobs": 3 }, "tiers": ["Now", "Today", "This week"],
  "mail_scope": "main", "mailboxes": ["clovis@example.com"], "enrich": "public",
  "gesture": "copy", "metrics": null,
  "notify": { "brief": "push", "inbox": "push_now", "review": "push" },
  "installed": "2026-09-22", "plugin_version": "0.3.3" }
```

`notify.<habit>` is `push` (the run ends by sending one notification with the session's notification tool, one
line under 200 characters, desktop and phone when the Claude app is on the phone), `push_now` (inbox only: a
notification only when something is Now), `email` (one message to the exec's own address, only where the mail
role can send, never for the inbox; for the brief, the page itself rendered for a mailbox, with its link), or
`none` (the pinned page). `notify.brief` can be a list, `["push", "email"]`: both. Install sets `push`,
`push_now`, `push` and asks one thing, the brief by email too, where the mail role can send; the exec changes any of it through `exec-productivity-help`. Nothing is
automatic: the run decides from this value. `installed` is the day of the install and
`plugin_version` the manifest's version that day, both written by install.

`morning`, `inbox` and `review` are read by install from the exec's last 30 days (the first meeting, the hours
their mail goes out, the end of their day) and shown under the priorities for the same go, never asked; with
not enough to read, 08:30, then 11:00, 13:00, 15:00 and 17:00 (the morning run is the inbox's first pass), then
17:30. `rhythm` keeps what was read: a field is `null` when nothing was read for it, and `source` is `inferred`,
`default` or `yours` (the exec changed it, at install or through `exec-productivity-help`). `key_people` lists
up to five `people/<id>` refs the inbox never cuts when its page is full; absent on installs before 0.9.0, and
then nobody is protected. Both change through `exec-productivity-help`. `inbox` is a
list of weekday times that share one minute value, so they fit one schedule line. The review's notification
fires only on a day something worth it qualified. `mail_scope` is `"main"` (the
default) or `"all"`. Under `main`, every skill that reads mail, context, brief, inbox and review, reads each
mailbox's main inbox only, in the form `connections/current.roles.mail.main` names for that mailbox:

- `primary`: the mailbox's own main view, what the exec sees first. Gmail: `in:inbox category:primary`, which
  follows the tabs they turned on (an Updates mail shows there when they have no Updates tab). Outlook: the
  Focused inbox.
- `minus_categories`: the inbox without the mailbox's bulk categories. Gmail: `in:inbox -category:promotions
  -category:social -category:updates -category:forums`. Outlook: the inbox without Other, Junk or Clutter.

Every run's probe counts both forms over its window, per mailbox, and writes `main`: `primary` when it returns
mail; `minus_categories` when it is empty while the other form is not (Gmail with its tabs turned off has an
empty Primary, seen on 2026-10-01; Outlook with Focused off). The exec can change their settings any day, so the
check is never cached across runs. Either way the bulk categories stay out: not read, not counted, not ranked.
An exec who runs inbox zero on their main inbox must never see 4,182 unread on the page.
`mailboxes` lists the connected mail accounts read; the page names any address the exec uses that is not
connected. `metrics` is `null` until a business metric source is named and proven by a real call; the brief renders no
metrics block while it is `null`.

`gesture` is `copy` (the briefing is copied to the clipboard, the default, written at install step 2) or `link`
(a `https://claude.ai/new?q=` link). `enrich` is `"public"` (the default: web lookups on organisations and on the public professional information
of the people on the page) or `"none"`; changed through `exec-productivity-help`.

`connections/in_place`, what the exec already has in Claude, written by any session that can list it (the
review when its task tool answers, `exec-productivity-help`), read by the review before it proposes anything:

```json
{ "checked": "2026-09-28",
  "tasks": [ { "name": "Newsletter digest", "schedule": "weekdays 07:30",
               "does": "Gathers the morning's newsletters into one digest mail." } ],
  "skills": [ { "name": "consulting-report", "from": "yours", "does": "The prep note before a client meeting." } ] }
```

`tasks` lists every scheduled task on the account, the assistant's three included; `does` is one line on what
its prompt produces, in the store's own words. `skills` lists the skills this session offers, `from` the plugin
that brings them or `yours`. A stale stock is better than none: the review never proposes what it lists.

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
  "gesture": "ask", "proposal": null,
  "briefing": "What the Claude button hands over: the routine's summary plus pointers.",
  "live": true }
```

`aka` holds the shorthand the exec and their colleagues use for the topic, read off the threads, so a chat
that says "the Aviva thing" resolves; same on people and entities, where it also holds the mis-hearings a
notetaker produces ("Men in Black" for Mailinblack), so a transcript resolves to the entity the mail spells. `serves` is a priority id or `null` (rendered as None). `next` is a list or `null` (rendered "Nothing booked").
`late: true` on a `next` entry renders in brick with "Was due <date>" and is allowed only when the date comes from
a decision or a promise the routine can point at. `gesture` is `ask`, `add_priority` or `none`; `proposal` carries the proposed priority's wording when `gesture` is
`add_priority`, else `null`.

### Closed topics, on the page

`topics/<id>` keeps `live: false` with `closed_reason` (`done | not_important | silent | settled`) and
`closed_at` when a topic stops being live. The page renders them in a "Closed" list at the end, greyed, three
rows and "and N more", so what left the page leaves a trace the exec can read and reopen through Claude. A
`done` or `not_important` dismissal on an inbox line or a job that served a topic closes nothing by itself: it
becomes a `so_far` fact; the topic closes by the topic rule (settled, silent 30 days) or by its own Drop.

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
`with[].type` is one of `member of | leads | sits on | contact for`, stored on one side only. The page JSON spells
the same four `member_of`, `leads`, `sits_on`, `contact_for` and carries the inverse on the other row (`member`,
`led_by`, `seat`, `contact`); the routine maps when it builds the page. `note` must read correctly from both rows, so it
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

Seven at most, three fixed (Read later, Receipts, To archive) and four work labels, `tint` one of
`sales | product | board | customers | hiring | later | receipts | arch`. `label` is the name as written in the
mailbox, in the exec's language ("Factures" and "À archiver", not "Receipts" and "To archive", for a French
exec); `tint` is the colour slot and never shows. `receipts` is the Receipts label: invoices, payment receipts,
order and delivery confirmations, never To archive. `archive: true` is the To archive label, drawn as an outline.

### `asks` and `suggestions`, the end-of-day review

```json
{ "date": "2026-09-17", "to": "people/julien", "what": "The cohort numbers for the board pack.",
  "system": "Power BI", "connector": { "name": null, "uuid": null }, "plugin": { "name": null, "path": null },
  "source": { "kind": "mail", "label": "To Julien, 17 Sept", "href": "" }, "status": "found" }
```

`status` is `found | proposed | declined | connected`. `source.kind` is `"you"` for an ask the exec named
themselves (the install's one question): `to` is `null`, `what` their words verbatim, and the review ranks it
first. `plugin` names the ready-made plugin or skill from the
Claude catalog that covers the ask, when one does. A scheduled run without the catalog tools writes `"unknown"`
as `connector` or `plugin`, and the next `exec-productivity-help` session resolves it. `suggestions/<id>`:

```json
{ "kind": "connection", "say": "Your HubSpot pipeline, read by your assistant when you ask.",
  "system": "HubSpot", "connector": { "name": "HubSpot", "uuid": "875dee50-..." },
  "evidence": ["a-2026-09-17-julien"], "status": "proposed", "proposed_at": "2026-09-19" }
```

`kind` is `prompt`, `connection`, `plugin`, `skill` or `routine`; `say` is the use case in one sentence, as
value, the words the page and the run's table show. Every suggestion carries its how: `prompt`, the words the
exec could have typed; `attach`, what to give it, absent when nothing; `needs`, `[{ "name": "Google Drive",
"connected": true }]`, each connection it uses. A prompt suggestion needs nothing added: its `briefing` is the
prompt, which the Claude button copies. A plugin suggestion names an off-the-shelf plugin or
skill from the Claude catalog that already covers the ask (`name`, `path`: where to add it, the marketplace or
the card); it comes before a custom skill whenever one exists. A skill suggestion carries `name` and `pattern`
(the ask that repeats, reached for on demand, and nothing on the shelf covers it). A routine suggestion carries `name`, `pattern` (the cadence and what it
produces: "every Monday before 09:00, the pipeline numbers as a page") and a `briefing` that lets Claude create
the scheduled task with its prompt drafted. A suggestion that changes a task or skill already in place carries `extends`, its name; the review never
proposes a second one beside it. A declined suggestion is never proposed again. The page's
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

### What the live inbox keeps in its own store

The Priority inbox page writes these itself, in its own artifact's store; no routine writes them, and a routine
reads none of them except `dismissals`.

- `inbox/provisional`: what the page sorted since the run, `{verdicts: {"<ref>@<message time>": {tier, say,
  fact, type, kind}}, filed: {<ref>: label}, at}`. A run that publishes again makes its verdicts old: the page
  keeps only those newer than the run.
- `inbox/snapshot`: the page's own whole sort, on a day it was opened before any run: `{scope, day, at, seen,
  lines}`. Ignored once a run of the same day has published.
- `inbox/lens`: `{own, updated}`, what the exec added on the page to what the sort knows about them. The run's
  part is `live.lens` in the page's data; the page reads both and never lets a run overwrite `own`.
- `threads/<slug of ref>`: a thread's summary, `{ref, key, at, summary}`, kept until the thread moves.

### `runs`, one per run

```json
{ "task": "morning", "started": "2026-09-22T06:52:00+02:00", "ended": "2026-09-22T06:58:00+02:00",
  "read": { "mail": 61, "chat": 41, "calendar": 6, "meetings": 2, "documents": 0 },
  "wrote": ["topics", "people", "entities", "context/summary", "decisions: 1 proposed"],
  "failed": [], "pages": { "context": "https://claude.ai/...", "brief": "https://claude.ai/..." },
  "version": "0.6.0", "note": "Ten lines at most." }
```

`task` is one of `install | morning | inbox | review`, the habit that wrote the document. The install's document,
`<date>-install`, is written as soon as the store exists and kept current: `done` lists the steps finished and
`ended` stays empty until the install ends, so a setup that stopped is picked up where it was. `version` is the
newest entry of `releases.md` when the run ended: the next run of the same task compares it to decide which
release steps it still owes.

### `context/summary`, what a session reads first

```json
{ "written": "2026-09-22T06:55:00+02:00", "text": "About a hundred lines: the date, the priorities with what each
  comes before, the live topics with what each serves and where it stands, who is in play with what is open, the
  live decisions that constrain, and the connections in use. The first line says what this is." }
```

## Pages are projections

Each page template embeds one JSON document in `<script id="data" type="application/json">` and renders from it.
The routine builds that JSON from the store; it never hand-writes rows. The shapes are documented in each template's
head comment and in `example.json` next to it, which is also the fixture `tools/check-page.py --kind <kind>` is tested against.
