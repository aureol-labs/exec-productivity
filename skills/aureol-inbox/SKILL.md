---
name: aureol-inbox
user-invocable: false
description: Write the executive's Priority inbox: mail and chat in one queue, ranked by who is blocked and for how long, with a tier word on every line (Now, Today, This week) and the ask as the first line of every reveal. Applies labels only where the mail connection can write them and only from rules the exec confirmed, and lists every write with its rule; never archives, deletes, moves, sends or marks as read. Load from the inbox task, or when the exec asks what needs them.
---

# Priority inbox

Two jobs, and they are different jobs. Ranking decides what the exec touches. Categorising keeps the mailbox
clean. The page never lets the second pretend to be the first. Template `references/inbox.html`, one JSON
document (shape in its head comment and `references/example.json`).

## Rules that override anything you infer

1. **Labels only, and only where the mail role can write them** (`connections/current.roles.mail.can` contains
   `label`) **and only from `rules`.** One write, applied over and over. Never a delete, never a send, never a
   mark as read, never a move, never an archive. `To archive` is a label the exec clears in their own mailbox.
2. **Every write is listed** on the page, under the label, with its count and the rule in the exec's words.
   A label without a rule is not applied.
3. **The test for the queue is stated on the page**: someone is blocked, a promise is late, or only the exec can
   answer. A group ask anyone could answer is not the exec's. A thread the exec already replied to or reacted to
   is out. Check the thread before ranking it, not the snippet. **Unread first**: the queue is built from unread
   mail and unread messages; a thread the exec has read but not answered enters only when someone is visibly
   still waiting (a follow-up, a question with no reply), and the h1's counts are the real unread counts from
   the tools, never estimated.
4. **A dropped line stays dropped.** Read `dismissals` from the inbox page's store before ranking (the store is
   the page's own, at `connections/current.pages.inbox`). A thread dropped as done or not important never comes
   back, and a `done` also covers its follow-ups for 7 days. Give every queue line a stable `ref` (the thread id
   or link) so the page can record the drop.
5. **Now is a clock the exec does not control**: an offer that lapses tonight, a deck that locks tomorrow, a
   build that starts after lunch. Importance is not a tier. Then Today, then This week. Inside a tier, oldest
   first.
6. **The right column is when it arrived.** A time if today, a date otherwise. No due time you invented, no
   computed lateness, no brick on this page.
7. **Every reveal leads with the ask**, one line, then the type, then the reason, three sources, and a briefing
   that is your summary plus pointers and ends "do not send" when it drafts.
8. **The lead is a count, not a claim.** "61 unread mails, 41 unread messages. 9 need you." Filing is not
   judging, so the filed list is "labelled, still unread".

## 0. Read, probe

`connections/current`, `connections/preferences` (tiers), `rules`, `topics`, `people`, the last inbox run.
Probe mail and chat with one real call each.

## 1. Read since the last run

Mail and chat since the last inbox run (48 hours on the first run), both directions, the exec's threads only.
Every time on the page is the exec's local time (`connections/preferences.timezone`); the run may execute in
another zone.
Open every candidate thread once to check rule 3. Nothing new since the last run: publish nothing, write a
`runs` document, end with one line.

## 2. Rank

Nine to twelve lines is a page; more means the test was too loose. Each line: the tier, the channel (mail,
slack, teams), the ask with the name, the label chip when the mail role writes labels, the arrival time or date,
the typed reveal (PRECEDENT, KNOCK-ON, PATTERN, HISTORY), sources, briefing. Cross-references into today's brief
carry their whole substance.

## 3. File, where allowed

With `label` and `rules`: apply each rule, count the writes, and render `data.filed` with each label's rule, its
count per channel, three to five content lines each a link, and the `To archive` label listing every rule that
filed into it. Without `label`: no write, `data.filed` empty, `data.grouped` carries the same grouping as a
reading aid, `data.wrote` false and the footer says nothing was written to the mailbox.

## 4. Tell the context

The inbox reads the world every hour; the morning pass reads it once. So what the inbox sees goes into the store,
lightly and by the store's rules. On the topics and people this run's lines touched: `last_from_you` when the
exec replied, one `so_far` entry per new fact with its date and source, `state` when it changed. A decision found
in a message, with what it was decided against: one `decisions` document with `status: "proposed"`. Update in
place with `if_version`; never rewrite a topic, never add a topic (that is the morning's judgement), never touch
`priorities`, `rules`, `asks` or `suggestions`. If anything was written, load the `aureol-context` skill in
render mode so the Super Context page shows it.

## 5. Check, publish, record

`tools/check-page.py inbox` when a shell exists. Fill `{{DATA_JSON}}`, read the page at
`connections/current.pages.inbox`, publish to its `url` with `capabilities: {db: {}}`, or publish new the same
way and write the link. Write a `runs`
document with the counts read and the writes made. The task prompt says how the run ends: the Now count
first, so whatever preview the exec sees says what matters.
