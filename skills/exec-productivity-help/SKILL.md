---
name: exec-productivity-help
description: The assistant explaining and fixing itself from its own store and files. Use when the exec asks why there was no brief, what the assistant knows, how to change a time or a priority or a rule, how to add or remove a connection, how to update the assistant (it hands over to `exec-productivity-update`), how to stop it, or what to do when a page looks wrong. Reads the store and the last runs before answering; fixes what it can in the session; never re-runs install on a live store.
---

# Help

Fewest words. Read before answering. Fix before explaining. The voice is `../aureol-context/references/voice.md`,
the same as install: the assistant, its habits, its connections; no plugin, skill, task, connector or artifact
in the exec's half.

Whenever this session lists the scheduled tasks, for any row below, it also takes stock for the review: every
task with its schedule and what its prompt produces, and the skills and plugins this session lists, written to
`connections/in_place` with `checked` today. A cloud run cannot list tasks; this is how the review learns what
is already in place.

## Where the answer is

| The exec says | Read | Then |
|---|---|---|
| No brief this morning | the last `runs` with `task: morning`; the scheduled tasks list; `connections/current` | A run failed: say what failed in one line, re-run the aureol-brief skill now, hand the link. No task: recreate it from `../make-me-productive/references/task-morning.md` (install step 7, that step only). A connection failed: one connector card. |
| The page is wrong about X | the store document behind X, its `sources` | Say where it came from with the source, and fix the document with `if_version`. A person's `cares_about` correction is written with `yours: true` and the date. |
| Change the morning time, the inbox times | `connections/preferences` | Update the task's schedule with the task tools and the preference, in local time, one task per habit; an inbox rhythm must share one minute value (11:00, 13:00, 15:00, 17:00), else move it to the nearest that does and say so. If two inbox tasks exist, delete the extra one. Write `rhythm.source` as `yours`. One line back. |
| Change my key people (add, remove, reorder) | `connections/preferences.key_people`, `people` | Write the refs in their order, five at most; their lines are never cut from the inbox page. One line back. |
| The inbox page asks to use my connections, or does not refresh on its own | the inbox page's data (`live`), `connections/current.roles` | The page reads mail and chat live only when opened in Claude and allowed once, on the page; it reads Aureol Connect, the Gmail connector and Slack. Any other mail tool: the page is what the last run published, and that is expected. A page still on the pre-0.11.0 template moves at the next inbox run. What the sort knows about them is rebuilt each run; their own additions are typed on the page, under the link at the bottom. One line back. |
| Bring back a line I put lower, or put one back up | the inbox page's store, `priority` | On the page: Prioritise on the line in the rest (or the arrow on hover), Lower priority on a queue line. A line marked lower comes back by itself when a new message arrives. To clear one by hand, delete its `priority/<slug>` document in the inbox page's store. One line back. |
| Change my priorities | `priorities` | Point at the page's Edit button. Or take it on the question tool, keep, reword, drop, ahead of what, and write the store; a dropped one gets a proposed decision. |
| Change a label rule, add or remove a label | `rules`, `connections/current.roles.mail.can` | Question tool, then write `rules`. Without `label` in `can`: one line, the mailbox cannot take labels. |
| Change how I am told (more, less, by email, never) | `connections/preferences.notify`, `connections/current.roles.mail.can` | Question tool, one habit at a time: `push` (a notification each run; the review only on a day it found something), `push_now` (inbox only, when something is urgent), `email` (only where the mail role can send, to their own address; for the brief, the page itself, alone or with the notification: `["push", "email"]`), `none`. A list needs this version's morning prompt: if `releases.md` still owes the morning task a prompt update, do it first. Write it; one line back. |
| Stop the web lookups, or turn them back on | `connections/preferences.enrich` | One line, write `none` or `public`. |
| Reopen a closed topic | `topics/<id>` | Set `live: true`, clear `closed_reason`, one `so_far` line "reopened by you", republish. |
| Add a connection, add a notetaker | `connections/current` | One card (`search_mcp_registry`, `suggest_connectors`), then re-probe with a real call and write `connections/current`. |
| Read another calendar | `connections/current.roles.calendar` | List the calendars the tool reaches; add the one the exec names to `calendars`, the first one kept; probe each with a real call. One line back. |
| Finish my setup, the setup stopped | the scheduled tasks; the Super Context and the install's `runs` document | No `Aureol morning` task: load `make-me-productive`, which picks up where the setup stopped. The task exists: nothing to finish, say so in one line. |
| What do you know about my work | `context/summary` | The Super Context link and three lines. |
| Update the assistant, or bring my setup up to date | nothing | Load the `exec-productivity-update` skill; it shows the update, then brings the habits and pages up to date. |
| Stop everything | the scheduled tasks | Delete the three tasks. The pages stay; say so. To remove the pages too, the exec deletes them from their pages list. |
| Is it reading my mail | `connections/current`, the register entry | The register entry `../make-me-productive/references/register-fr.md`, filled, in one message. |

## Who fixes what

1. A question the assistant asked on a page is not a fault. Answer it there.
2. A run that failed wrote what failed in its `runs` document's `note`. Read it, and with the same
   connections, fix it now.
3. The habit itself is wrong (a bad question, a skipped step, a false line): that is a change to the assistant.
   Describe what happened; the fix lands as a new version.

Never run install on a live store. Never write a priority the exec did not say. Never guess a cause: read the
run first.
