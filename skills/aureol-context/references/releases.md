# Releases

What an installed assistant does when the plugin moves on. Skills, templates and this file reach every run on
their own. A scheduled task keeps the prompt it was created with, and a page keeps its last publish until its
next run, so a release that changes either says here what each habit does about it.

Every habit reads this file before anything else in its run. The newest entry is the plugin's version. When it
is newer than the `version` on this task's last `runs` document, or that document has none, apply the steps of
every newer entry that name this task, oldest first, then do the run, and write the newest version in this run's
`runs` document. A step the run cannot do (no task tool, a tool that refuses) goes in the run's `note`, and
`exec-productivity-help` does it on the exec's next question. Never tell the exec about a step; the pages show
what changed.

Tasks are named as the store names them: `morning`, `inbox`, `review`. Placeholders in a reference prompt are
filled from the store: `{{LANGUAGE}}`, `{{FIRST_NAME}}` and `{{TIMEZONE}}` from `connections/preferences`,
`{{CONTEXT_URL}}` from `connections/current.pages.context`, `{{RUN_TIME}}` from the habit's times in
`connections/preferences`.

## 0.6.0

- **review**: update this task's own prompt to `skills/make-me-productive/references/task-review.md`, filled
  as above, with the session's task tool. This run already follows that prompt, whatever prompt it started
  with: each use case with its prompt, what to attach and the connections.
