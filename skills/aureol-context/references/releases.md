# Releases

What an installed assistant does when the plugin moves on. Skills, templates and this file reach every run on
their own. A scheduled task keeps the prompt it was created with, and a page keeps its last publish until its
next run, so a release that changes either says here what each habit does about it.

Every habit reads this file before anything else in its run. The newest entry is the plugin's version. When it
is newer than the `version` on this task's last `runs` document, or that document has none, the steps of every
newer entry that name this task are owed, oldest first. A run follows each owed step's new behaviour at once. A
step that edits a task (its prompt, its name, its schedule) needs a task tool, which a scheduled run in the
cloud does not have: the run writes it in its `note` and carries on, and `exec-productivity-help` does it in the
exec's next session. The run writes the newest version in its `runs` document. Never tell the exec about a step;
the pages show what changed.

Tasks are named as the store names them: `morning`, `inbox`, `review`. Placeholders in a reference prompt are
filled from the store: `{{LANGUAGE}}`, `{{FIRST_NAME}}` and `{{TIMEZONE}}` from `connections/preferences`,
`{{CONTEXT_URL}}` from `connections/current.pages.context`, `{{RUN_TIME}}` from the habit's times in
`connections/preferences`.

## 0.12.7

- No task step. The inbox demo on Outlook speaks of categories, not labels.

## 0.12.6

- No task step. The inbox demo has a quiet switch at the bottom: Slack or Teams, Gmail or Outlook. Real pages are unchanged.

## 0.12.5

- No task step. On the inbox page, Sum up the thread and Reply with Claude are the strong buttons.

## 0.12.4

- No task step. The inbox page sums up a thread on the quick model; sorting and drafting stay on default.

## 0.12.3

- No task step. The Claude button that copies a briefing reads "Think it through with Claude" (« Réfléchir avec
  Claude »), on every page; Prepare and Decide keep theirs.

## 0.12.2

- No task step. Mark as read waits 5 seconds in place with Undo before anything reaches the mailbox; the toast is gone.

## 0.12.1

- No task step. Mark as read has a tooltip on its check, and a short toast once done.

## 0.12.0

- `inbox`: the next run publishes the Priority inbox even when nothing arrived since the last run, so the page gets
  `live.mail.read` and the `unlabel_thread` tool where the mail connection is the Gmail connector.
- On the inbox page, a line of the rest or of a label opens under itself the same actions as a queue line: sum up,
  reply, mark as read, open. Mark as read is the exec's own click, mail only, on the Gmail connector; a check on
  hover does it too.

## 0.11.6

- No task step. On the inbox page, a line's actions sit on their own line as light buttons; its sources stay links.

## 0.11.5

- No task step. Under a thread's summary, Reply with Claude comes first, then the link to the thread.

## 0.11.4

- No task step. On the French inbox page, a thread is an « échange »: « Résumer l’échange ».

## 0.11.3

- No task step. The inbox page has a demo mode, for showing it without any connection: `design/demo/`.

## 0.11.2

- No task step. The live inbox's banner carries a refresh arrow: it reads the inboxes again and sorts what is new.

## 0.11.1

- No task step. When the live inbox's sort fails, its banner says why and offers to try again.

## 0.11.0

- `inbox`: the next run publishes the Priority inbox even when nothing arrived since the last run, so the page
  moves to the live template: the `live` block, `generated`, `seen`, and `kind` and `live` on every line, as the
  inbox skill's section 5 says, published with the capabilities it lists. No task prompt changes.
- The page itself now reads mail and chat when the exec opens it in Claude, sorts what arrived since the run,
  files under the exec's rules, and summarises a thread or drafts a reply on request. It asks the exec once to
  use their connections and Claude. Where the mail connection is one it cannot read, it is the page the run
  published. The pre-0.11.0 inbox is kept in `archive/inbox-static-0.10.0/`.

## 0.10.0

- No task step: the skills and the store carry it. Install proposes three fixed labels, Read later, Receipts
  ("Factures" in French) and To archive, and four work labels. Receipts files invoices, payment receipts, order
  and delivery confirmations; anything carrying an amount, an order reference or an attachment never goes to
  To archive. Installs already done keep their rules, in the exec's words; `exec-productivity-help` adds
  Receipts on the exec's word.

## 0.9.1

- No task step: the skills and the store carry it. Each mailbox's main inbox is checked on every run: Gmail's
  Primary while it returns mail, else the inbox without Promotions, Social, Updates and Forums (Gmail with tabs
  turned off has an empty Primary); Outlook's Focused inbox, else the inbox without Other. The form per mailbox
  is kept in `connections/current.roles.mail.main`.

## 0.9.0

- No task step. Install reads the exec's rhythm (first meeting, mail peaks, end of day) and sets the three
  habits' times from it, defaults when there is not enough to read; installs already done keep their times.
  Install also proposes up to five key people, whom the inbox never cuts when the page is full, and asks one
  question, a task to take off the exec's hands, recorded as an ask the review ranks first. Without
  `key_people` the inbox behaves as before.

## 0.8.0

- No task step. A new skill, `exec-productivity-update`, does the update: the plugin's own card (Manage, then
  Update), then the habits and pages brought up to date; help hands over to it. The Daily brief's footer says
  when a newer version is published, where the morning run can read the published manifest.
- No task step: the pages pick it up on their next publish. The Claude button says what it does: Prepare with
  Claude on a meeting, Decide with Claude on a call, Continue with Claude elsewhere. Every briefing hands over
  what the pages found as a starting point, never the frame; a meeting's asks Claude to look with fresh eyes
  and ends asking where to go deeper.

## 0.7.0

- **morning**: update this task's prompt to `task-morning.md`, filled as above, keeping what the exec added to
  it (help's rule): step 3's labels are no longer undone by a "label nothing" further down, and the brief goes by
  email where `notify.brief` lists `email`.
- No step for **inbox** or **review**. The install now picks up a setup that stopped, reminds the exec in the
  same conversation, and asks one question more, the brief by email: none of it touches a running setup.
- **review**: no step, the skill carries it. Before proposing, the review takes stock of what the exec already
  has (every scheduled task, their skills and plugins) and never proposes what is in place; it writes the stock
  to `connections/in_place` when it can list the tasks, and holds a routine or a skill as `found` while no stock
  exists.

## 0.6.2

- No task step: the skills and the checker carry it. A notice only for a channel not read, two at most; a `sub`
  of twenty words at most; twelve inbox lines at most; a bounce is a line.

## 0.6.1

- **morning**, **inbox**: update this task's prompt to its reference file, `task-morning.md` or `task-inbox.md`,
  filled as above. Installs from before 0.2.4 lack the clock check.
- **review**: a task still named `Aureol weekly`, on Fridays, becomes `Aureol review`, weekdays at
  `connections/preferences.review` (17:30 by default), with the 0.6.0 prompt.

## 0.6.0

- **review**: update this task's own prompt to `skills/make-me-productive/references/task-review.md`, filled
  as above, with the session's task tool. This run already follows that prompt, whatever prompt it started
  with: each use case with its prompt, what to attach and the connections.
