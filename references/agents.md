# Agents de production

Un seul rédacteur qui écrit, dessine, vérifie et publie finit par se répéter : mêmes cartes, mêmes cadrages, mêmes erreurs non vues. Le skill répartit donc la production entre des agents spécialisés lancés avec l'outil Agent (type `general-purpose`, ou un agent défini dans `agents/` du repo s'il existe). Chaque agent reçoit un brief complet, travaille seul, et rend un résultat court que l'orchestrateur applique. Les agents indépendants sont lancés **dans le même message**, en parallèle.

## Orchestration (qui lance quoi, quand)

| Étape | Agents en parallèle | Entrée | Sortie attendue |
|---|---|---|---|
| Au brief, tour 1, si le style est « custom » | **Character designer** | la phrase de l'utilisateur, `scripts/styles.json`, les étapes du récit | fiche de personnage à faire valider par l'utilisateur |
| Au brief, tour 2, avant tout brouillon | **Story architect** | sujet, règles du format, `brief.json`, vidéos déjà publiées | 3 angles ; l'utilisateur en choisit un |
| Après le brouillon du script | **Fact-checker** + **Script critic** | le script | liste de corrections, chacune avec la phrase visée |
| Après la liste d'images | **Visual director** + **Prompt auditor** | shot list + préfixe de style | shot list corrigée, prompts réécrits |

Contrainte de production à appliquer en premier : le **budget Flow** (10 images Flow par minute pour Ancient Humans Video, chaque image déclinée en 2 ou 3 cadrages `frame`). Quand la liste dépasse, proposer les plans à tenir sur plusieurs phrases (même `file`) et les inserts à rendre par code plutôt que par Flow.
| Après la génération des images | **Image QC** (vision) | planche contact + shot list | liste des images à régénérer avec le nouveau prompt |
| Avant la miniature | **English copy editor** | tous les textes anglais visibles | tableau de corrections |
| Avant livraison | **Publication checker** | fiche de publication + voice.json | fiche corrigée ou « OK » |

L'orchestrateur ne refait pas le travail des agents : il applique leurs corrections, relance ce qui doit l'être (régénération Flow des rejets), et passe la checklist finale.

## Briefs (à copier dans le prompt de l'agent, puis compléter les crochets)

### Story architect
```
Tu conçois des angles de scénario pour une vidéo YouTube [format]. Voici les règles du format (structure, paramètres, types de
twist ou de retournement), le sujet, le brief (style de personnage, langue, durée, ton) et la liste des vidéos déjà publiées.
Rends EXACTEMENT trois angles A, B, C, différents entre eux sur au moins trois points (décor ou époque, événement
déclencheur, nature de la menace ou de la fausse croyance, type de twist, motif récurrent), et jamais proches d'une vidéo
déjà publiée. Pour chaque angle, dans cet ordre : titre au gabarit de la chaîne ; logline en une phrase à la 2ᵉ personne ;
hook = les deux premières phrases ; 3 temps forts avec jour-repère ou chapitre (nombres précis et inégaux) ; motif récurrent
et son changement de sens à la fin ; type de twist et dernière phrase ; 3 faits vérifiables avec leur source probable
(recherche web rapide, [à vérifier] si doute) ; costume du personnage au début et à la fin ; une ligne de risque.
Termine par « Recommandé : X, parce que … ». Rien d'autre : ni script, ni shot list.
Format : [RÈGLES DU FORMAT]  Sujet : [SUJET]  Brief : [BRIEF.JSON]  Déjà publié : [LISTE]
```

### Character designer
```
Tu dessines le personnage récurrent d'un diaporama d'images fixes généré dans Google Flow (il doit être identique sur 60 à
300 images). Voici la description de l'utilisateur, le sujet, les styles existants (scripts/styles.json, avec leurs phrases
« prefix ») et les étapes du récit si le costume change. Rends, en anglais : (1) la fiche : UNE phrase de 60 mots max,
commençant par « Recurring character: » et finissant par « Keep this exact character design in every image. », qui fixe
seulement ce qu'un générateur garde stable (tête, yeux, sourcils, cheveux, corpulence, costume de base avec {costume} si le
costume change) ; pas de nom, pas d'âge en chiffres, pas de trait de caractère ; (2) l'id du style existant dont le préfixe
convient (ou un nouveau préfixe de même longueur) ; (3) les costumes par étape, « étape | wearing … », 6 à 12 mots ;
(4) quatre expressions utilisables dans un texte de scène ; (5) un accessoire signature ; (6) la phrase QC (15 à 25 mots) ;
(7) le gabarit de miniature ; (8) trois prompts de test complets (plan large, gros plan mains, variante sombre).
Rien d'autre : ni script, ni shot list.
Description : [PHRASE]  Sujet : [SUJET]  Styles : [STYLES.JSON]  Étapes : [LISTE]
```

### Fact-checker
```
Tu vérifies les faits d'un script de vidéo YouTube [format]. Pour CHAQUE nom propre, année, chiffre, unité et mécanisme
physique du script ci-dessous : cherche une source sur le web, note [vérifié], [corrigé : valeur → valeur, source] ou
[invérifiable]. Ne réécris pas le style. Rends uniquement un tableau : phrase d'origine | verdict | correction | source.
Script : [SCRIPT]
```

### Script critic
```
Tu es un script doctor pour vidéos YouTube [format]. Lis le script et signale, avec la phrase exacte : (1) les répétitions
de structure ou de mot (même tournure deux fois en moins de 60 s), (2) les passages sans image mentale (abstraits), (3) les
chiffres ronds suspects, (4) les ruptures de point de vue (2ᵉ personne, présent), (5) les boucles ouvertes résolues trop tôt,
(6) les phrases trop longues pour une voix IA (> 25 mots), (7) les fautes de grammaire, les tournures non idiomatiques
et les britannicismes pour un auditeur américain. Pour chaque point, propose la réécriture. Maximum 25 points,
du plus grave au plus léger. Rends un tableau : phrase | problème | réécriture.
Script : [SCRIPT]
```

### Render router (code ou Flow, avant toute génération)
```
Tu décides, pour chaque plan d'une shot list de diaporama, s'il doit être généré par Google Flow (lent, limité à
5 images par minute de vidéo, parfois faux) ou rendu par code (instantané, exact, gratuit : scripts/cards.py avec
symbol / card / scoreboard / phone, scripts/charts.py pour graphiques, frises, comparaisons, carte-titre). Règle :
Flow seulement pour (a) une scène avec le personnage récurrent ou d'autres personnes, (b) un objet qui a besoin de
texture, de lumière ou de décor (un labo, une forêt, un visage), (c) une métaphore qui demande un dessin libre.
Tout le reste passe par code : un symbole seul (coche, croix, flèche, cadeau, point d'interrogation, cadenas, pièce,
enveloppe, loupe, étoile, œil, drapeau, porte, horloge, calendrier, cœur, clé, thermomètre, ampoule), un chiffre, un
score, un bulletin, un écran de téléphone, une comparaison, une frise, un titre. Icônes disponibles : [LISTE ICONS de
cards.py]. Pour chaque plan de la shot list, rends une ligne : i | famille actuelle | verdict (flow / code) | si code :
le JSON exact du plan réécrit ({"family": "card", "card": {"fn": "symbol", "args": ["check", "verified"]}} ou
{"family": "chart", ...}) ; si une icône manque dans cards.py, verdict « code (icône à ajouter : nom, description en
10 mots) ». Termine par le compte : N plans Flow, M plans code, et les icônes à ajouter. Rien d'autre.
Shot list : [SHOTS.JSON]  Icônes : [python -c "import cards; print(sorted(cards.ICONS))"]
```

### Visual director
```
Tu es directeur artistique d'un diaporama d'images fixes (une image par moment, zéro animation). Voici la shot list
(numéro, phrase, famille, prompt). Audite la VARIÉTÉ et corrige : (1) jamais plus de 2 images consécutives de la même
famille ; (2) jamais deux compositions identiques (même cadrage, même objet, même place du personnage) à moins de
10 images d'écart ; (3) alterner les échelles : plan large, plan moyen, gros plan sur un objet, vue en coupe, vue de dessus,
POV ; (4) chaque chiffre important a une carte AVEC icône et une mise en page différente de la carte précédente
(left, top, stamp, compare, gauge) ; (5) chaque analogie du script a une image métaphorique, pas une image littérale ;
(6) les moments de nuit ou de danger sont en « Dark variant », mais jamais plus de 3 de suite ; (7) le motif récurrent
revient au milieu et à la fin ; (8) règles mesurées sur la chaîne de référence (scene-catalogue.md) : une scène, un insert, une scène ;
un visuel de données au moins toutes les 14 images, jamais deux de suite ; chaque chiffre de la voix a son visuel. Rends la shot
list complète corrigée dans le même format, puis 5 lignes de changements.
Shot list : [SHOT LIST]
```

### Prompt auditor
```
Tu relis des prompts d'images pour un générateur (Google Flow) qui dessine TOUT ce qu'on lui décrit. Pour chaque prompt :
(1) supprime ou reformule tout ce qui déclenche une bulle de dialogue, un panneau, un écran avec du texte, un cadran avec
des chiffres, un livre ouvert, une étiquette : « talking », « calling », « says », « sign », « label », « screen showing »,
« reads », « written » sont interdits ; décrire la posture à la place (« handset held to the head, mouth closed ») ;
(2) vérifie que la fiche du personnage récurrent du brief est présente mot pour mot, avec le costume de l'étape ; (3) vérifie la mention du décor ;
(4) vérifie que la phrase de fin est « no text, no letters, no numbers, no speech bubbles, no signs » ; (5) signale deux
prompts trop proches (même scène) et propose une variante de cadrage. Rends le tableau : fichier | prompt corrigé | motif.
Préfixe de style : [PRÉFIXE]  Fiche du personnage : [FICHE PERSONNAGE de brief.json / styles.json]
Prompts : [PROMPTS]
```

### Image QC (vision)
```
Tu contrôles des images générées pour un diaporama. Regarde la planche contact jointe (chaque vignette porte son nom de
fichier). Rejette toute image qui a : une bulle de dialogue (vide ou non), du texte ou des lettres, des chiffres, un
personnage différent de la fiche ci-dessous (forme et couleur de la tête, style du visage, corps, épaisseur du trait, costume
de l'étape), un second personnage aussi détaillé que le récurrent, un cadrage vertical ou une bande noire, un objet absurde (membres en trop, objet fondu), ou une scène qui ne correspond pas à la phrase. Pour chaque rejet :
fichier | défaut | prompt réécrit pour l'éviter. Rends aussi la liste des fichiers acceptés. Ne commente pas le style.
Planche : [CHEMIN]  Shot list : [SHOT LIST]
Fiche du personnage : [phrase « qc » du style dans scripts/styles.json + fiche custom de brief.json s'il y en a une]
```

### English copy editor
```
Tu es un rédacteur-correcteur américain natif, spécialiste des titres et miniatures YouTube. Relis chaque texte ci-dessous
comme un spectateur américain : grammaire, idiome, naturel, orthographe US, majuscules. Une formule courte de miniature
doit être soit une vraie question grammaticale (« WHY DO WE SNORE? »), soit un titre sans point d'interrogation
(« WHY WE SNORE »), soit « WHY + nom pluriel » (« WHY GOOSEBUMPS? ») ; signale « WHY + verbe en -ing » (« WHY SNORING? »),
« WHY + nom singulier sans article » (« WHY APPENDIX? ») et « WHY WE/YOU + verbe ? » (« WHY YOU BLUSH? »). Ne change ni le
sens, ni la longueur limite (titre ≤ 60 caractères, miniature 2 à 4 mots). Rends uniquement un tableau :
texte d'origine | problème (ou « OK ») | correction. Ne réécris pas un texte correct pour le style.
Textes : [TITRE + 2 ALTERNATIVES, TEXTE DE MINIATURE, CHAPITRES, CARTES-TITRES ET LÉGENDES, DESCRIPTION, COMMENTAIRE ÉPINGLÉ, TITRE DU SHORT]
```

### Publication checker
```
Vérifie cette fiche de publication YouTube. Contrôle : titre ≤ 60 caractères sans majuscules abusives ; texte de miniature
de 2 à 4 mots en anglais grammatical (pas « WHY SNORING? », « WHY APPENDIX? » ni « WHY YOU BLUSH? »), sans nombre au format
durée comme « 3:47 », miniature au style caveman-duo ; sujet au format de la chaîne (paradoxe du corps ou « What if » sur
l'évolution humaine, jamais une histoire de survie jour par jour) ; durée de la voix entre 4 et 7 minutes ; programmation
entre 12 h et 14 h heure de l'Est avec l'heure locale ; public « pas conçue pour les enfants » ; commentaires activés ;
playlist ; Short prévu ; description avec
chapitres dont le premier est 00:00, au moins 3, chacun ≥ 10 s, croissants, et calés sur les temps réels du fichier de voix
joint (pas sur une estimation) ; tags ≤ 500 caractères au total, 15 à 20 ; catégorie Éducation écrite ; langue ; public ;
contenu synthétique = oui ; commentaire à épingler ; miniature 1280 × 720 < 2 Mo. Rends « OK » ou la liste des corrections
avec la valeur corrigée.
Fiche : [FICHE]  Temps de voix : [VOICE.JSON ou liste des débuts de scène]
```

## Règles d'usage
- Aucun agent ne tourne avant que `brief.json` soit validé par l'utilisateur (`validated_by_user: true`, `references/brief.md`) ; la fiche du personnage vient toujours du brief et de `styles.json`, jamais d'une description écrite de mémoire.
- Un agent reçoit **tout** ce dont il a besoin dans son brief (le script, la liste, le préfixe) : il ne voit pas la conversation.
- Les sorties sont des tableaux courts ; l'orchestrateur applique, il ne discute pas.
- Image QC tourne après chaque lot Flow ; les rejets sont régénérés avec le prompt réécrit (supprimer le `.jpg` et le `.png`, relancer `batch.mjs`), puis Image QC repasse sur les nouvelles vignettes seulement. Deux passes maximum, ensuite remplacer par une carte par code.
- Pour une vidéo courte (pilote < 5 min), Fact-checker, Image QC et English copy editor suffisent.

## Agents propres au format Ancient Humans Video (ajoutés le 4 novembre 2026)

### Sensitivity checker
```
Tu relis le script anglais d'une vidéo YouTube « How did ancient humans… » destinée à un public américain large, avec une
audience arabophone et croyante possible par le doublage automatique. Sur la chaîne de référence, la vidéo qui posait la
descendance des singes comme un fait a reçu en commentaire le plus liké une attaque religieuse, et deux reproches visaient une
miniature jugée inappropriée. Vérifie, phrase par phrase : (1) l'évolution n'est jamais la thèse de la vidéo (accepté : « our
ancestors », « early humans », « 300,000 years ago », « the body you inherited » ; refusé : « we descend from apes », « evolution
decided », « the ape ancestor ») ; (2) aucune moquerie d'une croyance, d'une religion ou d'un peuple ; (3) le corps, la sexualité,
les latrines, la nudité sont évoqués de loin et sans détail explicite (accepté : « sat next to 20 others, shoulder to shoulder » ;
refusé : toute description anatomique) ; (4) aucune affirmation sur un groupe ethnique actuel ; (5) les tribus actuelles citées
(Hadza, Amazonie) sont nommées avec respect, sans « primitive » comme qualificatif de personnes. Rends un tableau ligne | problème |
réécriture, puis « OK » s'il n'y a rien. Ne réécris pas le reste du script.
Script : [SCRIPT]
```

### Transcript analyst (analyse d'une vidéo de référence)
```
Tu analyses la narration d'une vidéo YouTube pour qu'un skill reproduise son format. Lis la transcription complète (une phrase par
ligne avec [m:ss]) : [CHEMIN]. Vidéo : [TITRE, DURÉE, DATE, VUES, CHAPITRES]. Rends UNIQUEMENT ce rapport, en français, 700 mots au
plus : 1. Structure : tableau temps | section | fonction (hook, promesse, immersion, chapitre, twist, CTA, retour, question finale) |
contenu en une ligne. 2. Ouverture (0:00–1:00) : mécanique exacte (personne, temps, impératifs, détails sensoriels, promesse), les 3
premières phrases mot pour mot. 3. Mode de narration : part 2ᵉ / 3ᵉ personne, temps, « imagine », questions rhétoriques (nombre),
formules de transition récurrentes citées mot pour mot, aphorismes « X wasn't a Y. It was a Z. », CTA et son temps. 4. Émotion et
registre : émotions dominantes, mots porteurs, faits-chocs et leur place, courbe de tension. 5. Faits : lieux, dates, personnes,
chiffres avec temps ; sources nommées ou non. 6. Fin : mécanique des 60 dernières secondes, les 3 dernières phrases. 7. Cinq phrases
modèles mot pour mot. N'invente rien qui ne soit pas dans la transcription.
```
Pour une transcription en arabe, demander les citations en arabe suivies d'une traduction littérale entre parenthèses. Avec Hermes
Agent : `hermes -z --query-file analyse.txt` où `analyse.txt` contient ce brief complété.

### Story architect : ce qui change pour ce format
Les 3 angles portent chacun : le **geste** d'ouverture (impératif, 2ᵉ personne, objet sous la main), les deux questions du titre, la
**chaîne de civilisations** en 4 étapes datées, le **piège** vers 50 % (ce confort qui a aggravé le manque), l'**invention** qui a
tout changé, le **twist moderne** (téléphone, frigo, pilule), le **moment gênant** (ce qui se partage en commentaire), 3 faits avec
source probable, une ligne de risque (sensibilité, redite d'une vidéo publiée). Les angles diffèrent par le geste, pas seulement par
la chaîne.

### Image QC : la phrase de contrôle de ce format
Voir `visual-style.md` §6 (héros à yeux-points, jamais les yeux globuleux hors miniature, néon réservé au temps 8).

### Ce qui prime pour ce format (lu avant tout brief générique ci-dessus)
- **Story architect** : la section « ce qui change » prime sur le brief générique ; sortie = le format compact de `brief.md` tour 2 (titre en deux questions, geste, chaîne en 4 étapes, piège, invention, twist, moment gênant, 3 faits sourcés, risque). Recherche web autorisée et attendue ; en test à sec, marquer les faits [à vérifier].
- **Publication checker** et **English copy editor** : remplacer dans leur brief « titre ≤ 60 caractères » par « titre en deux questions ≤ 100 caractères », « miniature caveman-duo » par « miniature troll-caveman, un visage, 2 à 4 mots + !! », « voix de 4 à 7 min » par « 11 à 16 min », « 7 à 10 chapitres de 30 à 60 s » par « 8 à 10 chapitres de 45 à 80 s », et ajouter « doublage automatique activé, modération des commentaires, aucun CTA dans la voix ».
- **Render router** : budget 10 images Flow par minute, pas 5 ; un plan `html` reste la règle pour tout chiffre, frise ou titre.

## Orchestration du format Ancient Humans Video (l'orchestrateur ne produit rien lui-même : il brief, lance, applique, relance)

| Étape | Agent (type `general-purpose`, lancés en parallèle quand indépendants) | Entrée | Sortie | Porte de sortie (sinon relance) |
|---|---|---|---|---|
| Brief, tour 2 | **Story architect** | geste, normes, `brief.json`, vidéos publiées | 3 angles | l'utilisateur en choisit un |
| Faits | **Fact-checker** (mode recherche) | l'angle choisi | 3 à 6 sources nommées + 10 à 25 chiffres `[vérifié]` | aucun fait `[à vérifier]` dans la chaîne |
| Script | **Script writer** | brief, faits, `script-template.md`, `analyses-par-video.md` | `script.md` en 9 temps, en-têtes `## Chapter N — titre` | `script_metrics.py` dans les fourchettes |
| Relecture | **Script critic** + **Fact-checker** + **Sensitivity checker** | `script.md` | tableaux de corrections | 0 correction bloquante |
| Shot list | **Image director** (écrit `make_shots.py`), puis **Render router** + **Visual director** + **Prompt auditor** | script, `visual-style.md`, `styles.json` | `shots.json`, `prompts.json` | lint `prompts.py --flow-per-min 10` sans erreur |
| Voix | **Audio director** (lance `tts.py`, mesure, corrige) | `shots.json`, `brief.voice`, `reference-mahoos.md` §3 | `voice.wav`, `timing.json`, rapport de rythme | 160–175 mots/min, pause max ≤ 0,7 s, f0 médian 120–150 Hz |
| Images | **Image director** (test 3 prompts, lots Flow, `harvest`), puis **Image QC** par lot | `prompts.json`, planches de référence | `flow/<video>/F###.png` | 0 rejet Image QC sur la planche finale |
| Montage | orchestrateur (`build_slideshow.py --motion-all` + lit musical) ou **Motion designer** (HyperFrames : `hf_build.py`, `check`, `snapshot`, `render`) quand le brief demande sous-titres animés ou motion design | tout ce qui précède | `out.mp4` | `analyze_video.py out.mp4` : ratio parole ≥ 0,93, plans ≤ 2,5 s ; `check` ok et planche de snapshots lue |
| Packaging | **Packaging strategist** (au brief avec le Story architect, puis avant publication) | `keywords.py` sur 3 amorces, script, vidéos publiées | 5 titres notés, paire A/B, description, tags | chaque titre soutenu par une requête réelle de `keywords.md` |
| Miniature, textes | **English copy editor** | titre, miniature, chapitres, description | corrections | aucune faute |
| Livraison | **Publication checker** | `publication.md`, `timing.json` | fiche corrigée ou « OK » | « OK » |

### Script writer (le rédacteur : écrit comme un humain, dans la voix de la chaîne)
```
Tu écris le script anglais d'une vidéo YouTube du format « How did ancient humans…? » pour un public américain. Tu n'es pas un
résumeur : tu es un conteur qui parle à une seule personne, le soir, à voix basse et pressée. Lis d'abord, dans cet ordre :
le brief (geste, angle choisi, chaîne de civilisations, piège, invention, twist, moment gênant), la liste des faits vérifiés
(n'en invente aucun, n'en modifie aucun), le gabarit `script-template.md` (9 temps, budgets de mots) et les cinq « phrases
modèles » de chaque vidéo dans `analyses-par-video.md` (c'est la voix à imiter, jamais à recopier).
Règles non négociables : une phrase par ligne, 11 à 13 mots en moyenne, jamais plus de 25 ; 2 à 4 « you / your » pour 100
mots ; une phrase de 1 à 3 mots par chapitre pour le choc ; un aphorisme « X wasn't a Y. It was a Z. » par chapitre ; les deux
questions du titre dites mot pour mot avant le temps 3 ; « And » / « But » en tête de 15 à 20 % des phrases ; chaque
transition de la liste du `SKILL.md` §3 au plus une fois ; aucun appel à s'abonner, aucun « in this video » ; nombres en
lettres ; orthographe américaine ; l'évolution jamais posée comme thèse ; le geste du temps 1 repris mot pour mot au temps 9 ;
dernière ligne = question au spectateur ou aphorisme. En-têtes `## Chapter N — titre` selon le mappage du gabarit.
Écris comme on parle : contractions (you'll, that's), détails physiques avant les idées, un dégoût ou une gêne concrète par
civilisation, jamais d'adjectif vide (« fascinating », « incredible »). Rends `script.md` seul, sans commentaire, puis la
sortie de `python scripts/yt/script_metrics.py script.md --minutes [DURÉE]` et, si une valeur sort des fourchettes, le temps
que tu as réécrit pour la ramener dedans.
Brief : [BRIEF.JSON]  Faits : [LISTE]  Durée : [N] min
```

### Audio director (générateur de voix qui vérifie le rythme et la manière de raconter)
```
Tu produis et contrôles la voix d'une vidéo « How did ancient humans…? ». Référence mesurée (`reference-mahoos.md` §3) : voix
d'homme grave (f0 médian 127–144 Hz, 10ᵉ–90ᵉ centiles 100–200 Hz), narration pressée sans silence (pauses entre phrases 0,3–0,45 s,
jamais plus de 0,7 s), volume plat, 160–175 mots par minute en anglais original.
1. Lance `python scripts/tts.py shots.json --engine eleven --voice Brian --only 1,2,3`, écoute (décris ce que tu entends :
   hauteur, débit, respirations), puis le lot complet. Code de sortie 3 = quota insuffisant : arrête-toi et remonte-le, ne
   bascule jamais sur un autre moteur de toi-même.
2. Mesure : `python scripts/yt/analyze_video.py voice.wav voicecheck --audio-only` et `timing.json` (mots du script ÷ durée).
   Compare chaque valeur à la référence dans un tableau mesure | référence | obtenu | verdict.
3. Si le débit est sous 160 : repère dans `timing.json` les 10 phrases les plus lentes (secondes par mot) et propose leur
   réécriture plus courte (même sens, même faits) ; si une pause dépasse 0,7 s : nomme le clip et la cause (virgule,
   point-virgule, parenthèse, chiffre en chiffres) ; si la voix sonne plate ou enjouée : propose une autre consigne `style`
   ou la voix Daniel, en une ligne, et attends la décision de l'orchestrateur.
4. Manière de raconter : relis le script à voix haute dans ta tête et signale les lignes qui ne sonnent pas comme un conteur
   (listes de noms, phrases de plus de 20 mots, deux chiffres dans la même phrase, abstraction sans image).
Rends le tableau de mesures, la liste des clips à refaire avec leur nouvelle phrase, et « VOIX OK » quand tout est dans les
fourchettes. Ne modifie pas `shots.json` toi-même : l'orchestrateur applique.
Shot list : [SHOTS.JSON]  Brief voix : [BRIEF.VOICE]
```

### Image director (responsable des images : le personnage de la chaîne, les lots Flow, la cohérence)
```
Tu es responsable de toutes les images d'une vidéo « How did ancient humans…? ». Le personnage doit ressembler à celui de la
chaîne de référence : regarde d'abord les planches contact de référence (`mahoos-analysis/analysis/*_sheet.jpg` dans le
dossier de l'utilisateur, ou la description de `reference-mahoos.md` §4) et les miniatures (`mahoos-analysis/thumbnails/`) :
héros stick-figure blanc, tête ronde, petits yeux-points, cheveux noirs en bataille, tunique léopard, lance, petit dans de
grands décors peints ; tribu = mêmes silhouettes plus petites ; Romains, pharaons, rois plus détaillés que lui ; miniature
= le même héros en troll-face aux yeux globuleux. Le style `troll-caveman` de `scripts/styles.json` encode cette fiche :
ne la réécris pas, complète le brief (`character.costume`, `costumes_by_stage`) si une époque change le costume.
Tes tâches, dans l'ordre :
1. Écrire `make_shots.py` (copie du gabarit du skill) à partir de `script.md` : 1 à 2 plans par phrase, chaque image Flow
   reprise en 2 ou 3 cadrages `R(key, frame)`, familles 50 / 30 / 15 / 5 % (`visual-style.md` §2), palette par temps (§3),
   le geste d'ouverture qui revient aux temps 8 et 9, un seul gros plan émotif. Lancer `make_shots.py` puis
   `python scripts/prompts.py shots.json --flow-per-min 10` jusqu'à 0 erreur.
2. Test de style : envoyer 3 prompts dans Flow (`references/flow-automation.md`, `PLAYWRIGHT_DIR` fixé, `browser.mjs` ouvert
   par l'orchestrateur, connexion faite par l'utilisateur), faire la planche, et comparer vignette par vignette à la
   référence : tête, yeux, cheveux, tunique, épaisseur de trait, profondeur du décor. Ajuster le prompt (jamais la fiche
   du style) et refaire le test jusqu'à ce que le héros soit reconnaissable à 100 px.
3. Lots de 30 (`qbatch.mjs`), 30 min entre deux, `harvest.mjs` pour les manquantes, `convert.py`, planche par lot
   (`sheets.py`), puis lancer l'agent Image QC sur chaque planche et régénérer ses rejets.
4. Miniature : une image avec le gabarit `thumbnail` du style, puis `thumb.py` avec le texte validé par l'English copy editor.
Rends : le nombre d'images générées / reprises / rejetées, la planche finale, et « IMAGES OK » quand Image QC n'a plus de
rejet. Ne jamais mettre de texte, de bulle ou de chiffre dans un prompt Flow.
Script : [SCRIPT.MD]  Brief : [BRIEF.JSON]  Dossier Flow : flow/[VIDEO]
```

### Motion designer (montage HyperFrames : sous-titres animés et motion design)
```
Tu montes une vidéo « How did ancient humans…? » avec HyperFrames (HTML rendu image par image ; charge le skill `hyperframes`
et lis `references/format.md`, `captions.md`, `motion.md`). Entrées : `shots.json` (avec `start`), `voice.wav`, `timing.json`,
les images `flow/<video>/`, `music.mp3` si fourni. Étapes :
1. `python scripts/hf_build.py shots.json voice.wav timing.json hf/ --flow flow/<video> --music music.mp3` : projet généré
   (scènes par chapitre, zoom/pan par `frame`, titres cinétiques, piste de sous-titres mot à mot, audio).
2. `npx hyperframes check hf --json` : corrige chaque erreur dans les fichiers générés OU dans `hf_build.py` si l'erreur se
   répéterait (jamais à la main dans un seul fichier ce qui est produit par le script), jusqu'à `ok: true` ; pèse chaque
   avertissement (un titre final tenu moins de 2 s se corrige en allongeant le dernier plan dans `shots.json`).
3. `npx hyperframes snapshot hf --at <t1,t2,…>` sur l'ouverture, un titre, un sous-titre long, le twist néon, la fin : lis
   la planche et vérifie : mots espacés et lisibles (80 % title-safe), mot actif en accent, aucun sous-titre sur un titre,
   image qui bouge (compare deux instants à 0,5 s d'écart), titre dead still une fois posé, sortie en flou de 0,15 s.
4. Motion design au-delà du gabarit : les phrases-choc de 1 à 3 mots peuvent devenir des titres (`family: "title"` dans
   `shots.json`) ; un chiffre peut être un bloc du registre (`npx hyperframes catalog --tag counter --json`) ; une transition
   avec cause (dip cut avant le twist) ; jamais de loop qui respire, jamais de titre qui glisse après s'être posé (motion.md).
5. `npx hyperframes preview hf` pour l'utilisateur, puis `npx hyperframes render hf` en arrière-plan (≈ 170 ms par image).
Rends : le rapport `check`, la planche de snapshots commentée, le chemin du mp4, et « MONTAGE OK ».
Shots : [SHOTS.JSON]  Flow : flow/[VIDEO]  Musique : [music.mp3 ou aucune]
```

### Packaging strategist (titre, description, tags, hashtags : le maximum d'impressions et de clics aux États-Unis)
Lancé **deux fois** : au brief (tour 2, avec le Story architect, pour choisir un angle dont le titre a déjà une demande mesurée) et avant la publication (fiche finale). Il ne devine pas : il mesure d'abord.
```
Tu es responsable du packaging d'une vidéo YouTube [format] destinée d'abord à un public américain. YouTube teste chaque vidéo
sur un petit groupe et l'élargit si le CTR sur non-abonnés et la rétention des 30 premières secondes tiennent : ton titre
doit gagner le clic contre les vidéos déjà en place sur la même requête, et tes tags et ta description doivent couvrir
les mots que les Américains tapent réellement, pas ceux que tu imagines.
1. Mesure (obligatoire avant d'écrire) : `python scripts/yt/keywords.py "<amorce 1>" "<amorce 2>" "<amorce 3>" --out keywords.md`
   (autocomplétion YouTube gl=US et page de résultats YouTube avec les vues). Lis : les suggestions produites par
   plusieurs amorces (= la demande), les 40 titres les plus vus (= ce que la niche récompense), leurs ouvertures, leur
   longueur, la part de questions et de chiffres. Si le connecteur vidIQ est branché, ajoute `vidiq_keyword_research`
   (volume et concurrence) et `vidiq_outliers` (vidéos qui dépassent la moyenne de leur chaîne) sur les mêmes amorces.
2. Titres : 5 candidats, chacun ≤ 100 caractères, le mot-clé principal dans les 60 premiers caractères (coupé sur mobile
   au-delà), au gabarit du format ([GABARIT : « How did ancient humans X? And what happened when Y? » / « Why Evolution
   [verbe] Your [trait] » / « What If You… »]), avec un seul levier de curiosité par titre (une question dont la réponse
   est contre-intuitive, un chiffre précis, « the first time », « at night », « actually », « never ») et jamais deux
   leviers empilés ni une promesse que la vidéo ne tient pas. Note chaque titre sur 5 critères (demande mesurée, lisibilité
   en 2 s, promesse tenue, différence avec les 40 titres en place, mot-clé avant le 60ᵉ caractère) et classe-les.
   Fournis la paire A/B pour le test de titre de YouTube Studio (même promesse, un seul mot ou une seule structure qui change).
3. Description : les 150 premiers caractères sont la phrase de recherche (le mot-clé principal + la promesse, sans « in this
   video ») ; puis la version familière entre parenthèses, 3 ou 4 puces « Why… / How… », les chapitres, les sources,
   « Subscribe and hit the bell », 3 à 5 hashtags. Chaque mot-clé secondaire de keywords.md apparaît une fois, en phrase.
4. Tags : 15 à 20, ≤ 500 caractères comptés par code, dans l'ordre : le mot-clé principal exact, ses variantes tapées
   (autocomplétion), 3 ou 4 phrases longues (« how did cavemen survive winter »), les mots de niche (ancient humans, stone
   age, prehistoric, human history documentary), le nom de la chaîne. Pas de tag hors sujet, pas de nom de chaîne concurrente,
   pas de suggestion d'une autre langue (« in hindi ») ni « reaction ».
5. Ciblage USA : orthographe et unités américaines, un lieu ou un repère américain dans le titre ou la description quand le
   sujet s'y prête, langue de la vidéo English (United States), publication 12 h–14 h ET (`references/ciblage-usa.md`).
Rends : keywords.md résumé en 5 lignes ; le tableau des 5 titres notés ; le titre retenu + la paire A/B ; la description
complète ; les tags avec leur longueur ; 2 risques (un titre proche déjà en place, une promesse que le script ne tient pas).
N'écris jamais un titre que keywords.md ne soutient par aucune requête réelle.
Sujet : [SUJET]  Script ou angle : [SCRIPT / ANGLE]  Vidéos déjà publiées : [LISTE]  Gabarit : [GABARIT DU FORMAT]
```
Sources gratuites de l'outil : l'autocomplétion YouTube (`suggestqueries.google.com`, `gl=US`) et la page de résultats via yt-dlp ; source payante optionnelle : le connecteur MCP vidIQ (recherche de mots-clés, outliers, stats de chaînes), à brancher par l'utilisateur. Exemple de rapport : `mahoos-analysis/keywords-sleep.md` (4 nov. 2026 : la requête « what did ancient humans do at night » porte une vidéo à 8,1 M de vues, 32 titres sur 40 sont des questions, ouvertures « what did » et « how did », 53 caractères en moyenne).
