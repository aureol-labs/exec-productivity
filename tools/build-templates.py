#!/usr/bin/env python3
"""Build the three page templates from the one design source.

    build-templates.py            writes skills/<skill>/references/<page>.html
    build-templates.py --check    rebuilds to a temp dir and diffs against the written files

Each template is assembled from design/pages/<page>.html (the page's own head comment and
render()), design/partial.css, design/partial.js, design/dictionary.json, design/glyphs.html,
design/security.txt and the page's example.json, which is embedded as the fallback rendered
when {{DATA_JSON}} is left unreplaced. The output inlines everything: no external files, no
webfonts, no network. Idempotent. Standard library only.

Before writing, every example is run through tools/check-page.py and the assembled page is
checked for an em dash and for a placeholder left unfilled (other than {{DATA_JSON}}).
"""
import difflib
import importlib.util
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DESIGN = os.path.join(ROOT, 'design')
PAGES = [
    # page name, page kind (as check-page knows it)
    ('super-context', 'context'),
    ('daily-brief', 'brief'),
    ('inbox', 'inbox'),
]
# the skill folder that ships each kind's template and example
FOLDER = {'context': 'aureol-context', 'brief': 'aureol-brief', 'inbox': 'aureol-inbox'}
EM_DASH = chr(0x2014)  # the em dash, never written literally here


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def embed_json(obj):
    """JSON for a <script type="application/json"> element: every "<" escaped as \\u003c
    so no string can close the element, and nothing else touched."""
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')


def load_checker():
    spec = importlib.util.spec_from_file_location('check_page', os.path.join(HERE, 'check-page.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def build_one(page, skill, parts, checker, examples):
    src = read(os.path.join(DESIGN, 'pages', page + '.html'))
    example_path = os.path.join(ROOT, 'skills', FOLDER[skill], 'references', 'example.json')
    example = examples[skill]
    others = {k: set(checker.ids_of(v, k)) for k, v in examples.items() if k != skill}
    report = checker.check(example, skill, others)
    if not report.ok():
        raise SystemExit('%s: the example does not pass check-page:\n  ' % example_path + '\n  '.join(report.lines))
    out = (src.replace('{{SECURITY}}', parts['security'].rstrip('\n'))
              .replace('{{CSS}}', parts['css'].rstrip('\n'))
              .replace('{{GLYPHS}}', parts['glyphs'].rstrip('\n'))
              .replace('{{EXAMPLE_JSON}}', embed_json(example))
              .replace('{{DICT}}', embed_json(parts['dict']))
              .replace('{{JS}}', parts['js'].rstrip('\n')))
    left = set(re.findall(r'\{\{([A-Z_]+)\}\}', out)) - {'DATA_JSON'}
    if left:
        raise SystemExit('%s: placeholders left unfilled: %s' % (page, ', '.join(sorted(left))))
    if out.count('{{DATA_JSON}}') != 1:
        raise SystemExit('%s: the template must carry exactly one {{DATA_JSON}}' % page)
    if EM_DASH in out:
        line = next(i + 1 for i, l in enumerate(out.split('\n')) if EM_DASH in l)
        raise SystemExit('%s: em dash at line %d of the built page' % (page, line))
    if '\r' in out:
        raise SystemExit('%s: carriage return in the built page' % page)
    return out


def build_all():
    parts = {
        'css': read(os.path.join(DESIGN, 'partial.css')),
        'js': read(os.path.join(DESIGN, 'partial.js')),
        'glyphs': read(os.path.join(DESIGN, 'glyphs.html')),
        'security': read(os.path.join(DESIGN, 'security.txt')),
        'dict': json.loads(read(os.path.join(DESIGN, 'dictionary.json'))),
    }
    for key in ('css', 'js', 'glyphs', 'security'):
        if EM_DASH in parts[key]:
            raise SystemExit('design/%s carries an em dash' % key)
    en, fr = parts['dict'].get('en', {}), parts['dict'].get('fr', {})
    missing = sorted(set(en) ^ set(fr))
    if missing:
        raise SystemExit('dictionary: keys not in both languages: %s' % ', '.join(missing))
    checker = load_checker()
    examples = {}
    for page, skill in PAGES:
        examples[skill] = json.loads(read(os.path.join(ROOT, 'skills', FOLDER[skill], 'references', 'example.json')))
    built = {}
    for page, skill in PAGES:
        built[(page, skill)] = build_one(page, skill, parts, checker, examples)
    return built


def target(page, skill):
    return os.path.join(ROOT, 'skills', FOLDER[skill], 'references', page + '.html')


def main(argv):
    built = build_all()
    if '--check' in argv:
        rc = 0
        tmp = tempfile.mkdtemp(prefix='aureol-templates-')
        for (page, skill), out in built.items():
            fresh = os.path.join(tmp, page + '.html')
            with open(fresh, 'w', encoding='utf-8') as f:
                f.write(out)
            have = target(page, skill)
            if not os.path.exists(have):
                print('%s: not built yet' % have)
                rc = 1
                continue
            a, b = read(have).splitlines(keepends=True), out.splitlines(keepends=True)
            if a != b:
                rc = 1
                print('%s: differs from a fresh build' % have)
                for line in list(difflib.unified_diff(a, b, have, fresh, n=1))[:40]:
                    sys.stdout.write(line)
            else:
                print('%s: up to date' % have)
        return rc
    for (page, skill), out in built.items():
        path = target(page, skill)
        if os.path.exists(path) and read(path) == out:
            print('%s: unchanged (%d bytes)' % (path, len(out.encode('utf-8'))))
            continue
        with open(path, 'w', encoding='utf-8') as f:
            f.write(out)
        print('%s: written (%d bytes)' % (path, len(out.encode('utf-8'))))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
