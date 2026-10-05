#!/usr/bin/env python3
"""Build the Super Context demo: the same fictional CEO as the brief demo, every feature of the live page.

    python3 design/demo/build-brief-demo.py            first: the mailbox both demos read
    python3 design/demo/build-context-demo.py          writes design/demo/context-demo-fr.json
    python3 tools/fill-page.py --kind context skills/aureol-context/references/super-context.html \
        design/demo/context-demo-fr.json out/context-demo-fr.html

The page as a run would publish it is design/demo/context-demo-base-fr.json; this script adds what the
live page needs and the simulated world it reads (live.demo), the brief demo's mailbox plus two threads.
Publish the page with capabilities {sample: {}} only: nothing is read or written anywhere, and every
reload replays the demo. Claude answers when the page may ask it; the canned summaries and follow-ups
below stand in when it may not. Everyone and every company here is invented.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
NB = ' '


def fr(s):
    """French typography: a no-break space before : ? ! ; and curly apostrophes."""
    s = re.sub(r' ([:?!;])', NB + r'\1', s)
    return s.replace("'", '’')


with open(os.path.join(HERE, 'brief-demo-fr.json'), encoding='utf-8') as f:
    BRIEF = json.load(f)
WORLD = BRIEF['live']['demo']
ME = WORLD['account']
LEA = 'Léa Fontaine <lea@halden.example>'
ANTOINE = 'Antoine Leroy <antoine@kerys.example>'
HUGO = 'Hugo Lefèvre <hugo@halden.example>'

MAIL = json.loads(json.dumps(WORLD['mail']))
for t in MAIL:
    if t['id'] == 'ostral':
        # Hugo writes again after the morning run: the topic says so
        t['messages'].append({'from': HUGO, 'at': '10:05', 'later': True,
                              'body': fr("Camille, leur acheteuse vient d'appeler : elles acceptent 15 % si on ajoute trois mois offerts. Je peux le proposer au call ?")})
MAIL += [
    {'id': 'crm', 'subject': fr('Migration CRM : nouveau planning'), 'messages': [
        {'from': LEA, 'at': '2026-09-24T15:20:00+02:00', 'body': fr("Camille, l'intégrateur décale la migration. Je reviens vers toi avec un planning révisé d'ici vendredi.")},
        {'from': 'Camille Durand <camille@halden.example>', 'at': '2026-09-24T18:02:00+02:00', 'mine': True, 'to': 'lea@halden.example',
         'body': fr("Merci Léa. La clôture annuelle ne doit pas tomber en plein milieu : j'attends ton planning.")},
    ]},
    {'id': 'kerys', 'subject': fr('Partenariat Kerys x Halden'), 'messages': [
        {'from': ANTOINE, 'at': '2026-09-29T09:10:00+02:00', 'body': fr("Bonjour Camille, je reviens vers vous une troisième fois au sujet d'un partenariat. Avez-vous un créneau cette semaine ?")},
    ]},
]

LIVE = {
    't-ostral': {'threads': [{'thread': 'ostral', 'account': ME['alias']}]},
    't-brenner': {'threads': [{'thread': 'brenner', 'account': ME['alias']}]},
    't-espagne': {'threads': [{'thread': 'espagne', 'account': ME['alias']}]},
    't-budget': {'threads': [{'thread': 'budget', 'account': ME['alias']}]},
    't-comite': {'threads': [{'thread': 'cohortes', 'account': ME['alias']}]},
    't-crm': {'threads': [{'thread': 'crm', 'account': ME['alias']}], 'waiting': {'name': 'Léa', 'email': 'lea@halden.example'}},
    't-kerys': {'threads': [{'thread': 'kerys', 'account': ME['alias']}]},
}

SUMMARIES = {
    't-ostral': {'where': fr("Ostral veut 18 % sur 3 ans ; Hugo pousse, Claire bloque à 12 %, la règle dit 15 %."),
                 'who': [{'name': 'Hugo', 'date': '30 sept.', 'said': fr("Veut accepter 18 % pour signer demain et faire son trimestre.")},
                         {'name': 'Claire', 'date': '30 sept.', 'said': fr("Refuse au-delà de 12 % pour garder la marge du compte au-dessus de 60 %.")}],
                 'open': [fr("Votre réponse sur la remise, avant le call de 11:00.")], 'next': fr("Call Ostral à 11:00.")},
    't-crm': {'where': fr("L'intégrateur décale la migration ; le planning révisé de Léa n'est pas arrivé."),
              'who': [{'name': 'Léa', 'date': '24 sept.', 'said': fr("L'intégrateur décale la migration ; elle promet un planning révisé d'ici vendredi.")},
                      {'name': 'Vous', 'date': '24 sept.', 'said': fr("La clôture annuelle ne doit pas tomber en plein milieu ; vous attendez le planning.")}],
              'open': [fr("Le planning révisé, promis par Léa pour vendredi 26.")], 'next': ''},
}
DRAFTS = {
    't-crm': fr("Bonjour Léa,\n\nJe reviens vers toi sur le planning révisé de la migration CRM, que tu pensais m'envoyer vendredi. Peux-tu me le partager, en vérifiant que la clôture annuelle ne tombe pas en plein milieu ?\n\nMerci,\nCamille"),
}

with open(os.path.join(HERE, 'context-demo-base-fr.json'), encoding='utf-8') as f:
    doc = json.load(f)
for tp in doc['topics']:
    if tp['id'] in LIVE:
        tp['live'] = LIVE[tp['id']]
# a conflict carries its open question on both decisions
land = {x['id']: x.get('land') for x in doc['decisions']}
for x in doc['decisions']:
    if x.get('conflicts_with') and not x.get('land'):
        x['land'] = land.get(x['conflicts_with']['id'])

# a priority whose outcome has happened: Close puts it to rest in one click
doc['priorities'].append({
    'id': 'p5', 'short': fr('Assurance cyber'), 'say': fr("Renouveler l'assurance cyber avant le 1er octobre."),
    'ahead': fr('les autres achats'), 'confirmed': '1 sept.', 'lede': '', 'yours': '',
    'done_hint': fr('Contrat renouvelé le 28 sept.'),
    'history': [{'date': '1 sept.', 'event': fr('Ajoutée à la rentrée, rang 5')}],
    'sources': [{'kind': 'mail', 'label': fr('Courtier, contrat renouvelé, 28 sept.'), 'href': ''}],
    'briefing': fr("Mon assurance cyber devait être renouvelée avant le 1er octobre. Vérifie le contrat reçu le 28 septembre et dis-moi ce qui a changé. N'envoie rien."),
})

doc['sub'] = fr('Démonstration : personnes, entreprises et messages fictifs.')
doc['generated'] = '2026-10-01T06:45:00+02:00'
doc['live'] = {
    'me': BRIEF['live']['me'],
    'mail': {'server': 'Aureol Connect', 'api': 'aureol'},
    'chat': None,
    'demo': {'now': WORLD['now'], 'account': ME, 'mail': MAIL, 'summaries': SUMMARIES, 'drafts': DRAFTS},
}

# a delay the integrator announced is a fact read off a source; the page still never words it as lateness
text = json.dumps(doc, ensure_ascii=False, indent=1)
text = text.replace('rois semaines de retard', 'rois semaines de décalage')
out = os.path.join(HERE, 'context-demo-fr.json')
with open(out, 'w', encoding='utf-8') as f:
    f.write(text)
print('%s: written, %d priorities, %d topics, %d with threads' % (out, len(doc['priorities']), len(doc['topics']), len(LIVE)))
