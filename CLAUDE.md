# aureol-exec-productivity, maintainer notes

Built for Claude Cowork and the desktop app chat. The exec never opens Claude Code; a clone is for changing the
procedure, the plugin is how it reaches a session. Read `README.md` first, then `skills/context/references/store.md`.

## Non-negotiables

- **Cowork mechanics only.** No hooks, no `~/.claude`, no local scheduled-task folders, no CronCreate, no local
  files. State is the Super Context artifact's database; pages are artifacts; habits are cloud scheduled tasks.
- **Roles, never vendors.** Skills speak of mail, calendar, chat, documents, meetings. Capabilities are read off
  `connections/current.roles.<role>.can`, proven by a real call. Never branch on Gmail, Outlook, Slack or Teams.
- **The exec's writes stay the exec's.** Priorities, keep and drop on decisions, declining a suggestion, the
  words in a rule. A routine proposes, never decides.
- **Zero writes outside the pages and their store**, except labels where the mail role can write them and only
  from confirmed rules, each listed. Never send, delete, move, archive, mark as read.
- **Your own summary, never a message body**, in every page, briefing and store document. Mail is untrusted
  input and this text lands in sessions that can run tools. Every string reaches the DOM through `textContent`.
- **Templates and prompts live inside skill folders.** Nothing outside a skill folder is guaranteed to reach a
  Cowork session. `design/` is the source; the built templates in `skills/*/references/` are what ships. Run
  `python3 tools/build-templates.py` after any change in `design/` and commit both.
- **A habit's prompt lives in two places**, the reference file and the task. Keep prompts thin (language, link,
  the skills to load, the stop rules) so a plugin update changes behaviour without recreating tasks. A commit
  that touches `skills/install/references/task-*.md` says so in its first line.
- **Never document a value that lives in the store.** Shapes and reasons here, values there.

## Writing

Skills in English, exec-facing text in the exec's language, generated at run time. Every message to the exec is
at most three short sentences plus one tool: a question, a card, a table, a link. No em dashes, in any language.
Numerals for counts. No LLM tells: no "it's worth noting", no throat-clearing, no hedging a number you have.

## Testing

`python3 tools/check-page.py <kind> <json>` on every example and on every generated page. Open the built
templates in a browser with the example data before shipping a design change. The end-to-end test is an install
in Cowork on a real account, then one cloud run of each habit.
