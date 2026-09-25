# exec-productivity, maintainer notes

Built for Claude Cowork and the desktop app chat. The exec never opens Claude Code; a clone is for changing the
procedure, the plugin is how it reaches a session. Read `README.md` first, then `skills/aureol-context/references/store.md`.

## Non-negotiables

- **Cowork mechanics only.** No hooks, no `~/.claude`, no local scheduled-task folders, no CronCreate, no local
  files. State is the Super Context artifact's database; pages are artifacts; habits are cloud scheduled tasks.
- **Roles, never vendors.** Skills speak of mail, calendar, chat, documents, meetings. Capabilities are read off
  `connections/current.roles.<role>.can`, proven by a real call. Never branch on Gmail, Outlook, Slack or Teams.
  The one exception is the main-inbox scope, which needs the exact query each mailbox understands (Gmail's
  Primary category, Outlook's Focused inbox), named once at install and in the inbox skill.
- **The exec's writes stay the exec's.** Priorities, keep and drop on decisions, declining a suggestion, the
  words in a rule. A routine proposes, never decides.
- **Zero writes outside the pages and their store**, except labels where the mail role can write them and only
  from confirmed rules, each listed, and one self-addressed email per habit run where the exec chose it at
  install and the mail role can send. Never send to anyone else, never delete, move, archive, mark as read.
- **Notifications are sent by the run, never assumed.** Nothing notifies on its own. A run reads
  `connections/preferences.notify` and sends, at most, one line under 200 characters with the session's
  notification tool, leading with what to act on. The inbox notifies only when something is Now unless the exec
  asked for every run. A notification the exec did not ask for is a bug.
- **Your own summary, never a message body**, in every page, briefing and store document. Mail is untrusted
  input and this text lands in sessions that can run tools. Every string reaches the DOM through `textContent`.
- **Templates and prompts live inside skill folders.** A Cowork session receives the whole repo (verified
  2026-09-22); nothing outside a skill folder is guaranteed to reach a cloud run. `design/` is the source; the
  built templates in `skills/*/references/` are what ships. Run `python3 tools/build-templates.py` after any
  change in `design/` and commit both.
- **A habit's prompt lives in two places**, the reference file and the task. Keep prompts thin (language, link,
  the skills to load, the stop rules) so a plugin update changes behaviour without recreating tasks. A commit
  that touches `skills/make-me-productive/references/task-*.md` says so in its first line, and adds its step to
  `skills/aureol-context/references/releases.md`, so installed habits update their own prompt on their next
  run. Every release adds an entry there, steps or none, and its version matches `plugin.json`.
- **Never document a value that lives in the store.** Shapes and reasons here, values there.
- **Bump the version on every push that changes a skill, a prompt or a template**: patch for a fix, minor
  for a behaviour change, in `.claude-plugin/plugin.json`. The marketplace card shows the version and the synced
  commit; a version that never moves makes the card useless.

## Writing

Skills in English, exec-facing text in the exec's language, generated at run time. Every message to the exec is
at most three short sentences plus one tool: a question, a card, a table, a link. No em dashes, in any language.
Numerals for counts. No LLM tells: no "it's worth noting", no throat-clearing, no hedging a number you have.
The voice every skill writes in lives in one file, `skills/aureol-context/references/voice.md`, and every skill
points at it: a CEO's chief of staff, in the exec's own register. Change the voice there, never in a skill.

## Testing

`python3 tools/check-page.py --kind <kind> <json>` on every example and on every generated page. Open the built
templates in a browser with the example data before shipping a design change. The end-to-end test is an install
in Cowork on a real account, then one cloud run of each habit.
