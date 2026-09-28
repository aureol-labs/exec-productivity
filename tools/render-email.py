#!/usr/bin/env python3
"""The Daily brief as an email, for the exec who asked for it at install.

    render-email.py --kind brief PAGE OUT.html --url https://claude.ai/artifact/...
    render-email.py --selftest

PAGE is the brief's JSON, or the built page whose {{DATA_JSON}} has been filled. Writes OUT.html (inline
styles, tables, no script, nothing loaded from the network) and OUT.html.txt (the plain-text part), and
prints the subject on its first line. Every word comes from the data or from design/dictionary.json, so the
email says what the page says. The page stays the reference: the email ends on its link.
Standard library only.
"""
import argparse
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DICTIONARY = os.path.join(HERE, '..', 'design', 'dictionary.json')
EXAMPLE = os.path.join(HERE, '..', 'skills', 'aureol-brief', 'references', 'example.json')

# the page's tokens (design/partial.css); ink-3 one step darker, a mail client's grey is lighter than a page's
PAPER, INK, INK2, INK3, HAIR = '#FCFCFB', '#26292E', '#5F666F', '#8E969E', '#E4E9EA'
PINE, PINE_INK, BRICK = '#2E6B62', '#28564F', '#A2483A'
SERIF = "'Iowan Old Style',Palatino,'Palatino Linotype',Georgia,serif"
SANS = "'Avenir Next',Avenir,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"
CREDIT_HREF = 'https://www.linkedin.com/in/paul-rousselle/'


def load_page(path):
    src = open(path, encoding='utf-8').read()
    if path.endswith('.json'):
        return json.loads(src)
    m = re.search(r'<script id="data" type="application/json">(\{.*?)</script>', src, re.S)
    if not m:
        raise ValueError('no filled data script in %s' % path)
    return json.loads(m.group(1))


def words(lang):
    d = json.load(open(DICTIONARY, encoding='utf-8'))
    return d.get(lang) or d['en']


class Say:
    """L, F and P as the pages have them: a string, a string with {vars}, a plural pair (singular at 1)."""

    def __init__(self, lang):
        self.w = words(lang)

    def L(self, k):
        return self.w.get(k, k)

    def F(self, s, **v):
        return re.sub(r'\{(\w+)\}', lambda m: str(v.get(m.group(1), m.group(0))), s)

    def P(self, k, n, **v):
        s = self.L(k)
        if isinstance(s, list):
            s = s[0] if n == 1 else s[1]
        return self.F(s, n=n, **v)


def e(s):
    return html.escape(str(s or ''), quote=True)


def safe_href(h):
    return h if isinstance(h, str) and h.startswith('https://') else ''


def meta_text(mt, say):
    """The right column, as the page words it; late is the one brick mark."""
    if not isinstance(mt, dict) or not mt.get('value') or mt.get('kind') in (None, 'none'):
        return '', False
    k, v = mt['kind'], mt['value']
    if k == 'before':
        return say.F(say.L('m_before'), v=v), False
    if k == 'asked':
        return say.F(say.L('m_asked'), v=v), False
    if k == 'late':
        return say.F(say.L('m_late'), v=v), True
    return v, False


def colon(d):
    """French sets a no-break space before a colon, as the dictionary does."""
    return '\u00a0: ' if d.get('lang') == 'fr' else ': '


def fact(row):
    arg = row.get('argument')
    return arg[0] if isinstance(arg, list) and arg else ''


def counts(d):
    meetings = (d.get('strip') or {}).get('meetings') or []
    n_meet = n_clash = 0
    for m in meetings:
        if m.get('clash'):
            n_clash += 1
            n_meet += len(m.get('meetings') or [])
        else:
            n_meet += 1
    return n_meet, n_clash


def title(d, say):
    n_meet, n_clash = counts(d)
    parts = [say.P('meetings_n', n_meet)]
    if n_clash:
        parts.append(say.P('clashes_n', n_clash))
    parts += [say.P('decisions_n', len(d.get('decisions') or [])), say.P('jobs_n', len(d.get('jobs') or []))]
    return ', '.join(parts)


def subject(d, say):
    return '%s, %s' % (say.L('page_brief'), d.get('date_label') or d.get('today') or '')


def to_land_text(tl):
    if not isinstance(tl, dict):
        return ''
    return tl.get('text') or (tl.get('go') or {}).get('text') or ''


def render_brief(d, url):
    say = Say(d.get('lang') or 'en')
    url = safe_href(url)
    o = []
    w = o.append

    def head(label, n=None):
        tally = (' <span style="font-weight:400;letter-spacing:.3px;text-transform:none;color:%s;">%s</span>'
                 % (INK3, e(n))) if n is not None else ''
        w('<tr><td style="padding:30px 0 7px;border-bottom:1px solid %s;font-size:11px;letter-spacing:1.5px;'
          'text-transform:uppercase;font-weight:600;color:%s;">%s%s</td></tr>' % (HAIR, PINE, e(label), tally))

    def row(main, right='', late=False, lines=(), tone=INK):
        rc = BRICK if late else INK3
        rw = '600' if late else '400'
        w('<tr><td style="padding:13px 0 14px;border-bottom:1px solid %s;">'
          '<table role="presentation" width="100%%" cellpadding="0" cellspacing="0"><tr>'
          '<td valign="top" style="font-size:15.5px;line-height:1.45;font-weight:500;color:%s;padding-right:16px;">%s</td>'
          '<td valign="top" align="right" style="white-space:nowrap;font-size:12.5px;line-height:1.7;color:%s;font-weight:%s;">%s</td>'
          '</tr></table>' % (HAIR, tone, e(main), rc, rw, e(right)))
        for text, colour in lines:
            if text:
                w('<div style="padding-top:4px;font-size:13.5px;line-height:1.5;color:%s;">%s</div>' % (colour, e(text)))
        w('</td></tr>')

    w('<!doctype html><html lang="%s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
      '<title>%s</title></head><body style="margin:0;padding:0;background:%s;">'
      % (e(d.get('lang') or 'en'), e(subject(d, say)), PAPER))
    w('<table role="presentation" width="100%%" cellpadding="0" cellspacing="0" style="background:%s;"><tr>'
      '<td align="center" style="padding:32px 16px 40px;">'
      '<table role="presentation" width="100%%" cellpadding="0" cellspacing="0" style="max-width:680px;'
      'font-family:%s;color:%s;">' % (PAPER, SANS, INK))
    w('<tr><td style="font-size:11px;letter-spacing:1.5px;text-transform:uppercase;font-weight:600;color:%s;">'
      '%s</td></tr>' % (PINE, e(say.L('page_brief'))))
    w('<tr><td style="padding-top:12px;font-size:15px;color:%s;">%s</td></tr>' % (INK2, e(d.get('date_label'))))
    w('<tr><td style="padding-top:10px;font-family:%s;font-size:27px;line-height:1.25;color:%s;">%s</td></tr>'
      % (SERIF, INK, e(title(d, say))))
    if d.get('sub'):
        w('<tr><td style="padding-top:10px;font-size:14.5px;line-height:1.55;color:%s;">%s</td></tr>' % (INK2, e(d['sub'])))

    meetings = (d.get('strip') or {}).get('meetings') or []
    if meetings:
        n_meet, _ = counts(d)
        head(say.P('meetings_n', n_meet))
        for m in meetings:
            if m.get('clash'):
                ms = m.get('meetings') or []
                a = ms[0].get('start', '') if ms else ''
                z = ms[-1].get('end', '') if ms else ''
                lines = []
                for x in ms:
                    lines.append(('%s  %s' % (x.get('start', ''), x.get('title', '')), INK))
                    lines.append((x.get('cost', ''), INK2))
                lt = to_land_text(m.get('to_land'))
                if lt:
                    lines.append((say.L('to_land') + colon(d) + lt, BRICK))
                # two meetings at once is the page's one brick card: the head says so in brick here too
                row(say.F(say.L('clash_head'), a=a, b=z, what=say.P('meetings_n', len(ms))), '', False, lines, BRICK)
                continue
            b = m.get('brief') or {}
            span = '%s–%s' % (m.get('start', ''), m.get('end', '')) if m.get('end') else m.get('start', '')
            lines = []
            lt = to_land_text(b.get('to_land'))
            if lt:
                lines.append((say.L('to_land') + colon(d) + lt, PINE_INK))
            im = (b.get('in_mind') or {}).get('text') if isinstance(b.get('in_mind'), dict) else ''
            if im:
                lines.append((say.L('in_mind') + colon(d) + im, INK2))
            row(b.get('title') or m.get('label', ''), span, False, lines)

    decisions = d.get('decisions') or []
    if decisions:
        head(say.L('decisions_to_land'), len(decisions))
        for x in decisions:
            right, late = meta_text(x.get('meta'), say)
            row(x.get('say', ''), right, late, [(fact(x), PINE_INK)])
    jobs = d.get('jobs') or []
    if jobs:
        head(say.L('jobs_to_do'), len(jobs))
        for x in jobs:
            right, late = meta_text(x.get('meta'), say)
            row(x.get('say', ''), right, late, [(fact(x), PINE_INK)])

    foot = ' · '.join(str(f) for f in (d.get('footer') or []) if f)
    w('<tr><td style="padding-top:26px;font-size:12px;line-height:1.6;color:%s;">%s</td></tr>' % (INK3, e(foot)))
    if url:
        w('<tr><td style="padding-top:14px;"><a href="%s" style="font-size:14px;font-weight:600;color:%s;'
          'text-decoration:none;border-bottom:1px solid %s;">%s</a></td></tr>' % (e(url), PINE, PINE, e(say.L('open_brief'))))
    w('<tr><td style="padding-top:26px;font-size:11px;letter-spacing:.3px;color:%s;">%s '
      '<a href="%s" style="color:%s;text-decoration:none;">%s</a> %s</td></tr>'
      % (INK3, e(say.L('by')), CREDIT_HREF, INK3, e(say.L('by_name')), e(say.L('by_tail'))))
    w('</table></td></tr></table></body></html>')
    return ''.join(o)


def text_brief(d, url):
    say = Say(d.get('lang') or 'en')
    out = [subject(d, say), title(d, say), '']
    for m in (d.get('strip') or {}).get('meetings') or []:
        if m.get('clash'):
            for x in m.get('meetings') or []:
                out.append('%s  %s' % (x.get('start', ''), x.get('title', '')))
            lt = to_land_text(m.get('to_land'))
            if lt:
                out.append('  ' + say.L('to_land') + colon(d) + lt)
            continue
        b = m.get('brief') or {}
        out.append('%s  %s' % (m.get('start', ''), b.get('title') or m.get('label', '')))
        lt = to_land_text(b.get('to_land'))
        if lt:
            out.append('  ' + say.L('to_land') + colon(d) + lt)
    for key, rows in (('decisions_to_land', d.get('decisions') or []), ('jobs_to_do', d.get('jobs') or [])):
        if rows:
            out += ['', say.L(key)]
            for x in rows:
                right, _ = meta_text(x.get('meta'), say)
                out.append('- ' + x.get('say', '') + (' (%s)' % right if right else ''))
                if fact(x):
                    out.append('  ' + fact(x))
    out += [''] + [str(f) for f in (d.get('footer') or []) if f]
    if safe_href(url):
        out.append(url)
    return '\n'.join(out) + '\n'


def render(d, kind, url):
    if kind != 'brief':
        raise ValueError('only the brief goes by email')
    return render_brief(d, url), text_brief(d, url), subject(d, Say(d.get('lang') or 'en'))


def selftest():
    d = json.load(open(EXAMPLE, encoding='utf-8'))
    fails = []
    body, txt, subj = render(d, 'brief', 'https://claude.ai/artifact/example-brief')
    if '<script' in body.lower():
        fails.append('a script in the email')
    for h in re.findall(r'href="([^"]*)"', body):
        if not h.startswith('https://'):
            fails.append('a link that is not https: %r' % h)
    for x in (d.get('decisions') or []) + (d.get('jobs') or []):
        if html.escape(x['say'], quote=True) not in body:
            fails.append('missing line: %s' % x['say'])
    if 'https://claude.ai/artifact/example-brief' not in txt:
        fails.append('the text part has no link to the page')
    hostile = json.loads(json.dumps(d))
    hostile['decisions'][0]['say'] = '<img src=x onerror=alert(1)>'
    hostile_body, _, _ = render(hostile, 'brief', 'javascript:alert(1)')
    if '<img' in hostile_body or 'javascript:' in hostile_body:
        fails.append('data reached the markup unescaped, or a non-https link survived')
    fr = json.loads(json.dumps(d))
    fr['lang'] = 'fr'
    _, _, fr_subj = render(fr, 'brief', '')
    if not fr_subj.startswith(words('fr')['page_brief']):
        fails.append('the French subject does not use the French page name')
    for f in fails:
        print('FAIL ' + f)
    print('render-email selftest: %s (%s)' % ('ok' if not fails else '%d failed' % len(fails), subj))
    return 1 if fails else 0


def main():
    ap = argparse.ArgumentParser(description='The Daily brief as an email.')
    ap.add_argument('--kind', default='brief')
    ap.add_argument('--url', default='')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('page', nargs='?')
    ap.add_argument('out', nargs='?')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.page or not a.out:
        ap.error('PAGE and OUT are required')
    body, txt, subj = render(load_page(a.page), a.kind, a.url)
    open(a.out, 'w', encoding='utf-8').write(body)
    open(a.out + '.txt', 'w', encoding='utf-8').write(txt)
    print(subj)
    return 0


if __name__ == '__main__':
    sys.exit(main())
