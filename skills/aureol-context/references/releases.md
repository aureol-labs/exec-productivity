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
