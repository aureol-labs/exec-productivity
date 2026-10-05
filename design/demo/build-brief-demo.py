#!/usr/bin/env python3
"""Build the Daily brief demo: a fictional CEO's morning, every feature of the live page.

    python3 design/demo/build-brief-demo.py            writes design/demo/brief-demo-fr.json
    python3 tools/fill-page.py --kind brief skills/aureol-brief/references/daily-brief.html \
        design/demo/brief-demo-fr.json out/brief-demo-fr.html

The page as a run would publish it is design/demo/brief-demo-base-fr.json; this script adds what the
live page needs and the simulated world it reads (live.demo). Publish the page with capabilities
{sample: {}} only: its connections are simulated, nothing is read or written anywhere, and every reload
replays the demo. Claude answers when the page may ask it; the canned options and drafts below stand in
when it may not. Everyone and every company here is invented. The demo's clock reads 10:20.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
NB = ' '


def fr(s):
    """French typography: a no-break space before : ? ! ; and curly apostrophes."""
    s = re.sub(r' ([:?!;])', NB + r'\1', s)
    return s.replace("'", '’')


ME = {'alias': 'pro', 'email': 'camille@halden.example', 'name': 'Camille Durand'}
CAMILLE = 'Camille Durand <camille@halden.example>'
CLAIRE = 'Claire Martin <claire@halden.example>'
HUGO = 'Hugo Lefèvre <hugo@halden.example>'
JULIE = 'Julie Roux <julie@halden.example>'
MARC = 'Marc Delorme <marc.delorme@vellmar.example>'
ETIENNE = 'Étienne Morel <e.morel@brenner.example>'


def msg(frm, at, body, later=False, to=''):
    m = {'from': frm, 'at': at, 'body': fr(body)}
    if frm == CAMILLE:
        m['mine'] = True
        m['to'] = to
    if later:
        m['later'] = True
    return m


MAIL = [
    {'id': 'ostral', 'subject': fr('Renouvellement Ostral : la remise'), 'messages': [
        msg(HUGO, '2026-09-30T09:12:00+02:00', "Camille, Ostral demande 18 % sur 3 ans pour renouveler. Je peux signer demain si on accepte, ça me fait mon trimestre. Je pense qu'on peut y aller : c'est 240 k€ par an."),
        msg(CLAIRE, '2026-09-30T11:40:00+02:00', "Je ne suis pas d'accord. Au-delà de 12 %, la marge du compte passe sous 60 %. Et la règle de juin plafonne les renouvellements à 15 %. Brenner a signé à 15 % l'an dernier."),
        msg(HUGO, '2026-09-30T17:05:00+02:00', "Si on tient 15 %, ils peuvent regarder ailleurs. Leur acheteuse me l'a dit au téléphone. Camille, il nous faut ta décision avant le call de 11:00."),
    ]},
    {'id': 'espagne', 'subject': fr('Finalistes Espagne'), 'messages': [
        msg(JULIE, '2026-09-29T16:30:00+02:00', "Camille, les deux finalistes pour diriger les ventes en Espagne : Carmen Vidal, 10 ans chez un concurrent espagnol, réseau grands comptes, 160 k€, et elle a une autre offre ; Pablo Ortega, startup, très bon en acquisition, 120 k€. L'équipe penche pour Carmen, Hugo pour Pablo. Le budget prévu est de 140 k€. Il me faut ton choix pour faire l'offre."),
    ]},
    {'id': 'budget', 'subject': fr('Budget 2027 et comité du 8 octobre'), 'messages': [
        msg(MARC, '2026-09-30T08:20:00+02:00', "Camille, pour le comité du 8 octobre j'aurai besoin du budget 2027 arbitré, et de la rétention nette par cohorte sur 8 trimestres. Le plan de valeur reste 15 % d'EBITDA fin 2027."),
        msg(CLAIRE, '2026-09-30T19:10:00+02:00', "Mon scénario : +16 % de croissance, 5 recrutements commerciaux, 15 % d'EBITDA. Celui de Hugo : +22 %, 14 recrutements, 9 % d'EBITDA. Le Comex de mardi n'a pas tranché."),
    ]},
    {'id': 'cohortes', 'subject': fr('Cohortes pour le comité'), 'messages': [
        msg(MARC, '2026-09-30T08:24:00+02:00', "Pouvez-vous m'envoyer la rétention nette par cohorte sur 8 trimestres avant le comité ? La dernière fois, je l'ai reçue la veille."),
    ]},
    {'id': 'brenner', 'subject': fr('Avenant au contrat de transport'), 'messages': [
        msg(ETIENNE, '2026-09-29T10:02:00+02:00', "Madame, vous trouverez l'avenant relu par nos juristes et les vôtres. Il ne manque que votre signature."),
        msg(CAMILLE, '10:05', "Bonjour Étienne, c'est signé, vous l'avez en retour. Bien à vous, Camille", later=True, to='e.morel@brenner.example'),
    ]},
]

OPTIONS = {
    'thread:ostral': [
        {'option': fr('Tenir 15 % sur 3 ans'), 'who': fr('la règle de juin'), 'effect': fr("Respecte le plafond, comme Brenner l'an dernier."), 'risk': fr("Ostral peut regarder ailleurs, selon Hugo.")},
        {'option': fr('Accorder 18 % sur 3 ans'), 'who': 'Hugo', 'effect': fr('Signature demain, 240 k€ par an sécurisés sur 3 ans.'), 'risk': fr('Marge du compte sous 60 %, précédent pour les renouvellements.')},
        {'option': fr('Plafonner à 12 %'), 'who': 'Claire', 'effect': fr('Garde la marge du compte au-dessus de 60 %.'), 'risk': fr('Écart de 6 points avec la demande d’Ostral.')},
        {'option': fr('15 % et trois mois offerts si signature avant le 15'), 'who': '', 'effect': fr('Tient la règle et donne à Hugo une contrepartie à vendre.'), 'risk': ''},
    ],
    'thread:espagne': [
        {'option': fr('Recruter Carmen à 160 k€'), 'who': fr("l'équipe"), 'effect': fr('Réseau grands comptes en place pour le lancement de janvier.'), 'risk': fr('20 k€ au-dessus du budget de 140 k€.')},
        {'option': fr('Recruter Pablo à 120 k€'), 'who': 'Hugo', 'effect': fr("Sous le budget, profil d'acquisition."), 'risk': fr('Plus junior, sans réseau en Espagne.')},
    ],
    'thread:budget': [
        {'option': fr('+22 % de croissance, 14 recrutements'), 'who': 'Hugo', 'effect': fr("Croissance maximale, EBITDA à 9 %."), 'risk': fr("S'écarte du plan de valeur Vellmar.")},
        {'option': fr("+16 %, 5 recrutements, 15 % d'EBITDA"), 'who': 'Claire', 'effect': fr('Tient le plan de valeur à 15 % fin 2027.'), 'risk': fr('Croissance plus lente.')},
    ],
}

# a canned draft stands in only for the option it was written for; any other choice needs Claude
DRAFTS = {
    'thread:ostral|' + fr('Tenir 15 % sur 3 ans'): fr("Claire, Hugo,\n\nJe tranche : on tient 15 % sur 3 ans, comme la règle de juin et comme Brenner l'an dernier. Hugo, propose-le à Ostral au call de 11:00 ; si elles hésitent, reviens vers moi avant de bouger. Claire, merci de préparer l'avenant à 15 % pour demain.\n\nCamille"),
    'thread:espagne|' + fr('Recruter Carmen à 160 k€'): fr("Julie,\n\nJe pars sur Carmen : son réseau grands comptes compte plus que l'écart de salaire pour le lancement de janvier. Peux-tu lui faire une offre d'ici demain, avant son autre offre ?\n\nCamille"),
    'thread:budget|' + fr("+16 %, 5 recrutements, 15 % d'EBITDA"): fr("Claire, Hugo, Marc,\n\nNous présentons au comité le scénario à +16 % : 5 recrutements commerciaux et 15 % d'EBITDA fin 2027, en ligne avec le plan de valeur. Claire, peux-tu finaliser le budget pour lundi ?\n\nCamille"),
}

CONTEXT = {
    'c1': fr("Ostral, client à 240 k€ par an, demande 18 % pour renouveler sur 3 ans. Hugo, VP Sales, veut signer demain. Claire, CFO, refuse au-delà de 12 % pour garder la marge du compte au-dessus de 60 %. La règle de juin plafonne les renouvellements à 15 %. Brenner a signé à 15 % l'an dernier."),
}

with open(os.path.join(HERE, 'brief-demo-base-fr.json'), encoding='utf-8') as f:
    doc = json.load(f)

THREAD = {'c1': 'ostral', 'c2': 'espagne', 'c3': 'budget', 'j1': 'cohortes', 'j2': 'brenner'}
for row in doc['decisions'] + doc['jobs']:
    if row['id'] in CONTEXT:
        row['context'] = CONTEXT[row['id']]
    if row['id'] in THREAD:
        row['live'] = {'thread': THREAD[row['id']], 'account': ME['alias']}
    if row['ref'] == 'slack:thomas':
        row['ref'] = 'slack:D0THOMAS1'
        row['live'] = {'channel_id': 'D0THOMAS1'}

# a double booking this afternoon: its options are the meetings to keep
CLASH = {
    'id': 'm5', 'clash': True,
    'meetings': [
        {'start': '15:30', 'end': '16:15', 'title': fr('Revue produit, Léa'), 'organizer': 'lea@halden.example',
         'cost': fr("La déplacer coûte peu : Léa a proposé jeudi.")},
        {'start': '15:45', 'end': '16:30', 'title': fr('Avocat, pacte Vellmar'), 'organizer': 'cabinet@roux-avocats.example',
         'cost': fr("Le déplacer coûte : sa signature est attendue avant le comité.")},
    ],
    'to_land': {'text': fr('Lequel vous gardez, avant midi.')},
    'live': {'account': ME['alias']},
    'sources': [{'kind': 'calendar', 'label': fr('15:30 Revue produit'), 'href': ''},
                {'kind': 'calendar', 'label': fr('15:45 Avocat, pacte Vellmar'), 'href': ''}],
    'briefing': fr("Je suis pris deux fois à 15:30 : la revue produit avec Léa et l'avocat sur le pacte Vellmar. Dis-moi ce que coûte le déplacement de chacun, puis rédige le message pour celui que je déplace. N'envoie rien."),
}
doc['strip']['meetings'].append(CLASH)
doc['strip']['meetings'].sort(key=lambda m: m.get('start') or m['meetings'][0]['start'])
CLASH_DRAFT = fr("Bonjour Léa,\n\nJe dois prendre l'avocat sur le pacte Vellmar à 15:45. Peut-on décaler la revue produit à jeudi, comme tu l'avais proposé ?\n\nMerci,\nCamille")
DRAFTS['clash:m5|' + fr('Garder Avocat, pacte Vellmar')] = CLASH_DRAFT

doc['sub'] = fr('Démonstration : personnes, entreprises et messages fictifs.')
doc['generated'] = '2026-10-01T06:50:00+02:00'
doc['live'] = {
    'me': {'name': 'Camille', 'role': fr('CEO de Halden, éditeur SaaS de facturation B2B, 180 personnes, détenu majoritairement par Vellmar Capital')},
    'mail': {'server': 'Aureol Connect', 'api': 'aureol'},
    'calendar': {'server': 'Aureol Connect', 'api': 'aureol'},
    'chat': {'server': 'Slack', 'api': 'slack'},
    'demo': {'now': '10:20', 'account': ME, 'me_id': 'U0CAMILLE', 'mail': MAIL,
             'slack': [{'channel': 'D0THOMAS1', 'uid': 'U0THOMAS', 'from': 'Thomas Girard', 'at': '2026-09-30T18:40:00+02:00',
                        'text': fr("Camille, le budget du séminaire de direction, 18 k€, est-il validé ? Le lieu ne tient l'option que jusqu'à samedi.")}],
             'options': OPTIONS, 'drafts': DRAFTS},
}

out = os.path.join(HERE, 'brief-demo-fr.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)
print('%s: written, %d decisions, %d jobs, %d meetings' % (out, len(doc['decisions']), len(doc['jobs']), len(doc['strip']['meetings'])))
