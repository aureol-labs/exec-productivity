---
name: exec-productivity-update
description: Update the executive's assistant to its newest version, then bring its three habits and pages up to date on it. Shows the plugin's own card to install the update (Manage, then Update), waits for the exec, then updates each habit's prompt, name and schedule as the release notes say, keeping what the exec added, and rebuilds the pages. Use when the exec asks to update the assistant, when the Daily brief says a new version is ready, or after the exec clicked Update.
---

# Update

Fewest words, same voice as help (`../aureol-context/references/voice.md`): the assistant, its habits; no
plugin, skill, task or artifact in the exec's half, except the card and its two buttons.

Two versions matter. **Installed**: the newest heading of `../aureol-context/references/releases.md`, the files
this conversation runs. **Published**: the `version` in
`https://raw.githubusercontent.com/aureol-labs/exec-productivity/main/.claude-plugin/plugin.json`, read with the
session's web fetch. Write both to `connections/current.plugin` with `checked` today. Without web fetch, the
published version is unknown.

## 1. The update itself

Published newer than installed, or unknown, and the exec has not just said they updated:

1. Find the plugin with the session's plugin list tool (name `exec-productivity`) and show its own card with the
   plugin card tool, its id from that list. One line: "Manage, then Update, and tell me when it is done." Wait
   for their word. Without those tools, one line instead: Customize, Plugins, exec-productivity, Update.
2. On their word, read the installed version again. It now matches the published one: go on to step 2. It does
   not: a conversation keeps the files it opened with, so one line, "Open a new conversation and type
   /exec-productivity:exec-productivity-update, I finish there," and stop.

Published equal to installed: straight to step 2.

## 2. The habits and the pages

For each of the three habits, the steps `../aureol-context/references/releases.md` owes it, read against the
`version` on that task's last `runs` document:

- Update the task's prompt from its reference file in `../make-me-productive/references/`, placeholders filled
  from the store. What the exec added to the old prompt stays theirs: a paragraph the reference never had (a
  second calendar, an email they asked for, a step of their own) becomes the setting this version has for it
  (`connections/current.roles.calendar.calendars`, `notify.brief` with `email`) or is kept word for word at the
  end of the new prompt, and the line back names it.
- Its name and schedule as install step 7 sets them, keeping the times in `connections/preferences`.

List the scheduled tasks once for this, and take stock for the review as help does (`connections/in_place`).
Write `plugin_version` in `connections/preferences`. Then run the morning task now so the three pages rebuild on
this version.

One line back: what changed for the exec, in their words, from the release notes they skipped; never a version
number unless they ask. Nothing owed and nothing newer: "Your assistant is up to date."
