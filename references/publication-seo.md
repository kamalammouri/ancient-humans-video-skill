# Titre, miniature, chapitres, description, tags, doublage

## 0. Ce qui change pour Ancient Humans Video (4 novembre 2026)

Ce fichier reprend la fiche de publication générique de l'ancien skill explainer ; ses sections 1 à 6 restent valables (fiche de publication, heure ET, Short, doublage) sauf les points ci-dessous, qui priment.

| Champ | Ancient Humans Video |
|---|---|
| **Titre** | deux questions : « How did ancient humans [verbe] [objet]? And what happened when [première fois / at night / …]? », 11 à 17 mots, ≤ 100 caractères (`len(title)`), + 2 alternatives. Jamais une seule question (les deux vidéos sous 1 000 vues). |
| **Miniature** | gros plan du héros en troll-face + un accessoire + grotte bleu nuit ; texte 2 à 4 mots anglais + « !! » (« FIRST SUGAR!! », « NO PRIVACY!! ») par `scripts/thumb.py` ; un seul visage. |
| **Description** | ligne 1 = la question du titre + sa version familière entre parenthèses ; « In this video from [chaîne], we uncover… » ; 4 puces « • Why… • How… » ; chapitres (8 à 9, de 45 à 80 s, aux temps réels de la voix) ; « Subscribe and hit the bell 🔔 to uncover the secrets of the humans before us » ; 8 hashtags (#AncientHumans #StoneAge #HumanHistory #Prehistory …). |
| **Tags** | 15 à 20 en anglais, ≤ 500 caractères, les mêmes d'une vidéo à l'autre + 3 propres au sujet : ancient humans, early humans, stone age, prehistoric life, cavemen, how did ancient humans, human history, history documentary, animated history, [sujet] history, first [sujet]. |
| **Catégorie** | Éducation (la seule vidéo « People & Blogs » de la référence est à 637 vues). |
| **Doublage** | activer le doublage automatique (arabe, espagnol, portugais, hindi…) : la chaîne de référence doit ses titres anglais et une partie de ses vues à cette piste. |
| **Commentaires** | activés avec modération « Retenir les commentaires potentiellement inappropriés » et une liste de mots bloqués (insultes religieuses et ethniques) ; commentaire épinglé = la dernière question de la vidéo. |
| **Cadence** | une vidéo tous les 3 jours ; une suite sous 48 h quand une vidéo décolle (même geste, autre civilisation, ou « what happened at night » du même sujet). |
| **Short** | temps 1 + temps 2 (le geste + « remove… you will be shocked by a terrifying truth »), 35 à 55 s, recadré 9:16, publié le lendemain, vidéo associée = la longue. |


## 0-bis. Fiche de publication générique : toujours livrée, dans cet ordre, avec les remplacements du §0

Chaque livraison se termine par un bloc « Publication » prêt à coller dans YouTube Studio. Les oublis coûtent une relance : ne jamais omettre une ligne, même évidente.

| Champ | Valeur |
|---|---|
| Titre | un seul titre retenu + 2 alternatives |
| Description | bloc complet (hook, promesse, chapitres, suite, hashtags) |
| **Catégorie** | **Éducation** (Education), pour toutes les vidéos de la chaîne : la même catégorie partout aide YouTube à relier les vidéos entre elles et aux chaînes voisines |
| Tags | 15 à 20, **500 caractères au total maximum**, vérifier la longueur par code |
| Langue de la vidéo | English (United States), pour la vidéo et les métadonnées |
| Heure de publication | **18 h heure du Maroc pour The Hidden Bargain** (choix de l'utilisateur : 12 h à 14 h ET toute l'année, UTC+1 ou UTC+0 pendant le ramadan). Règle générale : **12 h à 14 h heure de l'Est**, jeudi à samedi de préférence, programmée dans Studio, jamais après 16 h ET. Donner la date et l'heure en ET **et** dans le fuseau de l'utilisateur, calculées par code : `python -c "from datetime import datetime;from zoneinfo import ZoneInfo as Z;t=datetime(2026,11,5,12,tzinfo=Z('America/New_York'));print(t.astimezone(Z('Europe/Paris')))"` (12 h ET = 18 h à Paris la plupart de l'année, 17 h pendant les semaines de décalage des changements d'heure). Puis l'onglet « Quand vos spectateurs sont sur YouTube » dès qu'il existe |
| Public | « Non, pas conçu pour les enfants » (sinon commentaires, écran de fin et recommandations sont coupés) |
| Commentaires | activés ; vérifier après la mise en ligne que la section commentaires s'affiche |
| **Short** | Short d'appel 9:16 (étape 10 du workflow), publié le lendemain de 12 h à 14 h ET, « Vidéo associée » = la vidéo longue. **Bloc Short complet, livré dans un fichier à part `short-titre-description-tags.txt` à côté de `short.mp4`** : titre ≤ 100 caractères (le mot-clé principal + un levier de curiosité, puis `#shorts`) et 2 alternatives ; description de 2 ou 3 lignes (la phrase d'accroche du Short, la question du titre de la longue, « ▶ Full story: [lien] ») puis 4 à 6 hashtags dont `#shorts` ; 8 à 12 tags ≤ 500 caractères (ils pèsent peu sur un Short) ; commentaire épinglé qui renvoie à la longue. |
| Contenu modifié ou synthétique | **oui** (voix et images générées par IA) : YouTube l'exige pour une voix réaliste |
| Miniature | fichier 1280 × 720, < 2 Mo, texte ajouté par code |
| Écran de fin | 5 dernières secondes : bouton Abonnement + emplacement « vidéo suivante » |
| Commentaire épinglé | la question posée à la fin de la vidéo, reformulée en une ligne |
| Playlist | la série du format |

## 1. Titre

Gabarit observé sur 28 titres sur 29 :

```
Why Evolution [verbe fort] [trait humain visible] ([parenthèse qui nie la réponse évidente])
```

- Verbes : Made, Gave, Let, Forced, Insisted on, Refused to, Allowed, Took Away, Invented, Ruined.
- Variante : « The [Real / Creepy / Strange / Shocking / Brilliant] Reason Evolution … ».
- Parenthèses qui marchent : « It's Not What You Think », « It Was Never A Beauty Trend », « You Won't Believe This », « The Reason is Crazy », « Every Blue Eyed Person Shares One Ancestor », « Doctors Still Won't Admit This ».
- Le format se transpose à d'autres forces : « Why Your Brain… », « Why Your Body… », « Why History… ».
- Proposer 3 titres et classer par force de la négation.

## 2. Miniature

Gabarit unique sur les 29 miniatures Apefully, confirmé par les miniatures à plus d'un million de vues des chaînes de référence (« ONLY 2 LEFT », « DAY 1. », « 1,000 OR 1? », « 1 MINUTE », « THE PRICE OF LUST. ») :

| Élément | Règle |
|---|---|
| Texte | 2 à 4 mots en anglais grammatical, relus par l'English copy editor (« WHY DO WE SNORE? » ou « WHY WE SNORE », jamais « WHY SNORING? », « WHY APPENDIX? » ni « WHY YOU BLUSH? »), jamais de nombre au format durée (« 3:47 »), majuscules, jaune vif (242,196,70) avec contour noir épais sur un bandeau bleu nuit en haut du cadre (`scripts/thumb.py`) |
| Formule | **un chiffre** (« 1 IN 13 », « ONLY 2 LEFT », « 1 MINUTE ») ou **une question** « WHY … ? » (WHY GOOSEBUMPS?, WHY BALD?!) ; proposer les deux, le chiffre d'abord |
| Personnages | un duo de mascottes récurrentes, expressives (choc, sueur, larmes), visage visible, style cartoon saturé, différent du style intérieur de la vidéo |
| Accessoire | un seul objet qui dit le sujet sans texte (banane, carte, bol, feu) |
| Décor | savane, coucher de soleil, nuit avec feu ; couleurs saturées |

Prompt de miniature :

```
Bold cartoon YouTube thumbnail, two expressive caveman mascots (man and woman in fur tunics,
messy brown hair, big eyes, stick limbs), [ÉMOTION], [ACCESSOIRE], [DÉCOR] at [MOMENT],
saturated colors, large empty area at the top for text, 16:9
```

Puis ajouter le texte « WHY … ? » en jaune (242,196,70) à contour noir par code (PIL, police Impact, contour 10 px, image 1280 × 720), jamais par le générateur d'images. Sur The Hidden Bargain, **toujours le duo caveman-duo** (gabarit `thumbnail` de `caveman-duo` dans `scripts/styles.json`), même si l'intérieur est en thin-line : les miniatures egg-headphones de Blush et Antarctic ont fait 37 et 18 vues. Pour une autre chaîne seulement, le personnage du brief peut remplacer le duo (pour `stickman-meme`, composition coupée en deux, perdant à gauche, gagnant à droite). Laisser le haut du cadre vide pour le bandeau de texte.

## 3. Chapitres

7 à 10 chapitres de 30 à 60 secondes (7 pour 5 min, 10 pour 7 min), nommés sur le modèle « The [Nom] of [Chose] » :
The Riddle of…, The Hidden Cost of…, The … Dilemma, What the Data Revealed, The … Mechanism, The Survival Trigger, The Rise of…, The Final Verdict.

Règles YouTube, sinon les chapitres ne s'affichent pas : le premier commence à `00:00`, au moins 3 chapitres, chacun d'au moins 10 secondes, dans l'ordre croissant. Format `mm:ss` suffisant sous une heure.

**Les horodatages viennent du minutage réel de la voix**, jamais d'une estimation : quand le fichier `voice.json` (fin de chaque caractère) existe, prendre le temps de fin de la phrase qui précède le début du chapitre. Sans voix générée, écrire « à caler après la voix » plutôt qu'un chiffre inventé. Les chapitres servent de mini-hooks dans la barre de lecture.

## 4. Description

```
#[Hashtag1] #[Hashtag2] #[Hashtag3]

[1 phrase qui reprend la question du titre et promet la réponse cachée.]

[Paragraphe de 120 à 180 mots, dense en mots-clés : reprendre le titre, nommer 4 à 6 concepts
scientifiques du script (noms de théories, d'hormones, de chercheurs), 2 ou 3 chiffres, et le
retournement final. Terminer par : « Your [organe] is not broken, it is… »]

[Question finale du script, mot pour mot, suivie de « Share your answer in the comments. »]

Subscribe for more animated documentaries on human evolution, prehistoric life and the mysteries of the human body.

CHAPTERS:
00:00:00 - [Chapitre 1]
00:02:36 - [Chapitre 2]
…

#[Hashtag1] #[Hashtag2] #[Hashtag3]
```

Catégorie YouTube : **Education**. Cocher la mention « contenu modifié ou généré par IA ».

## 5. Tags (15 à 20, **500 caractères au total maximum**)

YouTube refuse la sauvegarde au-delà de 500 caractères, virgules comprises : compter avant de livrer (`len(", ".join(tags))`) et retirer les tags les plus longs, jamais les génériques de niche. Trois familles, dans cet ordre :
1. **Génériques de niche avec « documentary »** (5) : human evolution documentary, evolutionary biology documentary, anthropology documentary, science documentary, evolutionary psychology.
2. **Questions en longue traîne** (8) reprises du script : why do so many people need glasses, why is childbirth so painful, why do men go bald.
3. **Concepts nommés** (4 à 6) : obstetric dilemma, antagonistic pleiotropy, inverted retina explained, GDF-15 pregnancy.

## 6. Doublage automatique et titres traduits

Activer dans YouTube Studio le doublage automatique et la traduction des titres et descriptions. La référence est servie en arabe, français, hindi, japonais, portugais, espagnol et plus de 15 autres langues : un spectateur français voit « La vraie raison pour laquelle l'évolution veut votre mort » et entend une voix française. C'est gratuit et invisible dans les statistiques publiques, mais c'est une part réelle de l'audience.

## 7. Cadence et série
- Une vidéo tous les deux jours au moins, pendant 30 jours avant de juger : Apefully a percé à la 6ᵉ vidéo ; Afterimath à la 1ʳᵉ (2,6 M) avec une vidéo tous les deux jours ; Monk Mode Films a enchaîné 6 parties de LUST VS LOVE en 9 jours après le succès de la première (2,1 M).
- Quand une vidéo décolle : une **suite dans les 48 h** (même sujet, autre angle ou « part 2 »), avec les liens vers les parties précédentes en description, comme Monk Mode Films et Chris Gu (« One Room series »).
- Description à la façon des références : logline en 2 ou 3 phrases, **une maxime d'une ligne** (« Motivation gets you started. Discipline keeps you going. »), la question au spectateur, les chapitres, les **sources** (Afterimath liste chaque étude citée), la ligne d'abonnement, 3 à 5 hashtags ; pour un sujet sensible (santé mentale, addiction), une ligne d'aide (« If this feels out of your control, you're not alone: findahelpline.com »).
- Carte finale « NEXT : [titre suivant] » 5 secondes ; une chaîne associée en collaboration (fonction « collab » de YouTube) partage les vues entre deux chaînes.

## 8. Posts YouTube (onglet Posts, ex-Communauté) : 4 posts par vidéo, agent **Community manager**
Vérifié le 5 novembre 2026 (aide YouTube « Create a post » et guides tiers ; refaire la vérification si Studio refuse un post).
- **Disponibilité** : Studio → Paramètres → Chaîne → Éligibilité des fonctionnalités ; les fonctionnalités avancées doivent être actives, sans avertissement en cours, et l'audience ne doit pas être « conçue pour les enfants ». Les anciens seuils de 500 ou 1 000 abonnés ne s'appliquent plus.
- **Types** : texte, image (une ou plusieurs), sondage texte (options ≤ 65 caractères), sondage image (options ≤ 36 caractères), quiz (une seule bonne réponse, révélée après le vote, avec une explication), vidéo (une vidéo ou un Short de la chaîne). 4 options au plus pour rester dans toutes les limites. YouTube limite le nombre de posts par 24 h : un post par jour au plus.
- **Image** : carrée 1:1, 1080 × 1080, JPG de moins de 16 Mo, faite par `scripts/thumb.py … --square=<x>` à partir d'une image Flow de la vidéo (bandeau de 2 à 4 mots facultatif, même lint que la miniature).
- **Calendrier** (cadence d'une vidéo tous les 3 jours, heure de publication 12 h–14 h ET) :

| Post | Quand | Type | Contenu |
|---|---|---|---|
| P1 | la veille | sondage (texte ou image) | la question du titre posée au spectateur (« How do you think ancient women handled their period? ») et 3 ou 4 réponses plausibles, dont celle de la vidéo ; pas de lien |
| P2 | 1 h après la mise en ligne | image + lien | l'image la plus forte de la vidéo, le geste d'ouverture en une phrase, la promesse, le lien, une question |
| P3 | le lendemain (jour du Short) | quiz | le fait le plus surprenant (`facts.md`), 3 ou 4 réponses, l'explication avec l'horodatage du chapitre et le lien |
| P4 | le surlendemain | sondage texte | « What should the next video be? » : 4 gestes de la banque d'idées (SKILL.md §1) ; le gagnant sert au choix du sujet suivant |

- **Rédaction** : anglais américain, 2ᵉ personne, 1 à 3 phrases avant le lien ou la question, 0 à 2 hashtags, pas de « smash like ». Les mêmes règles de sensibilité que la vidéo : sur un sujet intime, aucun mot cru dans l'image ni dans les options. Réponds aux premiers commentaires du post dans l'heure.
- **Livrable** : `posts-youtube.md` (type, date et heure ET + heure locale, texte prêt à coller, options, bonne réponse, image) et `posts/P1.jpg`…, copiés dans le dossier de livraison.
