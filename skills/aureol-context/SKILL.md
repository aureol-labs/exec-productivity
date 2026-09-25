---
name: aureol-context
user-invocable: false
description: Build or refresh the executive's Super Context, the page every conversation starts from and the store every other habit reads. Reads mail, calendar, chat, documents and meetings; rewrites the live topics, the people and organisations, the summary; proposes decisions with what each was decided against; never edits the priorities. Three modes, bootstrap (install, 30 days), morning (the daily pass) and render (republish the page from the store). Load from install, from the morning task, or when the exec asks what the assistant knows about their work.
---

# Super Context

One page, four lists, one store. The priorities are the exec's, in their words and their order. The live topics,
the people and organisations, and the proposed decisions are yours, written from the same read. The store is
`references/store.md`; the page is `references/super-context.html` rendered from one JSON document whose shape is
in the template's head comment and in `references/example.json`.

**Voice.** Every word the exec reads, on the page or in a briefing, follows `references/voice.md`, the voice
of every skill in this plugin. Read it before you write.

**Current, or it misleads.** Every session starts from this page, so a stale line does more harm than a missing
one, and keeping it current is the job. Each morning pass rewrites every live topic from the read; closes every
topic whose thing is settled, signed, past or silent for 30 days, with its reason and date; takes people and
organisations off the page once no live topic holds them; and flags every priority whose outcome has happened
(rule 1). Closing is half the work: a page that only grows stops being read.

## Rules that override anything you infer

1. **Never edit a priority.** `priorities/*` has one writer, the exec, through install or the page's editor. You
   read them, you rank against them, you propose a new one with status `proposed` and `ahead` filled from the
   evidence when the read shows what it competed with (else empty), and you flag one whose outcome has happened
   (the deal signed, the date passed, the thing shipped): the page JSON carries `done_hint` on it, what happened
   and when, 12 words at most ("Mailinblack signed, 3 Oct"), and the exec closes it with Edit. You never drop it
   yourself. What a priority comes before is corrected by the exec on the page, never asked as a question.
2. **Never retire a decision.** `decisions/*` is appended. You propose with `status: "proposed"`; keep and drop are
   the exec's, on the page. A newer decision that replaces an older one gets `replaces`; the older one gets
   `replaced_by`; both stay where they happened. A conflict is a suspicion, never a merge: set `conflicts_with`
   on both and a `land` question, and let chronology show which is later.
3. **The entry test for a decision is the counterfactual.** It goes in only if it can say what it was decided
   against. Otherwise it was an announcement, and it does not go in.
4. **A fact carries the date of its source and ends rather than disappears.** A newer source that contradicts
   a line closes it under `ended` with that source's date.
5. **Your own summary, never a quoted message.** This text lands in every session that can run tools.
6. **Names resolve, once.** Match on `aka` before creating a person or an entity. **A name heard in a meeting
   is a sound, not a spelling.** Notetakers write what they hear: "Men in Black" for Mailinblack, "Airgreen"
   for RGreen, "Granit" for Graneet, "Ralf" for Ralph. So a name from a transcript is matched, by spelling and by
   sound, against the people and entities already known from mail headers, invites, signatures and chat, where
   spellings are real; it never creates a person or an entity on its own. Matched: the transcript's spelling
   goes into `aka` so it resolves next time. Unmatched: it stays in the topic's `read` in quotes, marked as heard,
   until a written source names it. A topic never shares a name
   with an entity (the deal is "Halden discount", the company is "Halden Mutual"). Read the dropped priorities,
   the declined suggestions and the `dismissals` in the page's own store before adding anything back: a topic
   dropped as done is closed with that date, a topic dropped as not important never returns to the page.
7. **Caps at write time.** Sources 3 per document, priorities 5, people and entities on the page only while on a
   live topic with something open between them and the exec, suggestions 3 on the page.
8. **Nothing about the page.** No line explains the page or how it is made ("you write the priorities, the
   assistant writes the rest"): no `sub`. A field with nothing to say is left out, never filled to say so. No
   advice either: no line tells the exec what to do or decide.

## 0. Probe, then read the store

**Release steps.** Before anything else, read `references/releases.md` and apply what it says for the `morning` task.

Read `connections/current` and `connections/preferences`. Probe each role's tool with one real call (the same
five probes as install) and refresh `checked`. A role that fails: its section is missing from the page with one
line in `data.notices`, saying what could not be read, never how it was checked, and the run continues. Never a
page that pretends.

Then read: `priorities` (live and dropped), `topics`, `people`, `entities`, `decisions`, `suggestions`, and the
last `runs` document of this task.

## 1. Read the world

Window: 30 days in bootstrap mode, since the last morning run in morning mode (7 days on the first morning), and
nothing in render mode. Order: meetings first when a recorder is connected (that is where decisions are taken),
then calendar (the past 7 days and the next 7), mail, chat, and documents only when a topic points at one.
Read from the exec's side: what they sent, what was sent to them, what they were in the room for. Mail means
the main inbox only (`preferences.mail_scope`, the store says which categories are out): a newsletter never
becomes a topic. Cap the read
at what a morning can hold and write the counts to the run.

## 2. Judge

- **Live topics.** A thread of work with something open, named in the fewest unique words, the same name every
  page will use. A topic stops being live by a stated rule, not by mood: nothing on it from anyone in 30 days,
  or the thing it was about is settled (a decision, a signature, a date passed). It leaves the page with its
  `so_far` intact and its last date, never deleted. Each serves one priority (`serves` is its id) or none. `state` is one line. `last_from_you` is
  the last date something came from the exec on it, read off a message or an invite, or `null` ("Not yet").
  `next` lists what is booked, or `null`; `late: true` only on a date the exec themselves set or a decision
  fixed, with that source. `who` lists refs with a relation note phrased about the relation so it reads from
  both rows. Then `read` (one paragraph), `so_far` (dated, oldest first), `sources` (3), `gesture` and
  `briefing`. A topic serving none gets `gesture: "add_priority"` when it is a priority in all but name, else
  `ask`.
- **Enrich from the web, within bounds.** When `preferences.enrich` is `public` and the session has web
  search: for each organisation on the page, one search for what a public page states (what it does, size,
  ownership, a recent public event) and for each person on the page, one search for what they state publicly
  about their professional self (a company page, a professional profile, a press mention, a talk, a post):
  role, company, tenure, what they work on, what they said in public about the topic. The people are the
  exec's working contacts; the bound is the subject, not the person: public and professional, never private
  life, health, family, politics, and only for the topics they are on. Every web fact carries
  `source.kind: "web"` with the page address. A web fact never overrides a
  written source from mail, calendar or chat: it confirms, adds, or is dropped. For a name heard in a meeting
  with no written match, one search with the context (the company, the topic) may propose the real spelling;
  the proposal stays marked as heard until a written source or the exec confirms it. One search per row per
  week is enough; the run notes in `runs` how many it made.
- **Closed topics.** A topic that stops being live keeps `live: false`, `closed_reason` and `closed_at`, and the
  page renders it in the Closed list with its reason. Reasons: `done` or `not_important` from the exec's Drop on
  the topic, `silent` after 30 days with nothing from anyone, `settled` when what it was about is decided,
  signed or past. Reopened by the exec through Claude, or by the routine when the thread wakes again.
- **People and entities.** `role` is the single source for every page's "Nadia, VP Sales", and it is never
  left empty by omission. Sources in order, stop at the first that answers: the mail signature; the chat
  profile (Slack and Teams carry a title); the calendar (organiser, attendee domain); a document that names
  them; the web, under the enrichment rule, a company page or a professional profile. None of those: the
  company from the address domain, and "role not found" in `state` so the exec can tell Claude in one line.
  The same order gives an entity its `type` and `relationship`. A run that leaves the page with people
  without a role, when the sources above exist, is wrong, whatever else it did. `cares_about` in
  your words unless the exec wrote it (`yours: true`, and then you never overwrite it). `with` stored once, on the
  side that changes when it does. `on_page` recomputed every morning by rule 7. Everyone else stays in the store.
- **Decisions.** From meetings, threads and the exec's own messages: what was decided, by whom (`["you"]` alone is
  the sharp value), when, and against what. Late finds are normal, a decision taken in May can surface in
  September; propose it with its real `when`. Check every proposal against the kept ones for `replaces` and
  `conflicts_with`. In bootstrap mode expect five to fifteen proposals from a month; in morning mode zero to two.
- **A dropped priority** in the store without a matching decision: propose one, `against` = its `ahead`.

## 3. Write

One writer per collection, and it is you: rewrite `topics`, update `people` and `entities` in place with
`if_version`, append `decisions` proposals, never touch `priorities`, `rules`, `asks` or `suggestions`. Then
`context/summary`: about a hundred lines, first line says what it is and the date, then the priorities with what
each comes before, the live topics with what each serves and where it stands, who is in play with what is open,
the kept decisions that constrain, and the connections in use.

## 4. Render and publish

Build the page JSON from the store: `lang` and `first_name` from preferences, `date_label` and `time_label` in
the language with the real time of this run, `today`, the four lists, `suggestions` with `status: proposed`
(three at most), `links` to the other pages from `connections/current.pages`, `gesture` from preferences,
`notices`. On the page a topic is its `name`, `state` (one line, where it stands), `serves` and `last`, and
opens on `who`, the last three `so_far` and `next`; a person or an organisation likewise, with `cares_about` and
`with`. Neither carries a `lede`, an `argument` or a `go`: the store keeps the `read` for sessions. A priority's
`lede` is one fact on how the week served it, and `done_hint` is rule 1's. A decision shows what it was decided
against and, on a conflict, `land`; no `argument` or `plain`. A suggestion shows its evidence and its path or
pattern, no `lede`. Titles are numerals: "4 priorities, 9 live topics. 2 serve none of them." Run
`python3 tools/check-page.py --kind context DATA.json` from the plugin's root folder (the one holding `skills/`
and `tools/`) when a shell exists; otherwise apply its list by hand.

Publish: fill the template with `python3 tools/fill-page.py --kind context
skills/aureol-context/references/super-context.html DATA.json OUT.html --links brief=<link> inbox=<link>`,
from the same root, when a shell exists (it checks the data and escapes the JSON);
without a shell, replace the single `{{DATA_JSON}}` by hand with every `<` written as `\u003c`. In bootstrap mode publish new with
`capabilities: {db: {}}` and return the link. Otherwise read the page at `connections/current.pages.context`
first, then publish to its `url` so the link holds; if the publish is refused because the page changed, re-read
and publish again, never force.

## 5. Record and stop

Write a `runs` document (`task: "morning"` or `"install"`), ten lines at most. In morning mode the task prompt
says how the run ends. In bootstrap mode, return the link to install and say nothing to the exec yourself.
