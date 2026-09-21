---
name: help
description: The assistant explaining and fixing itself from its own store and files. Use when the exec asks why there was no brief, what the assistant knows, how to change a time or a priority or a rule, how to add or remove a connection, how to update the assistant, how to stop it, or what to do when a page looks wrong. Reads the store and the last runs before answering; fixes what it can in the session; never re-runs install on a live store.
---

# Help

Fewest words. Read before answering. Fix before explaining. Same voice as install: the assistant, its habits,
its connections; no plugin, skill, task, connector or artifact in the exec's half.

## Where the answer is

| The exec says | Read | Then |
|---|---|---|
| No brief this morning | the last `runs` with `task: morning`; the scheduled tasks list; `connections/current` | A run failed: say what failed in one line, re-run the aureol-brief skill now, hand the link. No task: recreate it from `../make-me-productive/references/task-morning.md` (install step 8, that step only). A connection failed: one connector card. |
| The page is wrong about X | the store document behind X, its `sources` | Say where it came from with the source, and fix the document with `if_version`. A person's `cares_about` correction is written with `yours: true` and the date. |
| Change the morning time, the inbox times | `connections/preferences` | Update the task's schedule with the task tools and the preference. One line back. |
| Change my priorities | `priorities` | Point at the page's Edit button. Or take it on the question tool, keep, reword, drop, ahead of what, and write the store; a dropped one gets a proposed decision. |
| Change a label rule, add or remove a label | `rules`, `connections/current.roles.mail.can` | Question tool, then write `rules`. Without `label` in `can`: one line, the mailbox cannot take labels. |
| Add a connection, add a notetaker | `connections/current` | One card (`search_mcp_registry`, `suggest_connectors`), then re-probe with a real call and write `connections/current`. |
| What do you know about my work | `context/summary` | The Super Context link and three lines. |
| Update the assistant | nothing | The plugin card's menu, Check for updates, keep Sync automatically on. If the update changed a habit's prompt (the release note says so), delete the three tasks and recreate them from the reference files. |
| Stop everything | the scheduled tasks | Delete the three tasks. The pages stay; say so. To remove the pages too, the exec deletes them from their pages list. |
| Is it reading my mail | `connections/current`, the register entry | The register entry `../make-me-productive/references/register-fr.md`, filled, in one message. |

## Who fixes what

1. A question the assistant asked on a page is not a fault. Answer it there.
2. A run that failed leaves a "Technical note" at the end of its message with what failed. Paste it here and
   say "fix this": with the same connections, do it now.
3. The habit itself is wrong (a bad question, a skipped step, a false line): that is a change to the assistant.
   Describe what happened; the fix lands as a new version.

Never run install on a live store. Never write a priority the exec did not say. Never guess a cause: read the
run first.
