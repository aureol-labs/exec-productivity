#!/usr/bin/env python3
"""Build the Priority inbox demo: a fictional CEO's mail and Slack, every feature of the live page.

    python3 design/demo/build-inbox-demo.py            writes design/demo/inbox-demo-fr.json
    python3 tools/fill-page.py --kind inbox skills/aureol-inbox/references/inbox.html \
        design/demo/inbox-demo-fr.json out/inbox-demo-fr.html

Publish the page with capabilities {sample: {}} only: its connections are simulated from live.demo,
nothing is read or written anywhere, and every reload replays the demo. Everyone and every company
here is invented. Times are written on a reference day; the page moves them so the run happened 40
minutes before it is opened.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
NB = ' '


def fr(s):
    """French typography: a no-break space before : ? ! ; and curly apostrophes."""
    s = re.sub(r' ([:?!;])', NB + r'\1', s)
    return s.replace("'", '’')


ME = {'alias': 'pro', 'email': 'camille@norvel.example', 'name': 'Camille Durand'}
ME_FROM = 'Camille Durand <camille@norvel.example>'
RUN = '2026-10-01T11:30:00+02:00'
DAY = '2026-10-01'
LABELS = [{'id': 'Label_1', 'name': 'Factures'}, {'id': 'Label_2', 'name': 'À lire plus tard'},
          {'id': 'Label_3', 'name': 'À archiver'}]
RULES = [
    {'label': 'Factures', 'rule': fr('Factures, reçus de paiement, confirmations de commande et de livraison')},
    {'label': 'À lire plus tard', 'rule': fr('Newsletters et presse')},
    {'label': 'À archiver', 'rule': fr('Promotions et invitations de fournisseurs')},
]


def t(day, hm):
    return '2026-%s-%sT%s:00+02:00' % (day[:2], day[3:], hm)


def msg(frm, at, body, later=False):
    m = {'from': frm, 'at': at, 'body': fr(body)}
    if later:
        m['later'] = True
    return m


# ---------- the mailbox: [unread at the run, unread now] ----------
MAIL = [
    {'id': 'ostral', 'subject': fr('Ostral : remise demandée sur le renouvellement'), 'unread': [True, True], 'messages': [
        msg('Hugo Lefèvre <hugo@norvel.example>', t('09-30', '16:10'),
            "Camille, Ostral demande 18 % de remise pour renouveler sur 3 ans. Le contrat actuel est à 240 k€ par an. Leur DAF dit avoir une offre concurrente à moins 20 %. Si on accepte avant la fin du mois, le trimestre est sécurisé."),
        msg('Claire Martin <claire@norvel.example>', t('09-30', '18:40'),
            "Je ne suis pas d'accord sur 18 %. À ce niveau, la marge brute du compte passe sous 60 %. Je propose 12 % avec un engagement de 3 ans et une indexation ensuite. Pour mémoire, Brenner a signé à 15 % l'an dernier."),
        msg('Hugo Lefèvre <hugo@norvel.example>', t('10-01', '08:05'),
            "À 12 % on risque de les perdre. Je peux aller chercher 15 % avec un engagement ferme de 3 ans, mais il me faut une réponse aujourd'hui : ils veulent signer demain."),
        msg('Claire Martin <claire@norvel.example>', t('10-01', '09:32'),
            "Camille, il nous faut ton arbitrage avant ce soir : 18 %, 15 % ou 12 % ?"),
    ]},
    {'id': 'vellmar', 'subject': fr('Comité d\'investissement : rétention par cohorte'), 'unread': [True, True], 'messages': [
        msg('Marc Delorme <marc.delorme@vellmar.example>', t('09-30', '17:05'),
            "Bonjour Camille, avant notre comité d'investissement, pourriez-vous m'envoyer la rétention nette par cohorte sur les 8 derniers trimestres ? Le comité regardera de près la cohorte 2024. Merci, Marc"),
    ]},
    {'id': 'espagne', 'subject': fr('Head of Sales Espagne : les deux finalistes'), 'unread': [True, True], 'messages': [
        msg('Julie Moreau <julie@norvel.example>', t('09-29', '15:20'),
            "Camille, voici les deux finalistes pour diriger les ventes en Espagne. Carmen : 10 ans chez un concurrent direct, 160 k€. Pablo : parcours startup, plus junior, 120 k€. L'équipe penche pour Carmen, Hugo pour Pablo. Carmen a une autre offre et attend une réponse cette semaine."),
    ]},
    {'id': 'brenner', 'subject': fr('Avenant au contrat de transport'), 'unread': [True, False], 'messages': [
        msg('Étienne Girard <e.girard@brenner-logistique.example>', t('09-28', '11:00'),
            "Bonjour Madame Durand, vous trouverez ci-joint l'avenant relu par nos juristes et les vôtres. Pouvez-vous le signer d'ici la fin de la semaine ? Bien cordialement, Étienne Girard"),
        msg(ME_FROM, t('10-01', '11:50'), "Bonjour Étienne, signé et renvoyé ce matin. Bonne journée, Camille", later=True),
    ]},
    {'id': 'kerys', 'subject': 'Kerys', 'unread': [True, False], 'messages': [
        msg('Antoine Roche <antoine@kerys.example>', t('09-14', '10:00'), "Camille, as-tu eu le temps de regarder notre proposition de partenariat ?"),
        msg('Antoine Roche <antoine@kerys.example>', t('09-22', '09:30'), "Je me permets de revenir vers toi au sujet de Kerys."),
        msg('Antoine Roche <antoine@kerys.example>', t('10-01', '08:12'), "Camille, on en reparle ?"),
    ]},
    {'id': 'roux', 'subject': fr('Pacte d\'associés, version finale'), 'unread': [True, True], 'incoming': True, 'messages': [
        msg('Hélène Roux <h.roux@roux-avocats.example>', t('10-01', '11:55'),
            "Madame, le pacte d'associés dans sa version finale est prêt. Tous les investisseurs l'ont signé ; il manque votre signature pour clôturer la levée demain. Le lien de signature électronique est dans mon message précédent. Bien à vous, Hélène Roux"),
    ]},
    {'id': 'crm', 'subject': fr('Migration CRM : point d\'avancement'), 'unread': [True, True], 'messages': [
        msg('Léa Fontaine <lea@norvel.example>', t('10-01', '10:15'),
            "Point migration CRM : 92 % des comptes migrés, aucun blocage, bascule prévue la semaine prochaine. Rien à faire de ton côté."),
    ]},
    {'id': 'rh', 'subject': fr('Planning des entretiens annuels'), 'unread': [True, True], 'messages': [
        msg('Équipe RH <rh@norvel.example>', t('09-30', '14:00'), "Le planning des entretiens annuels est en ligne. Merci de valider vos créneaux avant la fin du mois."),
    ]},
    {'id': 'nimbus1', 'subject': fr('Nimbus Cloud : votre facture de septembre'), 'unread': [True, True], 'labels': ['Label_1'], 'messages': [
        msg('Nimbus Cloud <factures@nimbus.example>', t('10-01', '06:02'), "Votre facture de septembre est disponible : 4 812 € HT."),
    ]},
    {'id': 'rail', 'subject': fr('Votre reçu de paiement, Paris-Lyon'), 'unread': [True, True], 'labels': ['Label_1'], 'messages': [
        msg('RailGo <recus@railgo.example>', t('09-30', '19:20'), "Merci pour votre achat. Montant : 124 €."),
    ]},
    {'id': 'nimbus2', 'subject': fr('Nimbus Cloud : reçu de paiement'), 'unread': [True, True], 'incoming': True, 'messages': [
        msg('Nimbus Cloud <recus@nimbus.example>', t('10-01', '11:45'), "Nous avons bien reçu votre paiement de 4 812 €."),
    ]},
    {'id': 'lettredaf', 'subject': fr('La Lettre du DAF, n° 118'), 'unread': [True, True], 'labels': ['Label_2'], 'messages': [
        msg('La Lettre du DAF <news@lettredaf.example>', t('10-01', '07:00'), "Au sommaire : trésorerie, affacturage, clôtures plus rapides."),
    ]},
    {'id': 'decideurs', 'subject': fr('Décideurs IA : l\'édition de la semaine'), 'unread': [True, True], 'labels': ['Label_2'], 'messages': [
        msg('Décideurs IA <hebdo@decideurs-ia.example>', t('09-30', '08:00'), "Cinq cas d'usage en finance, et ce qu'ils ont coûté."),
    ]},
    {'id': 'saas', 'subject': 'Revue SaaS France, n° 42', 'unread': [True, True], 'labels': ['Label_2'], 'messages': [
        msg('Revue SaaS France <revue@saas-france.example>', t('09-29', '07:30'), "Les multiples de valorisation au troisième trimestre."),
    ]},
    {'id': 'salon', 'subject': fr('Salon Tech Paris : moins 30 % jusqu\'à dimanche'), 'unread': [True, True], 'labels': ['Label_3'], 'messages': [
        msg('Salon Tech Paris <promo@salontech.example>', t('09-30', '12:00'), "Dernières places à prix réduit."),
    ]},
    {'id': 'webinar', 'subject': fr('Invitation : l\'IA générative pour les équipes finance'), 'unread': [True, True], 'labels': ['Label_3'], 'messages': [
        msg('Optima Software <events@optima.example>', t('09-29', '16:00'), "Rejoignez notre webinar de 45 minutes."),
    ]},
]

# ---------- Slack direct messages ----------
SLACK = [
    {'channel': 'D0SOFIA1', 'uid': 'U0SOFIA', 'from': 'Sofia Benali', 'at': t('10-01', '10:41'),
     'text': fr("Camille, on est prêts pour la mise en production de la nouvelle facturation demain à 7 h. J'ai besoin de ton go écrit ici, le comité des changements l'exige depuis l'incident de juin. Tu confirmes ?"),
     'history': [fr("Sofia Benali : Les tests de charge sont passés, aucune erreur sur 50 000 factures.")]},
    {'channel': 'D0THOMAS1', 'uid': 'U0THOMAS', 'from': 'Thomas Petit', 'at': t('10-01', '09:05'),
     'text': fr("Bonjour Camille, le budget du séminaire de direction (18 k€) est-il validé ? Le lieu ne tient l'option que jusqu'à après-demain."),
     'history': []},
    {'channel': 'D0HUGO1', 'uid': 'U0HUGO', 'from': 'Hugo Lefèvre', 'at': t('10-01', '12:02'), 'incoming': True,
     'text': fr("Tu as 5 minutes avant ton call de 14 h ? Rien d'urgent."), 'history': []},
]


def last(th, at_run=True):
    ms = [m for m in th['messages'] if not (at_run and m.get('later'))]
    return ms[-1]


def name(frm):
    return frm.split('<')[0].strip()


def when(iso):
    """the right column: a clock for the run's day, a date before that"""
    d = iso[:10]
    if d == DAY:
        return {'kind': 'time', 'value': iso[11:16]}
    months = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']
    day = int(d[8:10])
    return {'kind': 'date', 'value': ('1er' if day == 1 else str(day)) + ' ' + months[int(d[5:7]) - 1]}


MAILS = {m['id']: m for m in MAIL}
SLACKS = {c['channel']: c for c in SLACK}


def mail_row(rid, tid, tier, kind, typ, say, fact, sources, briefing):
    th = MAILS[tid]; m = last(th)
    return {'id': rid, 'ref': 'thread:' + tid, 'tier': tier, 'channel': 'mail', 'kind': kind,
            'live': {'at': m['at'], 'from': name(m['from']).split()[0], 'thread': tid, 'account': ME['alias']},
            'say': fr(say), 'meta': when(m['at']), 'type': typ, 'argument': [fr(fact)],
            'sources': sources, 'briefing': fr(briefing)}


def slack_row(rid, ch, tier, kind, typ, say, fact, briefing):
    c = SLACKS[ch]
    return {'id': rid, 'ref': 'slack:' + ch, 'tier': tier, 'channel': 'slack', 'kind': kind,
            'live': {'at': c['at'], 'from': c['from'].split()[0], 'channel_id': ch},
            'say': fr(say), 'meta': when(c['at']), 'type': typ, 'argument': [fr(fact)],
            'sources': [{'kind': 'chat', 'via': 'Slack', 'label': c['from'].split()[0] + ', message direct', 'href': ''}],
            'briefing': fr(briefing)}


def src(label, kind='mail'):
    return {'kind': kind, 'label': fr(label), 'href': ''}


QUEUE = [
    mail_row('r1', 'ostral', 'now', 'decision', 'precedent',
             "Claire et Hugo attendent votre arbitrage sur la remise Ostral.",
             "Brenner a signé à 15 % l'an dernier, sur 3 ans.",
             [src('Claire Martin, échange Ostral'), src('Hugo Lefèvre, échange Ostral'), src('Contrat Brenner, 2025', 'doc')],
             "Ostral demande 18 % de remise pour renouveler sur 3 ans, à 240 k€ par an. Hugo veut accepter entre 15 et 18 % pour signer demain ; Claire refuse au-delà de 12 % pour garder la marge du compte au-dessus de 60 %. Brenner a signé à 15 % l'an dernier. C'est ce que je sais, un point de départ, pas le cadre.\n\nOuvre l'échange Ostral et le contrat Brenner. Puis :\n1. Dis-moi ce que chaque option fait à la marge et au trimestre.\n2. Donne-moi le meilleur argument pour chacune.\n3. Rédige ma réponse à Claire et Hugo pour l'option que je choisis. Ne l'envoie pas."),
    slack_row('r2', 'D0SOFIA1', 'now', 'action', 'history',
              "Sofia attend votre go écrit pour la mise en production de demain.",
              "Go écrit exigé depuis l'incident de juin.",
              "Sofia met en production la nouvelle facturation demain à 7 h et attend mon go écrit sur Slack, exigé depuis l'incident de juin. Les tests de charge sont passés. C'est un point de départ.\n\nOuvre ma conversation avec Sofia. Puis :\n1. Dis-moi ce qui pourrait encore bloquer, et qui serait d'astreinte.\n2. Rédige mon go, ou mes conditions, en une ligne. Ne l'envoie pas."),
    mail_row('r3', 'espagne', 'today', 'decision', 'knock_on',
             "Julie attend votre choix entre les deux finalistes Espagne.",
             "Carmen a une autre offre ; le lancement Espagne en dépend.",
             [src('Julie Moreau, finalistes Espagne')],
             "Julie attend mon choix entre Carmen (10 ans chez un concurrent, 160 k€) et Pablo (startup, plus junior, 120 k€) pour diriger les ventes en Espagne. L'équipe penche pour Carmen, Hugo pour Pablo, et Carmen a une autre offre. C'est un point de départ.\n\nOuvre le mail de Julie. Puis :\n1. Donne-moi le meilleur argument pour chacun, au regard du lancement Espagne.\n2. Dis-moi ce qu'il faudrait vérifier avant de trancher.\n3. Rédige ma réponse à Julie. Ne l'envoie pas."),
    mail_row('r4', 'vellmar', 'today', 'info', 'history',
             "Marc (Vellmar) veut la rétention par cohorte avant son comité.",
             "Même demande au dernier trimestre, envoyée la veille du comité.",
             [src('Marc Delorme, Vellmar Capital')],
             "Marc, de Vellmar Capital, veut la rétention nette par cohorte sur 8 trimestres avant son comité d'investissement, avec un regard sur la cohorte 2024. Au dernier trimestre, je l'avais envoyée la veille du comité. C'est un point de départ.\n\nOuvre le mail de Marc. Puis :\n1. Dis-moi qui chez nous peut produire ces chiffres, et d'où ils viennent.\n2. Rédige ma réponse à Marc avec un délai. Ne l'envoie pas."),
    slack_row('r5', 'D0THOMAS1', 'today', 'info', 'knock_on',
              "Thomas demande si le budget du séminaire est validé.",
              "Le lieu ne tient l'option que jusqu'à après-demain.",
              "Thomas demande sur Slack si le budget du séminaire de direction, 18 k€, est validé ; le lieu tient l'option jusqu'à après-demain. C'est un point de départ.\n\nOuvre ma conversation avec Thomas. Puis rédige ma réponse, oui ou non avec une condition. Ne l'envoie pas."),
    mail_row('r6', 'brenner', 'week', 'action', 'history',
             "Brenner Logistique attend votre signature sur l'avenant.",
             "Avenant relu par les juristes des deux côtés.",
             [src('Étienne Girard, Brenner Logistique')],
             "Brenner Logistique attend ma signature sur l'avenant au contrat de transport, relu par les juristes des deux côtés. C'est un point de départ.\n\nOuvre le mail d'Étienne et l'avenant. Puis dis-moi ce qui change par rapport au contrat, en trois lignes."),
    mail_row('r7', 'kerys', 'week', 'unclear', 'pattern',
             "Antoine relance sur Kerys sans dire ce qu'il attend.",
             "Troisième relance depuis la mi-septembre.",
             [src('Antoine Roche, Kerys')],
             "Antoine, de Kerys, m'a relancé trois fois depuis la mi-septembre au sujet d'un partenariat, sans dire ce qu'il attend de moi. C'est un point de départ.\n\nOuvre l'échange avec Antoine. Puis :\n1. Dis-moi ce qu'il propose réellement.\n2. Rédige une réponse qui lui demande ce qu'il attend, ou qui décline. Ne l'envoie pas."),
]

# the run's filed labels and the rest, as the run saw them
filed = []
tints = {'Factures': 'receipts', 'À lire plus tard': 'later', 'À archiver': 'arch'}
for lb in LABELS:
    xs = [m for m in MAIL if lb['id'] in (m.get('labels') or []) and not m.get('incoming') and m['unread'][0]]
    rule = [r['rule'] for r in RULES if r['label'] == lb['name']][0]
    f = {'id': 'f' + lb['id'][-1], 'label': lb['name'], 'tint': tints[lb['name']], 'count': len(xs), 'by_channel': {'mail': len(xs)},
         'contents': [{'channel': 'mail', 'from': name(last(x)['from']), 'what': x['subject'], 'href': ''} for x in xs[:5]], 'href': '',
         'briefing': fr("Ma boîte a classé %d non lus sous « %s », selon ma règle : « %s ». Rien n'a été archivé ni marqué comme lu.\n\nOuvre-les et dis-moi si l'un d'eux attend en fait quelque chose de moi." % (len(xs), lb['name'], rule)).replace('« ', '«' + NB).replace(' »', NB + '»')}
    if f['tint'] == 'arch':
        f['rules'] = [{'count': len(xs), 'rule': rule}]
    else:
        f['rule'] = rule
    filed.append(f)
in_queue = {r['live'].get('thread') for r in QUEUE}
labelled = {m['id'] for m in MAIL if m.get('labels')}
others = [m for m in MAIL if not m.get('incoming') and m['unread'][0] and m['id'] not in in_queue and m['id'] not in labelled]
others.sort(key=lambda m: last(m)['at'], reverse=True)
items = [{'channel': 'mail', 'from': name(last(m)['from']), 'what': m['subject'], 'href': '', 'when': when(last(m)['at'])['value']} for m in others]

counts_mail = sum(1 for r in QUEUE if r['channel'] == 'mail') + sum(f['count'] for f in filed) + len(items)
counts_chat = sum(1 for r in QUEUE if r['channel'] == 'slack')

seen = {}
for m in MAIL:
    if not m.get('incoming'):
        seen['thread:' + m['id']] = last(m)['at']
for c in SLACK:
    if not c.get('incoming'):
        seen['slack:' + c['channel']] = c['at']

LENS = fr("Camille Durand, directrice générale de Norvel, éditeur de logiciel de facturation (180 personnes), soutenu par le fonds Vellmar Capital.\n"
          "Priorités, dans l'ordre : 1. Clôturer la levée de série B ce mois-ci, avant tout nouveau recrutement. 2. Tenir la marge brute au-dessus de 60 %, avant la croissance à tout prix. 3. Lancer l'Espagne au premier trimestre.\n"
          "Sujets en cours : renouvellement Ostral (Hugo, Claire), mise en production de la facturation (Sofia), comité Vellmar (Marc), recrutement Espagne (Julie), partenariat Kerys (Antoine), levée de série B (Maître Roux).\n"
          "Personnes clés : Claire, Hugo, Sofia, Marc.\n"
          "Jamais dans la file sauf s'ils bloquent une priorité : newsletters, notifications, reçus, promotions.")

SUMMARIES = {
    'thread:ostral': {'who': [
        {'name': 'Hugo', 'date': 'hier', 'said': fr("Ostral demande 18 % pour renouveler 3 ans à 240 k€ par an ; il vise 15 % avec un engagement ferme, signature demain.")},
        {'name': 'Claire', 'date': 'ce matin', 'said': fr("Refuse 18 % : la marge passerait sous 60 %. Propose 12 % sur 3 ans, puis indexation.")}],
        'agree': [fr("Renouveler Ostral sur 3 ans, avec un engagement ferme.")],
        'disagree': [fr("Hugo accepte 15 à 18 % pour signer demain ; Claire tient à 12 % pour protéger la marge.")],
        'decide': fr("Quelle remise accordez-vous à Ostral : 18 %, 15 % ou 12 % ?")},
    'slack:D0SOFIA1': {'who': [
        {'name': 'Sofia', 'date': 'ce matin', 'said': fr("Mise en production de la facturation demain à 7 h, tests de charge passés sans erreur ; attend votre go écrit.")}],
        'agree': [], 'disagree': [], 'decide': fr("Donnez-vous le go pour la mise en production de demain matin ?")},
    'thread:espagne': {'who': [
        {'name': 'Julie', 'date': 'avant-hier', 'said': fr("Deux finalistes : Carmen, 10 ans chez un concurrent, 160 k€ ; Pablo, plus junior, 120 k€. Carmen a une autre offre.")}],
        'agree': [], 'disagree': [fr("L'équipe penche pour Carmen, Hugo pour Pablo.")],
        'decide': fr("Carmen ou Pablo pour diriger les ventes en Espagne ?")},
    'thread:vellmar': {'who': [
        {'name': 'Marc', 'date': 'hier', 'said': fr("Veut la rétention nette par cohorte sur 8 trimestres avant le comité d'investissement, surtout la cohorte 2024.")}],
        'agree': [], 'disagree': [], 'decide': ''},
    'slack:D0THOMAS1': {'who': [
        {'name': 'Thomas', 'date': 'ce matin', 'said': fr("Demande si le budget du séminaire de direction, 18 k€, est validé ; option sur le lieu jusqu'à après-demain.")}],
        'agree': [], 'disagree': [], 'decide': fr("Validez-vous le budget de 18 k€ pour le séminaire ?")},
    'thread:brenner': {'who': [
        {'name': 'Étienne', 'date': 'il y a 3 jours', 'said': fr("Envoie l'avenant relu par les deux juristes et demande la signature avant la fin de semaine.")},
        {'name': 'Vous', 'date': "aujourd'hui", 'said': fr("Avenant signé et renvoyé ce matin.")}],
        'agree': [], 'disagree': [], 'decide': ''},
    'thread:kerys': {'who': [
        {'name': 'Antoine', 'date': 'depuis la mi-septembre', 'said': fr("Trois relances sur une proposition de partenariat Kerys, sans dire ce qu'il attend.")}],
        'agree': [], 'disagree': [], 'decide': ''},
    'thread:roux': {'who': [
        {'name': 'Hélène Roux', 'date': "à l'instant", 'said': fr("Pacte d'associés final signé par tous les investisseurs ; manque votre signature pour clôturer la levée demain.")}],
        'agree': [], 'disagree': [], 'decide': ''},
}
DRAFTS = {
    'thread:ostral': fr("Claire, Hugo,\n\nJ'ai regardé vos arguments. On propose 15 % à Ostral, avec un engagement ferme de 3 ans et une indexation à partir de la deuxième année. Pas en dessous. Hugo, tu peux leur faire l'offre aujourd'hui.\n\nCamille"),
    'slack:D0SOFIA1': fr("Go pour demain 7 h. Préviens-moi dès que c'est en ligne, et s'il y a le moindre écart sur les premières factures, on revient en arrière."),
    'thread:espagne': fr("Julie,\n\nMerci pour ce travail. Je pars sur Carmen : l'expérience du marché compte plus que l'écart de salaire pour le lancement. Peux-tu lui faire une offre d'ici demain ?\n\nCamille"),
    'thread:vellmar': fr("Bonjour Marc,\n\nC'est noté. Claire vous envoie la rétention nette par cohorte sur 8 trimestres d'ici deux jours, avec le détail de la cohorte 2024.\n\nBien à vous,\nCamille"),
    'slack:D0THOMAS1': fr("Oui, budget validé à 18 k€. Tu peux confirmer le lieu."),
    'thread:kerys': fr("Bonjour Antoine,\n\nMerci pour tes relances. Avant d'aller plus loin, peux-tu me dire en deux lignes ce que tu attends de Norvel et dans quel délai ?\n\nCamille"),
    'thread:roux': fr("Bonjour Maître,\n\nMerci. Je signe dans l'heure.\n\nBien à vous,\nCamille Durand"),
}
SORT = {
    'lines': [{'id': 'm:roux', 'tier': 'now', 'say': fr("Maître Roux attend votre signature sur le pacte d'associés."),
               'fact': fr("Tous les investisseurs ont signé ; le closing est demain."), 'type': 'knock_on', 'kind': 'action'}],
    'labels': [{'id': 'm:nimbus2', 'label': 'Factures'}],
}

doc = {
    'lang': 'fr', 'date_label': 'jeudi 1 octobre', 'time_label': '11:30', 'today': DAY, 'gesture': 'copy',
    'sub': fr("Démonstration : personnes, entreprises et messages fictifs."),
    'links': {}, 'counts': {'mail': counts_mail, 'chat': counts_chat},
    'queue': QUEUE, 'filed': filed, 'wrote': True,
    'others': {'mail': len(items), 'chat': 0, 'items': items},
    'generated': RUN, 'seen': seen,
    'live': {'mail': {'server': 'Aureol Connect', 'api': 'aureol', 'label': True, 'read': True},
             'chat': {'server': 'Slack', 'api': 'slack'},
             'rules': RULES, 'lens': LENS,
             'demo': {'run_minutes_ago': 40, 'account': ME, 'me_id': 'U0CAMILLE', 'labels': LABELS,
                      'mail': MAIL, 'slack': SLACK, 'sort': SORT, 'summaries': SUMMARIES, 'drafts': DRAFTS}},
}
out = os.path.join(HERE, 'inbox-demo-fr.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)
print('%s: written, %d queue lines, %d unread mails, %d unread messages' % (out, len(QUEUE), counts_mail, counts_chat))
