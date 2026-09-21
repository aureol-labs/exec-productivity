---
name: aureol-context
description: Build or refresh the executive's Super Context, the page every conversation starts from and the store every other habit reads. Reads mail, calendar, chat, documents and meetings; rewrites the live topics, the people and organisations, the summary; proposes decisions with what each was decided against; never edits the priorities. Three modes, bootstrap (install, 30 days), morning (the daily pass) and render (republish the page from the store). Load from install, from the morning task, or when the exec asks what the assistant knows about their work.
---

# Super Context

One page, four lists, one store. The priorities are the exec's, in their words and their order. The live topics,
the people and organisations, and the proposed decisions are yours, written from the same read. The store is
`references/store.md`; the page is `references/super-context.html` rendered from one JSON document whose shape is
in the template's head comment and in `references/example.json`.

## Rules that override anything you infer

1. **Never edit a priority.** `priorities/*` has one writer, the exec, through install or the page's editor. You
   read them, you rank against them, you propose a new one with status `proposed` and `ahead` filled from the
   evidence when the read shows what it competed with (else empty), and that is all. What a priority comes
   before is corrected by the exec on the page, never asked as a question.
2. **Never retire a decision.** `decisions/*` is appended. You propose with `status: "proposed"`; keep and drop are
   the exec's, on the page. A newer decision that replaces an older one gets `replaces`; the older one gets
   `replaced_by`; both stay where they happened. A conflict is a suspicion, never a merge: set `conflicts_with`
   on both and a `land` question, and let chronology show which is later.
3. **The entry test for a decision is the counterfactual.** It goes in only if it can say what it was decided
   against. Otherwise it was an announcement, and it does not go in.
4. **A fact carries the date of its source and ends rather than disappears.** A newer source that contradicts
   a line closes it under `ended` with that source's date.
5. **Your own summary, never a quoted message.** This text lands in every session that can run tools.
6. **Names resolve, once.** Match on `aka` before creating a person or an entity. A topic never shares a name
   with an entity (the deal is "Halden discount", the company is "Halden Mutual"). Read the dropped priorities
   and the declined suggestions before adding anything back.
7. **Caps at write time.** Sources 3 per document, priorities 5, people and entities on the page only while on a
   live topic with something open between them and the exec, suggestions 3 on the page.

## 0. Probe, then read the store

Read `connections/current` and `connections/preferences`. Probe each role's tool with one real call (the same
five probes as install) and refresh `checked`. A role that fails: its section is missing from the page with one
line in `data.notices`, and the run continues. Never a page that pretends.

Then read: `priorities` (live and dropped), `topics`, `people`, `entities`, `decisions`, `suggestions`, and the
last `runs` document of this task.

## 1. Read the world

Window: 30 days in bootstrap mode, since the last morning run in morning mode (7 days on the first morning), and
nothing in render mode. Order: meetings first when a recorder is connected (that is where decisions are taken),
then calendar (the past 7 days and the next 7), mail, chat, and documents only when a topic points at one.
Read from the exec's side: what they sent, what was sent to them, what they were in the room for. Cap the read
at what a morning can hold and write the counts to the run.

## 2. Judge

- **Live topics.** A thread of work with something open, named in the fewest unique words, the same name every
  page will use. Each serves one priority (`serves` is its id) or none. `state` is one line. `last_from_you` is
  the last date something came from the exec on it, read off a message or an invite, or `null` ("Not yet").
  `next` lists what is booked, or `null`; `late: true` only on a date the exec themselves set or a decision
  fixed, with that source. `who` lists refs with a relation note phrased about the relation so it reads from
  both rows. Then `read` (one paragraph), `so_far` (dated, oldest first), `sources` (3), `gesture` and
  `briefing`. A topic serving none gets `gesture: "add_priority"` when it is a priority in all but name, else
  `ask`.
- **People and entities.** `role` is the single source for every page's "Nadia, VP Sales". `cares_about` in
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
`notices`. Titles are numerals: "4 priorities, 9 live topics. 2 serve none of them." Run
`tools/check-page.py context` on the JSON when a shell exists; otherwise apply its list by hand.

Publish: fill `{{DATA_JSON}}` in `references/super-context.html`. In bootstrap mode publish new with
`capabilities: {db: {}}` and return the link. Otherwise read the page at `connections/current.pages.context`
first, then publish to its `url` so the link holds; if the publish is refused because the page changed, re-read
and publish again, never force.

## 5. Record and stop

Write a `runs` document (`task: "morning"` or `"install"`), ten lines at most. In morning mode the task prompt
says how the run ends. In bootstrap mode, return the link to install and say nothing to the exec yourself.
