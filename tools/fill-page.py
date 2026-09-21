#!/usr/bin/env python3
"""Fill a built page template with one JSON document and check the result.

    fill-page.py --kind brief|inbox|context TEMPLATE.html DATA.json OUT.html [--links key=url ...]

Replaces the single {{DATA_JSON}} placeholder with the serialised document, every "<" escaped as
\\u003c so the JSON can never close its own script element, then runs check-page on the data and
refuses to write a page that fails. --links sets or overrides data.links entries (the other pages'
addresses) before filling. Standard library only.
"""
import argparse, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kind', required=True, choices=['brief', 'inbox', 'context'])
    ap.add_argument('template'); ap.add_argument('data'); ap.add_argument('out')
    ap.add_argument('--links', nargs='*', default=[], help='key=url pairs written into data.links')
    a = ap.parse_args()
    with open(a.data, encoding='utf-8') as f:
        data = json.load(f)
    if a.links:
        data.setdefault('links', {})
        for pair in a.links:
            k, v = pair.split('=', 1); data['links'][k] = v
    tmp = a.out + '.data.json'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    r = subprocess.run([sys.executable, os.path.join(HERE, 'check-page.py'), '--kind', a.kind, tmp])
    if r.returncode != 0:
        os.remove(tmp); sys.exit('fill-page: the data does not pass check-page; nothing written')
    os.remove(tmp)
    with open(a.template, encoding='utf-8') as f:
        html = f.read()
    if html.count('{{DATA_JSON}}') != 1:
        sys.exit('fill-page: the template must carry exactly one {{DATA_JSON}}')
    payload = json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')
    html = html.replace('{{DATA_JSON}}', payload)
    if '—' in html:
        sys.exit('fill-page: an em dash is in the page; nothing written')
    with open(a.out, 'w', encoding='utf-8') as f:
        f.write(html)
    print('%s: written (%d bytes)' % (a.out, len(html.encode('utf-8'))))


if __name__ == '__main__':
    main()
