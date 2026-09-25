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

## 0.6.1

- **morning**, **inbox**: update this task's prompt to its reference file, `task-morning.md` or `task-inbox.md`,
  filled as above. Installs from before 0.2.4 lack the clock check.
- **review**: a task still named `Aureol weekly`, on Fridays, becomes `Aureol review`, weekdays at
  `connections/preferences.review` (17:30 by default), with the 0.6.0 prompt.

## 0.6.0

- **review**: update this task's own prompt to `skills/make-me-productive/references/task-review.md`, filled
  as above, with the session's task tool. This run already follows that prompt, whatever prompt it started
  with: each use case with its prompt, what to attach and the connections.
