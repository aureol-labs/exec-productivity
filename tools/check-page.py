#!/usr/bin/env python3
"""Check a page document before it is rendered.

    check-page.py --kind brief|inbox|context PATH [--brief X.json] [--inbox Y.json] [--context Z.json]
    check-page.py --selftest

PATH is the page JSON, or a built page (HTML) whose {{DATA_JSON}} has been filled. The
optional --brief/--inbox/--context paths are the other pages' JSON, used to resolve
cross-page references. Exits non-zero with one line per violation. Standard library only.

--selftest loads the three example fixtures next to the templates, asserts they pass, then
breaks copies of them in memory one rule at a time and asserts each break is caught.
"""
import argparse
import copy
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EXAMPLES = {
    'brief': os.path.join(ROOT, 'skills', 'brief', 'references', 'example.json'),
    'inbox': os.path.join(ROOT, 'skills', 'inbox', 'references', 'example.json'),
    'context': os.path.join(ROOT, 'skills', 'context', 'references', 'example.json'),
}

EM_DASH = '—'
TYPES = {'precedent', 'knock_on', 'pattern', 'history'}
SRC_KINDS = {'mail', 'chat', 'calendar', 'doc', 'meeting', 'file', 'you'}
TINTS = {'sales', 'product', 'board', 'customers', 'hiring', 'later', 'arch'}
REL_INVERSE = {'contact_for': 'contact', 'contact': 'contact_for', 'member_of': 'member',
               'member': 'member_of', 'leads': 'led_by', 'led_by': 'leads',
               'sits_on': 'seat', 'seat': 'sits_on'}

TIME = re.compile(r'^\d{2}:\d{2}$')
DATE = re.compile(r'^\d{1,2}(er)? [^\W\d_]{3,}\.?$', re.UNICODE)
ISO = re.compile(r'^\d{4}-\d{2}-\d{2}$')

# lateness dressed as arithmetic: "6 days late", "8 days waiting", "no reply in five days",
# "four days, no reply", "6 jours de retard", "n'a pas répondu depuis", "sans réponse depuis"
NUM = r'(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|un|une|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze)'
LATE = [
    re.compile(r'\b' + NUM + r'\s+(?:days?|weeks?|hours?|jours?|semaines?|heures?)\s+(?:late|waiting|overdue|without\s+(?:a\s+)?(?:reply|answer)|de\s+retard|d[’\']attente)\b', re.I),
    re.compile(r'\b' + NUM + r'\s+(?:days?|weeks?|jours?|semaines?)\s*,\s*(?:no|without|sans)\s+(?:reply|answer|response|réponse)', re.I),
    re.compile(r'\b(?:no|without)\s+(?:reply|answer|response)\s+(?:in|for)\s+' + NUM + r'\s+(?:days?|weeks?|hours?)', re.I),
    re.compile(r'\b(?:waiting|waited|blocked)\s+(?:for\s+)?' + NUM + r'\s+(?:days?|weeks?|hours?)', re.I),
    re.compile(r'\b(?:late|overdue|en\s+retard)\s+by\s+' + NUM + r'\s+(?:days?|weeks?|hours?)', re.I),
    re.compile(r'\bn[’\']a\s+pas\s+répondu\s+depuis\b', re.I),
    re.compile(r'\bsans\s+réponse\s+depuis\s+' + NUM + r'\s+(?:jours?|semaines?|heures?)', re.I),
    re.compile(r'\bdepuis\s+' + NUM + r'\s+(?:jours?|semaines?)\s+(?:sans|de\s+retard)', re.I),
    re.compile(r'\bjours?\s+de\s+retard\b', re.I),
]
NUMBER_WORDS = re.compile(r'\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|treize|quatorze|quinze|seize|vingt)\b', re.I)


class Report:
    def __init__(self):
        self.lines = []

    def bad(self, where, what):
        self.lines.append('%s: %s' % (where, what))

    def ok(self):
        return not self.lines


# ---------- walking ----------

def walk_strings(node, path='$'):
    """Yield (path, string) for every string in a JSON tree."""
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield from walk_strings(v, path + '.' + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_strings(v, '%s[%d]' % (path, i))


def walk_items(node, path='$'):
    """Yield (path, dict) for every object in a JSON tree."""
    if isinstance(node, dict):
        yield path, node
        for k, v in node.items():
            yield from walk_items(v, path + '.' + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_items(v, '%s[%d]' % (path, i))


# ---------- common rules ----------

def check_common(d, r, kind):
    for path, s in walk_strings(d):
        if EM_DASH in s:
            r.bad(path, 'em dash')
        for rx in LATE:
            m = rx.search(s)
            if m:
                r.bad(path, 'lateness arithmetic: "%s"' % m.group(0))
                break
    for key in ('date_label', 'time_label', 'today', 'sub'):
        if not d.get(key):
            r.bad('$.' + key, 'missing')
    if d.get('today') and not ISO.match(str(d['today'])):
        r.bad('$.today', 'not an ISO date')
    if d.get('lang') not in ('en', 'fr'):
        r.bad('$.lang', 'must be "en" or "fr"')
    if d.get('gesture', 'copy') not in ('copy', 'link'):
        r.bad('$.gesture', 'must be "copy" or "link"')
    links = d.get('links') or {}
    for k, v in links.items():
        if v and not str(v).startswith('https://'):
            r.bad('$.links.' + k, 'not an https:// link')
    for path, it in walk_items(d):
        src = it.get('sources')
        if isinstance(src, list):
            if len(src) > 3:
                r.bad(path + '.sources', '%d sources, 3 at most' % len(src))
            for i, s in enumerate(src):
                if not isinstance(s, dict):
                    r.bad('%s.sources[%d]' % (path, i), 'not an object')
                    continue
                if s.get('kind') not in SRC_KINDS:
                    r.bad('%s.sources[%d].kind' % (path, i), 'unknown kind %r' % s.get('kind'))
                h = s.get('href') or ''
                if h and not re.match(r'^(https://|mailto:|#)', h):
                    r.bad('%s.sources[%d].href' % (path, i), 'href must start with https://, mailto: or #')
        go = it.get('go')
        if isinstance(go, list):
            for i, g in enumerate(go):
                if not isinstance(g, dict) or not g.get('id') or not g.get('text'):
                    r.bad('%s.go[%d]' % (path, i), 'a cross-reference carries an id and its substance as text')
    for i, s in enumerate(d.get('footer') or []):
        if isinstance(s, str) and NUMBER_WORDS.search(s):
            r.bad('$.footer[%d]' % i, 'a count spelled out: "%s"' % NUMBER_WORDS.search(s).group(0))


def ids_of(d, kind):
    ids = []
    if kind == 'brief':
        for m in (d.get('strip') or {}).get('meetings') or []:
            ids.append(m.get('id'))
        for row in (d.get('decisions') or []) + (d.get('jobs') or []):
            ids.append(row.get('id'))
    elif kind == 'inbox':
        for row in (d.get('queue') or []) + (d.get('filed') or []) + (d.get('grouped') or []):
            ids.append(row.get('id'))
    elif kind == 'context':
        for key in ('priorities', 'topics', 'entities', 'decisions', 'suggestions'):
            for row in d.get(key) or []:
                ids.append(row.get('id'))
    return [i for i in ids if i]


def check_ids(d, r, kind):
    ids = ids_of(d, kind)
    seen = set()
    for i in ids:
        if i in seen:
            r.bad('$', 'duplicate id %r' % i)
        seen.add(i)
    return seen


def check_refs(d, r, kind, own_ids, others):
    """Every same-page reference names a row on this page; every cross-page one names a
    row on that page's data, when that data is given."""
    def one(path, g):
        page = g.get('page')
        if page:
            if page == kind:
                r.bad(path, 'a cross-page reference to this page')
            elif page in others:
                if g.get('id') not in others[page]:
                    r.bad(path, 'no row %r on the %s page' % (g.get('id'), page))
            elif page not in ('brief', 'inbox', 'context'):
                r.bad(path, 'unknown page %r' % page)
        elif g.get('id') not in own_ids:
            r.bad(path, 'no row %r on this page' % g.get('id'))
    for path, it in walk_items(d):
        for i, g in enumerate(it.get('go') or []):
            if isinstance(g, dict):
                one('%s.go[%d]' % (path, i), g)
        for key in ('to_land', 'in_mind'):
            v = it.get(key)
            if isinstance(v, dict) and isinstance(v.get('go'), dict):
                one('%s.%s.go' % (path, key), v['go'])


def check_meta(path, meta, r, allowed):
    if meta is None:
        return
    if not isinstance(meta, dict) or meta.get('kind') not in allowed:
        r.bad(path, 'right column kind must be one of %s' % sorted(allowed))
        return
    k, v = meta.get('kind'), meta.get('value')
    if k == 'none':
        return
    v = '' if v is None else str(v)
    if k in ('time', 'before') and not TIME.match(v):
        r.bad(path, 'a %s needs HH:MM, got %r' % (k, v))
    elif k in ('asked', 'date') and not (DATE.match(v) or TIME.match(v)):
        r.bad(path, 'a %s needs a date like "3 Sept" or HH:MM, got %r' % (k, v))
    elif k == 'late' and not (TIME.match(v) or DATE.match(v)):
        r.bad(path, 'late needs HH:MM or a date, got %r' % v)


def row_types(rows, path, r, decision_ids=None):
    for i, row in enumerate(rows):
        p = '%s[%d]' % (path, i)
        if row.get('type') not in TYPES:
            r.bad(p, 'untyped row (%r); the routine types the line or leaves it off' % row.get('type'))
        if not row.get('say'):
            r.bad(p, 'no sentence')
        if not row.get('lede'):
            r.bad(p, 'no lede: every reveal opens on the ask')


# ---------- the brief ----------

def check_brief(d, r, others):
    own = check_ids(d, r, 'brief')
    caps = d.get('caps') or {}
    dec, jobs = d.get('decisions') or [], d.get('jobs') or []
    for key, rows in (('decisions', dec), ('jobs', jobs)):
        cap = caps.get(key)
        if not isinstance(cap, int):
            r.bad('$.caps.' + key, 'missing or not a numeral')
        elif len(rows) > cap:
            r.bad('$.' + key, '%d rows, cap is %d' % (len(rows), cap))
        row_types(rows, '$.' + key, r)
        for i, row in enumerate(rows):
            p = '$.%s[%d]' % (key, i)
            check_meta(p + '.meta', row.get('meta'), r, {'time', 'before', 'asked', 'late', 'none'})
            meta = row.get('meta') or {}
            if meta.get('kind') == 'late':
                has_you = any(s.get('kind') == 'you' for s in row.get('sources') or [] if isinstance(s, dict))
                has_dec = any(isinstance(g, dict) and g.get('page') == 'context' and str(g.get('id', '')).startswith('d')
                              for g in row.get('go') or [])
                if not (has_you or has_dec):
                    r.bad(p + '.meta', 'late without a "you" source or a decision reference')
    strip = d.get('strip') or {}
    meetings = strip.get('meetings') or []
    start, end = strip.get('start', '08:00'), strip.get('end', '18:00')
    if not (TIME.match(str(start)) and TIME.match(str(end))):
        r.bad('$.strip', 'start and end must be HH:MM')
    times = []
    for i, m in enumerate(meetings):
        p = '$.strip.meetings[%d]' % i
        if m.get('clash'):
            inner = m.get('meetings') or []
            if len(inner) < 2:
                r.bad(p, 'a clash needs at least two meetings')
            for j, x in enumerate(inner):
                if not (TIME.match(str(x.get('start', ''))) and TIME.match(str(x.get('end', '')))):
                    r.bad('%s.meetings[%d]' % (p, j), 'start and end must be HH:MM')
                if not x.get('cost'):
                    r.bad('%s.meetings[%d]' % (p, j), 'each column of a clash ends on what it costs to move that one')
            if not m.get('briefing') and not m.get('sources'):
                r.bad(p, 'a clash brief has sources')
        else:
            if not (TIME.match(str(m.get('start', ''))) and TIME.match(str(m.get('end', '')))):
                r.bad(p, 'start and end must be HH:MM')
            if not m.get('label'):
                r.bad(p, 'a block is labelled with its time and a word')
            br = m.get('brief') or {}
            for key in ('who', 'before'):
                if not br.get(key):
                    r.bad(p + '.brief.' + key, 'missing')
            if not br.get('to_land') or not br.get('in_mind'):
                r.bad(p + '.brief', 'a brief carries WHO, BEFORE, TO LAND and IN MIND')
        times.append(m.get('start'))
    mx = d.get('metrics')
    if mx is not None:
        if not isinstance(mx, dict) or not isinstance(mx.get('tiles'), list) or not mx.get('source'):
            r.bad('$.metrics', 'metrics carry tiles and a one-line source, or are null')
        else:
            for i, tl in enumerate(mx['tiles']):
                if not re.search(r'\d', str(tl.get('value', ''))):
                    r.bad('$.metrics.tiles[%d]' % i, 'a tile is a numeral')
    check_refs(d, r, 'brief', own, others)
    return own


# ---------- the inbox ----------

def check_inbox(d, r, others):
    own = check_ids(d, r, 'inbox')
    counts = d.get('counts') or {}
    for k in ('mail', 'chat'):
        if not isinstance(counts.get(k), int):
            r.bad('$.counts.' + k, 'missing or not a numeral')
    q = d.get('queue') or []
    row_types(q, '$.queue', r)
    total = (counts.get('mail') or 0) + (counts.get('chat') or 0)
    if len(q) > total:
        r.bad('$.queue', '%d rows need you out of %d unread' % (len(q), total))
    order = {'now': 0, 'today': 1, 'week': 2}
    last = -1
    for i, row in enumerate(q):
        p = '$.queue[%d]' % i
        if row.get('tier') not in order:
            r.bad(p + '.tier', 'tier must be now, today or week')
        else:
            if order[row['tier']] < last:
                r.bad(p + '.tier', 'tiers run Now, then Today, then This week')
            last = order[row['tier']]
        if row.get('channel') not in ('mail', 'slack', 'teams'):
            r.bad(p + '.channel', 'channel must be mail, slack or teams')
        check_meta(p + '.meta', row.get('meta'), r, {'time', 'date'})
        if row.get('meta') is None:
            r.bad(p + '.meta', 'the right column is when it arrived')
        lb = row.get('label')
        if lb is not None and (not isinstance(lb, dict) or not lb.get('name')):
            r.bad(p + '.label', 'a label carries a name and a tint')
    filed, grouped = d.get('filed') or [], d.get('grouped') or []
    wrote = d.get('wrote')
    if filed and not wrote:
        r.bad('$.wrote', 'labels shown as written, but wrote is not true')
    if not filed and wrote:
        r.bad('$.wrote', 'wrote is true but nothing is filed')
    for key, rows, with_rule in (('filed', filed, True), ('grouped', grouped, False)):
        for i, f in enumerate(rows):
            p = '$.%s[%d]' % (key, i)
            if not isinstance(f.get('count'), int):
                r.bad(p + '.count', 'a tally is a numeral')
            bc = f.get('by_channel') or {}
            if bc and isinstance(f.get('count'), int) and sum(v for v in bc.values() if isinstance(v, int)) != f['count']:
                r.bad(p + '.by_channel', 'the per-channel counts do not add up to the count')
            if f.get('tint') not in TINTS:
                r.bad(p + '.tint', 'tint must be one of %s' % sorted(TINTS))
            if not f.get('label'):
                r.bad(p + '.label', 'missing')
            if not f.get('lede'):
                r.bad(p + '.lede', 'every reveal opens on the ask')
            items = f.get('contents') or []
            if isinstance(f.get('count'), int):
                want = min(5, f['count'])
                if len(items) > 5 or len(items) < min(3, want):
                    r.bad(p + '.contents', '3 to 5 lines, got %d' % len(items))
            for j, x in enumerate(items):
                if x.get('channel') not in ('mail', 'slack', 'teams'):
                    r.bad('%s.contents[%d].channel' % (p, j), 'channel must be mail, slack or teams')
                if not x.get('from') or not x.get('what'):
                    r.bad('%s.contents[%d]' % (p, j), 'every line names who and what')
            if with_rule:
                if f.get('tint') == 'arch':
                    rules = f.get('rules') or []
                    if not rules:
                        r.bad(p + '.rules', 'To archive carries the rules that filed it')
                    n = sum(x.get('count', 0) for x in rules if isinstance(x.get('count'), int))
                    if n != f.get('count'):
                        r.bad(p + '.rules', 'the rule counts do not add up to the count')
                    briefing = f.get('briefing') or ''
                    for x in rules:
                        if x.get('rule') and x['rule'] not in briefing:
                            r.bad(p + '.briefing', 'the briefing does not list the rule "%s"' % x['rule'])
                elif not f.get('rule'):
                    r.bad(p + '.rule', 'every filed label carries the rule that made it, in the exec\'s words')
            else:
                if f.get('rule') or f.get('rules'):
                    r.bad(p, 'a group carries no rule: nothing was written')
    if d.get('next_run') is not None and not TIME.match(str(d['next_run'])):
        r.bad('$.next_run', 'HH:MM')
    check_refs(d, r, 'inbox', own, others)
    return own


# ---------- super context ----------

def check_context(d, r, others):
    own = check_ids(d, r, 'context')
    pri = d.get('priorities') or []
    topics = d.get('topics') or []
    ents = d.get('entities') or []
    decs = d.get('decisions') or []
    sugg = d.get('suggestions') or []
    if len(pri) > 5:
        r.bad('$.priorities', '%d priorities, 5 at most' % len(pri))
    names = {t.get('name') for t in topics} | {e.get('name') for e in ents}
    shorts = set()
    for i, p in enumerate(pri):
        pp = '$.priorities[%d]' % i
        for key in ('say', 'ahead', 'short'):
            if not p.get(key):
                r.bad(pp + '.' + key, 'missing: a priority says what it comes before, and has a short name')
        if p.get('short') in names:
            r.bad(pp + '.short', '"%s" is also a topic or entity name' % p['short'])
        if p.get('short') in shorts:
            r.bad(pp + '.short', 'duplicate short name')
        shorts.add(p.get('short'))
        if p.get('confirmed') and not DATE.match(str(p['confirmed'])):
            r.bad(pp + '.confirmed', 'a date like "1 Sept"')
        for j, h in enumerate(p.get('history') or []):
            if not DATE.match(str(h.get('date', ''))):
                r.bad('%s.history[%d].date' % (pp, j), 'a date like "1 Jul"')
    pri_ids = {p.get('id') for p in pri}
    tnames = [t.get('name') for t in topics]
    enames = [e.get('name') for e in ents]
    for n in set(tnames) & set(enames):
        r.bad('$.topics', 'topic "%s" shares its name with an entity' % n)
    ent_ids = {e.get('id') for e in ents}
    row_ids = {t.get('id') for t in topics} | ent_ids
    dec_ids = {x.get('id') for x in decs}

    def check_dated(path, items, allow_today=False, allow_late=False):
        for j, x in enumerate(items or []):
            when = x.get('when') or x.get('date') or ''
            if x.get('today') and allow_today:
                if not TIME.match(str(when)):
                    r.bad('%s[%d]' % (path, j), 'a today entry carries HH:MM')
            elif not DATE.match(str(when)):
                r.bad('%s[%d]' % (path, j), 'a date like "3 Sept", got %r' % when)
            if x.get('late'):
                if not allow_late:
                    r.bad('%s[%d]' % (path, j), 'late is only allowed on next')
                elif not (x.get('decision') in dec_ids):
                    r.bad('%s[%d]' % (path, j), 'late needs a decision the routine can point at')

    def check_who(path, items):
        for j, w in enumerate(items or []):
            ref = w.get('ref')
            if ref and ref not in row_ids and ref not in own:
                r.bad('%s[%d].ref' % (path, j), 'no row %r' % ref)
            if not ref and not w.get('name'):
                r.bad('%s[%d]' % (path, j), 'a who line names someone')

    for i, t in enumerate(topics):
        tp = '$.topics[%d]' % i
        for key in ('name', 'state', 'lede'):
            if not t.get(key):
                r.bad(tp + '.' + key, 'missing')
        if t.get('serves') is not None and t['serves'] not in pri_ids:
            r.bad(tp + '.serves', 'no priority %r' % t['serves'])
        if t.get('last') is not None and not DATE.match(str(t['last'])):
            r.bad(tp + '.last', 'a date like "24 Aug", or null for Not yet')
        if t.get('gesture', 'none') not in ('ask', 'add_priority', 'none'):
            r.bad(tp + '.gesture', 'ask, add_priority or none')
        if t.get('gesture') == 'ask' and not t.get('briefing'):
            r.bad(tp + '.briefing', 'Ask Claude needs a briefing')
        check_who(tp + '.who', t.get('who'))
        check_dated(tp + '.so_far', t.get('so_far'))
        check_dated(tp + '.next', t.get('next'), allow_today=True, allow_late=True)
    by_id = {e.get('id'): e for e in ents}
    for i, e in enumerate(ents):
        ep = '$.entities[%d]' % i
        for key in ('name', 'state', 'lede'):
            if not e.get(key):
                r.bad(ep + '.' + key, 'missing')
        if e.get('kind') not in ('person', 'entity'):
            r.bad(ep + '.kind', 'person or entity')
        if e.get('kind') == 'person' and not e.get('role'):
            r.bad(ep + '.role', 'a person has a role, the one every page uses')
        if e.get('kind') == 'entity':
            if e.get('type') not in ('company', 'team', 'board', 'product', 'other'):
                r.bad(ep + '.type', 'company, team, board, product or other')
            if e.get('type') == 'company' and e.get('relationship') not in ('customer', 'prospect', 'investor', 'partner', 'supplier'):
                r.bad(ep + '.relationship', 'customer, prospect, investor, partner or supplier')
            if e.get('type') == 'other' and not e.get('label'):
                r.bad(ep + '.label', 'other carries a label')
        if e.get('last') is not None and not DATE.match(str(e['last'])):
            r.bad(ep + '.last', 'a date like "24 Aug", or null for Not yet')
        ca = e.get('cares_about')
        if isinstance(ca, dict) and ca.get('yours') and not ca.get('date'):
            r.bad(ep + '.cares_about', 'your words carry their date')
        for j, w in enumerate(e.get('with') or []):
            wp = '%s.with[%d]' % (ep, j)
            if w.get('type') not in REL_INVERSE:
                r.bad(wp + '.type', 'one of %s' % sorted(REL_INVERSE))
            other = by_id.get(w.get('ref'))
            if not other:
                r.bad(wp + '.ref', 'no entity %r' % w.get('ref'))
                continue
            mirror = [m for m in other.get('with') or [] if m.get('ref') == e.get('id')]
            if not mirror:
                r.bad(wp, 'relation note "%s" appears on only one side' % w.get('note'))
            else:
                m = mirror[0]
                if m.get('note') != w.get('note'):
                    r.bad(wp, 'the note differs between the two sides: "%s" vs "%s"' % (w.get('note'), m.get('note')))
                if w.get('type') in REL_INVERSE and m.get('type') != REL_INVERSE[w['type']]:
                    r.bad(wp + '.type', 'the other side should read %r' % REL_INVERSE[w['type']])
        check_dated(ep + '.so_far', e.get('so_far'))
        check_dated(ep + '.ended', e.get('ended'))
        check_dated(ep + '.next', e.get('next'), allow_today=True)
    for i, x in enumerate(decs):
        dp = '$.decisions[%d]' % i
        if not x.get('say'):
            r.bad(dp + '.say', 'missing')
        if not x.get('against'):
            r.bad(dp + '.against', 'a decision says what it was decided against, or it was an announcement')
        if not x.get('decided_by'):
            r.bad(dp + '.decided_by', 'who decided it')
        if not DATE.match(str(x.get('when', ''))):
            r.bad(dp + '.when', 'a date like "9 Sept"')
        if not ISO.match(str(x.get('when_iso', ''))):
            r.bad(dp + '.when_iso', 'ISO date for the order')
        if x.get('status') not in ('proposed', 'kept', 'dropped'):
            r.bad(dp + '.status', 'proposed, kept or dropped')
        for key in ('proposed_at', 'kept_at', 'dropped_at'):
            if x.get(key) and not ISO.match(str(x[key])):
                r.bad(dp + '.' + key, 'ISO date')
        if x.get('status') == 'kept' and not x.get('kept_at'):
            r.bad(dp + '.kept_at', 'a kept decision carries kept_at')
        for key in ('replaces', 'replaced_by', 'conflicts_with'):
            rel = x.get(key)
            if rel is None:
                continue
            if not isinstance(rel, dict) or rel.get('id') not in dec_ids or not rel.get('name'):
                r.bad(dp + '.' + key, 'names an existing decision, in words')
                continue
            other = next(y for y in decs if y.get('id') == rel['id'])
            back = {'replaces': 'replaced_by', 'replaced_by': 'replaces', 'conflicts_with': 'conflicts_with'}[key]
            ob = other.get(back)
            if not isinstance(ob, dict) or ob.get('id') != x.get('id'):
                r.bad(dp + '.' + key, 'the other decision does not name this one back')
        if x.get('conflicts_with') and not x.get('land'):
            r.bad(dp + '.land', 'a conflict ends on the open question')
        if x.get('replaces') and x.get('conflicts_with') and x['replaces'].get('id') == x['conflicts_with'].get('id'):
            r.bad(dp, 'a conflict is not a supersede; never both on the same pair')
    if len([s for s in sugg if s.get('status', 'proposed') == 'proposed']) > 3:
        r.bad('$.suggestions', 'three at most')
    for i, s in enumerate(sugg):
        sp = '$.suggestions[%d]' % i
        if s.get('kind') not in ('connection', 'skill'):
            r.bad(sp + '.kind', 'connection or skill')
        if not s.get('say') or not s.get('lede'):
            r.bad(sp, 'a suggestion has a sentence and a lede')
        if not s.get('evidence'):
            r.bad(sp + '.evidence', 'a suggestion carries its evidence')
        if s.get('kind') == 'connection' and not s.get('path'):
            r.bad(sp + '.path', 'a connection carries the settings path sentence')
        if s.get('kind') == 'skill' and not s.get('briefing'):
            r.bad(sp + '.briefing', 'a skill carries the Draft the skill briefing')
    check_refs(d, r, 'context', own, others)
    return own


CHECKS = {'brief': check_brief, 'inbox': check_inbox, 'context': check_context}


# ---------- entry points ----------

def load_page(path):
    """A page JSON, or a built page whose data script has been filled."""
    with open(path, encoding='utf-8') as f:
        text = f.read()
    if path.lower().endswith('.json'):
        return json.loads(text), None
    m = re.search(r'<script id="data" type="application/json">(.*?)</script>', text, re.S)
    if not m:
        return None, 'no <script id="data"> in the page'
    raw = m.group(1).strip()
    if raw == '{{DATA_JSON}}':
        return None, '{{DATA_JSON}} has not been filled'
    if EM_DASH in text:
        pass  # the JSON walk reports it with a path; the template itself is checked at build
    try:
        return json.loads(raw), None
    except ValueError as e:
        return None, 'the data script is not valid JSON: %s' % e


def check(d, kind, others=None):
    r = Report()
    if not isinstance(d, dict):
        r.bad('$', 'not an object')
        return r
    check_common(d, r, kind)
    CHECKS[kind](d, r, others or {})
    return r


def load_others(args):
    others = {}
    for k in ('brief', 'inbox', 'context'):
        p = getattr(args, k, None)
        if p:
            with open(p, encoding='utf-8') as f:
                others[k] = set(ids_of(json.load(f), k))
    return others


def selftest():
    data = {}
    for k, p in EXAMPLES.items():
        with open(p, encoding='utf-8') as f:
            data[k] = json.load(f)
    others = {k: set(ids_of(v, k)) for k, v in data.items()}
    fails = 0
    for k in data:
        r = check(data[k], k, others)
        print('%-8s example: %s' % (k, 'ok' if r.ok() else 'FAIL'))
        for line in r.lines:
            print('   ' + line)
        fails += 0 if r.ok() else 1

    base = {k: set(check(v, k, others).lines) for k, v in data.items()}

    def broken(kind, name, mutate):
        nonlocal fails
        d = copy.deepcopy(data[kind])
        mutate(d)
        new = [l for l in check(d, kind, others).lines if l not in base[kind]]
        print('%-8s %-52s %s' % (kind, name, 'caught' if new else 'MISSED'))
        if new:
            print('   ' + new[0])
        else:
            fails += 1

    broken('brief', 'em dash in a sentence', lambda d: d['decisions'][0].__setitem__('say', 'A — B'))
    broken('brief', 'untyped job', lambda d: d['jobs'][0].pop('type'))
    broken('brief', 'four sources', lambda d: d['decisions'][0]['sources'].extend([{'kind': 'doc', 'label': 'x', 'href': ''}] * 2))
    broken('brief', 'lateness arithmetic in a briefing', lambda d: d['jobs'][0].__setitem__('briefing', 'It is six days late.'))
    broken('brief', 'right column is an interval', lambda d: d['jobs'][0].__setitem__('meta', {'kind': 'time', 'value': '6 days'}))
    broken('brief', 'cross-reference to a missing row', lambda d: d['jobs'][0]['go'].__setitem__(0, {'id': 'zz', 'text': 'x'}))
    broken('brief', 'cross-page reference to a missing row', lambda d: d['decisions'][0]['go'].__setitem__(0, {'page': 'context', 'id': 'd99', 'text': 'x'}))
    broken('brief', 'rows over the cap', lambda d: d['jobs'].append(dict(d['jobs'][0], id='j9')))
    broken('brief', 'late without a decision or a you source', lambda d: d['jobs'][1].__setitem__('meta', {'kind': 'late', 'value': '10:00'}))
    broken('brief', 'time_label missing', lambda d: d.pop('time_label'))
    broken('brief', 'a count spelled out in the footer', lambda d: d.__setitem__('footer', ['Three replies drafted']))
    broken('inbox', 'untyped queue row', lambda d: d['queue'][8].__setitem__('type', None))
    broken('inbox', 'filed label without its rule', lambda d: d['filed'][1].pop('rule'))
    broken('inbox', 'To archive briefing missing a rule', lambda d: d['filed'][6].__setitem__('briefing', 'Nothing here.'))
    broken('inbox', 'per-channel counts do not add up', lambda d: d['filed'][0]['by_channel'].__setitem__('mail', 3))
    broken('inbox', 'more than 5 contents', lambda d: d['filed'][0]['contents'].append(dict(d['filed'][0]['contents'][0])))
    broken('inbox', 'lateness arithmetic in a briefing', lambda d: d['queue'][0].__setitem__('briefing', 'No reply in five days.'))
    broken('inbox', 'tiers out of order', lambda d: d['queue'][0].__setitem__('tier', 'week'))
    broken('context', 'decision without against', lambda d: d['decisions'][0].pop('against'))
    broken('context', 'six priorities', lambda d: d['priorities'].extend([dict(d['priorities'][0], id='p5', short='Five'), dict(d['priorities'][0], id='p6', short='Six')]))
    broken('context', 'short equals a topic name', lambda d: d['priorities'][3].__setitem__('short', 'Migration date'))
    broken('context', 'relation note on one side only', lambda d: d['entities'][2].__setitem__('with', []))
    broken('context', 'relation notes differ', lambda d: d['entities'][2]['with'][0].__setitem__('note', 'runs it'))
    broken('context', 'late next without a decision', lambda d: d['topics'][8]['next'][0].pop('decision'))
    broken('context', 'conflict without land', lambda d: d['decisions'][1].pop('land'))
    broken('context', 'conflict pair not mirrored', lambda d: d['decisions'][11].__setitem__('conflicts_with', None))
    broken('context', 'topic shares a name with an entity', lambda d: d['topics'][0].__setitem__('name', 'Elena'))
    broken('context', 'French lateness in a briefing', lambda d: d['topics'][2].__setitem__('briefing', 'Bergen n’a pas répondu depuis 5 jours.'))
    print('selftest: %s' % ('ok' if fails == 0 else '%d FAILED' % fails))
    return 0 if fails == 0 else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('path', nargs='?')
    ap.add_argument('--kind', choices=['brief', 'inbox', 'context'])
    ap.add_argument('--brief')
    ap.add_argument('--inbox')
    ap.add_argument('--context')
    ap.add_argument('--selftest', action='store_true')
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.path or not args.kind:
        ap.error('PATH and --kind are required (or --selftest)')
    d, err = load_page(args.path)
    if err:
        print('%s: %s' % (args.path, err))
        return 2
    r = check(d, args.kind, load_others(args))
    for line in r.lines:
        print(line)
    if r.ok():
        print('%s: ok (%s)' % (args.path, args.kind))
        return 0
    return 1


if __name__ == '__main__':
    sys.exit(main())
