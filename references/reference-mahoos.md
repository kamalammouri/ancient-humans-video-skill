# La chaîne de référence, mesurée le 4 novembre 2026

« المهووس - الإنسان قبلنا » (« The Obsessed : the human before us »), https://www.youtube.com/@Mahoos-beforeUs. Narration en arabe égyptien, doublage automatique YouTube en anglais activé depuis la 3ᵉ vidéo (piste « English (US) »), 1 300 abonnés au moment de la mesure, 6 vidéos en 17 jours, environ 333 000 vues cumulées. Outils : `scripts/yt/extract_channel.py` (liste), `yt-dlp -J` (métadonnées), `scripts/yt/analyze_video.py` (parole, pauses, hauteur, plans, planche contact), `scripts/yt/script_metrics.py` (texte), agents sur les transcriptions (`analyses-par-video.md`).

## 1. Les six vidéos

| Date | Titre (traduit) | Durée | Vues | Likes | Comm. | Débit | Plans (médiane) | Voix f0 méd. |
|---|---|---|---|---|---|---|---|---|
| 17 oct. | Ancient humans lived 300,000 years without progress. Why did they suddenly evolve? | 8:10 | 730 | 20 | 1 | 127 mots/min (ar) | 216 (1,96 s) | 128 Hz |
| 22 oct. | What did ancient humans do during endless rain? | 6:49 | 637 | 14 | 0 | 139 mots/min (ar) | 146 (2,56 s) | 127 Hz |
| 25 oct. | How did ancient humans discover sugar? And what happened when they tasted it for the first time? | 16:11 | 56 412 | 534 | 81 | 176 mots/min (en) | 426 (2,10 s) | 132 Hz |
| 28 oct. | How did ancient humans discover salt? And what happened when they tasted it for the first time? | 12:30 | 32 580 | 177 | 4 | 167 mots/min (en) | 363 (1,96 s) | 131 Hz |
| 31 oct. | How did ancient humans overcome deadly diseases? And how was the first surgery performed? | 11:09 | 5 157 | 63 | 6 | 182 mots/min (en) | 340 (1,83 s) | 144 Hz |
| 2 nov. | How did ancient humans gain privacy? And what happened at night in the cave? | 14:53 | 237 674 | 2 534 | 114 | 196 mots/min (en) | 452 (1,88 s) | 143 Hz |

Débit « en » = piste doublée automatiquement, compressée dans le minutage arabe (donc rapide) ; le débit natif arabe est 127 à 139 mots/min. Cible pour une narration anglaise originale : **160 à 175 mots/min**, voir §3.

Ce qui sépare les deux vidéos à moins de 1 000 vues des quatre suivantes : titre en une seule question sans « And what happened when… » ; pas de doublage anglais ; miniature avec un groupe au lieu d'un gros plan de visage ; une catégorie « People & Blogs » (la pluie) au lieu d'« Éducation » ; durée sous 9 min. Corrélations sur 6 vidéos, pas des preuves. La vidéo phare ajoute un sujet-tabou universel (la pudeur, la nuit dans la grotte) et un couple gêné en miniature.

## 2. Le texte (mesuré sur les 4 transcriptions anglaises)

| Mesure | Sucre | Sel | Maladies | Privacy (phare) |
|---|---|---|---|---|
| Mots | 2 853 | 2 084 | 2 030 | 2 924 |
| Phrases | 214 | 154 | 188 | 237 |
| Mots par phrase | 13,3 | 13,5 | 10,8 | 12,3 |
| Phrases ≤ 4 mots | 4 % | 7 % | 11 % | 3 % |
| Phrases ≥ 25 mots | 6 % | 8 % | 6 % | 7 % |
| « you / your » pour 100 mots | 1,4 | 1,0 | 1,9 | **3,8** |
| Nombres par minute | 2,6 | 1,8 | 2,2 | 0,7 |
| Questions | 7 | 3 | 9 | 4 |
| Phrases ouvertes par « And » | 34 | 37 | 27 | 46 |
| Phrases ouvertes par « But » | 9 | 3 | 10 | 16 |
| CTA abonnement dans le script | 0 | 0 | 0 | 0 |

Lecture : la vidéo qui a explosé est celle qui parle le plus au spectateur (3,8 « you » pour 100 mots, le double des autres) et qui porte le moins de chiffres (un sujet de sensation, pas de données). Les vidéos « sucre » et « sel » compensent par des chercheurs nommés ; « maladies » par des lieux et des dates. Dans tous les cas : phrases courtes (11 à 13 mots), une phrase de 1 à 3 mots pour le choc (« Isolation meant. Death. »), un aphorisme « X wasn't a Y. It was a Z. » par chapitre, et **aucun appel à s'abonner dans la voix** (le CTA est dans la description et le commentaire épinglé).

Structures complètes, formules de transition et fins : `analyses-par-video.md`.

## 3. La voix

| Mesure | Valeur sur les 6 vidéos | Ce que ça impose |
|---|---|---|
| Ratio parole / durée | 0,86 (première vidéo) → 0,94–0,975 (quatre dernières) | un lit musical continu sous la voix : jamais de silence pur |
| Pauses ≥ 0,3 s | 8 à 13 par minute sur les 2 premières (max 0,64 s), aucune détectable sur les 4 dernières (musique) | pauses courtes entre phrases (0,3–0,45 s), pas de « silence-arme » |
| Hauteur (pyin, 3 fenêtres de 60 s) | médiane 127–144 Hz, 10ᵉ–90ᵉ centiles 100–200 Hz | voix d'homme grave et expressive, pas monotone |
| Volume moyen par 10 s | −11 à −15 dB, plat du début à la fin, fondu final seulement | compression régulière, pas de crescendos musicaux |
| Débit natif | 127–139 mots/min en arabe ; 167–196 en doublage anglais | en anglais original : 160–175 mots/min, « +0% » à « +5% » sur edge-tts |

Le ton (transcriptions et écoute) : un conteur qui s'adresse à toi, grave, pressé, qui annonce l'horreur et la surprise (« terrifying », « shocking », « nightmare ») mais finit sur la gratitude. Rien d'ironique dans la voix elle-même : l'ironie est dans les mots.

## 4. L'image

| Mesure | Valeur | Ce que ça impose |
|---|---|---|
| Coupes | une toutes les **1,8 à 2,6 s** (médiane), 90ᵉ centile 3 s ; 146 à 457 plans par vidéo | ≈ 30 plans par minute, presque 2 plans par phrase |
| Mouvement | **toutes** les images bougent (zoom ou panoramique lent : différence de 4 à 12 niveaux de gris en 0,4 s, 35 à 85 à la coupe) | jamais une image fixe : `--motion-all` au montage |
| Images distinctes | la planche contact montre une image nouvelle environ toutes les 15 à 20 s ; les coupes intermédiaires sont des recadrages ou des variantes de la même scène | 8 à 10 images générées par minute, chacune déclinée en 2 ou 3 cadrages (clé `frame` de `shots.json`) |
| Familles (lecture des planches) | ≈ 50 % scènes avec le héros dans un décor peint profond, ≈ 30 % scènes et objets sans le héros (éléphants, chocolat, latrines romaines, parchemin), ≈ 15 % inserts « science » lumineux (ADN, cerveau, cellule, hologramme), ≈ 5 % symboles (maison barrée de rouge, frise « 200,000 YEARS AGO », tablette) | tout ce qui est abstrait reçoit une image concrète et lumineuse |
| Palette | crépuscule chaud (ocre, orange, vert) pour la vie ; bleu nuit et feu de camp pour la grotte ; cyan et magenta néon pour le présent numérique (le twist) | le changement de palette signale le retour au présent |
| Texte dans l'image | rare : une frise avec une date, une tablette gravée, des enseignes romaines (« FORICA ») | les chiffres restent par code (cartes), jamais demandés à Flow |
| Personnage | héros stick-figure blanc, tête ronde, yeux-points, cheveux noirs en bataille, tunique léopard, lance ; tribu = mêmes silhouettes plus petites ; Romains, pharaons, rois dessinés en humains plus détaillés | style `troll-caveman` de `scripts/styles.json` |
| Miniature | gros plan du héros en troll-face (yeux globuleux injectés de sang, sueur, rougeur), un accessoire (cube de sucre, tas de sel, lance dans la tête), grotte bleu nuit, texte arabe jaune-vert à contour noir, 2 à 3 mots + « !! » | `thumb.py` avec texte anglais de 2 à 4 mots + « !! » |

## 5. Packaging

- **Titre** : deux questions, « How did ancient humans [verbe] [objet]? And what happened when [première fois / la nuit / …]? » ; 11 à 17 mots ; la seconde question est la promesse (« what happened at night in the cave »).
- **Description** : première ligne = la question + la variante en dialecte entre parenthèses ; « In this video from the channel X, we uncover… » ; 4 puces de teasing ; chapitres (8 à 9 de 45 à 80 s) ; 8 hashtags ; « Subscribe and hit the bell ».
- **Tags** : 15, en arabe, répétés d'une vidéo à l'autre (« الإنسان القديم », « العصر الحجري », « تاريخ البشرية », le nom de la chaîne).
- **Catégorie** : Éducation (5 sur 6 ; la seule « People & Blogs » est à 637 vues).
- **Cadence** : une vidéo tous les 3 jours (17, 22, 25, 28, 31 oct., 2 nov.).
- **Doublage** : piste anglaise automatique sur les 4 dernières (c'est ce qui donne les titres anglais dans la liste de la chaîne pour un spectateur anglophone).

## 6. Les commentaires (deux vidéos, 92 commentaires lus)

- **Sucre (56 k vues)** : le commentaire le plus liké (20) attaque la théorie de l'évolution (« كفر », « ملحد »), 8 autres dans le même sens ; « فيه معلومات خطأ كثير » (10) ; « المصدر ؟ » (0). La vidéo nommait l'ancêtre commun des singes et des humains.
- **Privacy (237 k vues)** : « باختصار : نحن نعيش في نعمة » (27), « الحمد لله » (15), « محترف حبيت محتواك » (21), blagues sur les invités qui dorment à côté (10) ; deux reproches sur la miniature (« صورة المقطع », « ليست مناسبة ») ; « quel logiciel pour les dessins ? » (5).

Conséquence pour une version anglaise : le public arabophone sanctionne l'évolution dite comme un fait ; un public américain la sanctionne moins mais le même réflexe existe dans une partie de l'audience. Règle du skill : dire « our ancestors », « early humans », « 300,000 years ago » sans jamais poser la descendance des singes comme thèse de la vidéo ; les sources nommées (chercheur + année) désamorcent « source ? ».
