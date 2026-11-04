# Les images : 30 plans par minute, toutes en mouvement

Mesuré sur les 6 vidéos de la référence (`reference-mahoos.md` §4) : une coupe toutes les 1,8 à 2,6 s, chaque image en zoom ou panoramique lent, une image nouvelle toutes les 15 à 20 s et des recadrages entre deux. Le style est `troll-caveman` (`scripts/styles.json`) ; `prompts.py` assemble chaque prompt Flow à partir de la fiche.

## 1. Décliner une image en plusieurs plans

Une phrase = 1 ou 2 plans. Une image Flow = 2 ou 3 plans consécutifs qui partagent le même `file` et changent de `frame` :

```json
{"i": 12, "sentence": "You are one member of a group of 20 to 50 people moving together through open spaces.", "family": "scene",
 "scene": "the character walking with a tribe of twenty small white stick figures across a wide golden savanna at dusk, spears on shoulders", "composition": "wide", "file": "F006", "frame": "wide"},
{"i": 13, "sentence": "You wake up with people around you, you eat with people around you.", "family": "scene", "file": "F006", "frame": "zoom"},
{"i": 14, "sentence": "You fight, cry, and rejoice in front of those same 20 people.", "family": "scene", "file": "F006", "frame": "pan-left"}
```

`build_slideshow.py --motion-all` rend chaque `frame` :

| `frame` | Mouvement | Quand |
|---|---|---|
| `wide` (défaut) | zoom avant lent, centré, 1,00 → 1,07 | la première apparition d'une image |
| `zoom` | zoom avant plus serré, 1,15 → 1,30, centré | la phrase qui précise, le visage, l'objet |
| `zoom-out` | 1,30 → 1,10 | la révélation du décor |
| `pan-left` / `pan-right` | 1,20 fixe, le cadre glisse d'un bord à l'autre | la tribu, une rangée (latrines), une frise |
| `left` / `right` | 1,25, ancré sur le tiers gauche ou droit, dérive légère | un personnage placé sur un côté |

Sans `frame`, `--motion-all` alterne zoom avant et arrière. Numérotation des fichiers : `F001`, `F002`… (trois chiffres, comme `make_shots.py`). Toujours poser `composition` sur une scène avec le héros : sans elle `prompts.py` fait tourner les cadrages et peut tirer un `close` hors du moment gênant. Les inserts `html`, `card`, `chart`, `title` restent fixes (comme sur la référence : la frise et la maison barrée ne bougent pas).

## 2. Budget et rythme

- **8 à 10 images Flow par minute** (`python scripts/prompts.py shots.json --flow-per-min 10`), soit 100 à 120 pour 12 min, en lots de 30 (`qbatch.mjs`, 30 min de pause entre deux lots).
- **Familles cibles** : scènes avec le héros 50 % ; scènes et objets sans le héros 30 % (`nochar: true` : éléphants, chocolat, une rangée de Romains, un parchemin) ; images symboliques sans le héros 15 % (`family: "metaphor"` : une double hélice d'ADN qui brille, un cerveau en coupe orange, une chambre minuscule flottant dans le noir, une main géante qui éteint le monde) ; symboles et chiffres 5 % (`html` : frise avec une date, chiffre, carte-titre, maison barrée de rouge).
- Jamais plus de 2 inserts de suite ; jamais 3 images sans le héros de suite dans les temps 3 et 4 ; un gros plan émotif du héros (`composition: "close"`, sueur, rougeur, yeux écarquillés mais **pas** les yeux globuleux de la miniature) au moment le plus gênant de la vidéo ; au moins un `overhead` (le village vu de haut) et un `pov`.
- L'image du geste d'ouverture (la chambre, la porte) revient au temps 8 en version néon et au temps 9 telle quelle : même `file` ou même scène regénérée.

## 3. Palette par temps

| Temps | Palette | Mot-clé de prompt |
|---|---|---|
| 1, 9 (le geste, aujourd'hui) | chambre sombre, une lampe chaude, bleu de la fenêtre | `dark: true` + « a modern bedroom, one warm bedside lamp, blue window light » (la variante sombre du style s'applique au lieu décrit, pas seulement à la grotte) |
| 2, 3 (la tribu) | crépuscule ocre et vert, feu de camp, nuit bleu marine avec des yeux qui brillent | `dark: true` pour la nuit |
| 4 à 7 (civilisations) | lumière peinte chaude, pierre, terre cuite, or pour les palais | « warm painted light, terracotta and sand » |
| 8 (twist moderne) | cyan et magenta néon, écran qui éclaire le visage, lignes de données | « glowing cyan and magenta neon light, holographic » (3 à 6 images seulement) |

Le changement de palette est le signal du retour au présent : ne jamais mettre de néon avant le temps 8.

## 4. Prompts : ce que la référence montre

- Le héros est **petit dans un grand décor** (plan large, horizon bas, beaucoup de ciel ou de voûte) sauf pour le gros plan émotif. Les décors sont peints avec profondeur, jamais plats.
- Les membres de la tribu sont les **mêmes silhouettes blanches, plus petites, sans cheveux marqués** ; les humains d'une civilisation (soldat romain, pharaon, roi) sont **plus détaillés et colorés** que le héros : « a detailed cartoon Roman soldier in red cloak and bronze helmet, drawn with more detail than the white stick figure ».
- Les objets porteurs du sujet en gros plan sans personnage : « a close-up of a broken bar of dark chocolate on a wooden table », « a steaming cup of coffee with a sugar cube dropping in ».
- Le gênant est montré **de loin et de dos** (la rangée de latrines vue de côté, les corps blancs sans détail), jamais explicite.
- Mots interdits dans un prompt (lint de `prompts.py`) : `talking, sign, label, poster, map, screen showing, reads, written, number, letters` ; les objets à texte sont « plain, blank, unmarked ».

## 5. Miniature

Gabarit `thumbnail` du style : le héros redessiné en troll-face (yeux globuleux injectés de sang, pupilles minuscules, bouche tremblante, sueur, rougeur), en très gros plan sur les deux tiers inférieurs, un accessoire qui dit le sujet (un cube de sucre géant, un tas de sel blanc, une lance plantée, une couverture tirée jusqu'au nez), grotte bleu nuit et feu de camp, « two small tribe members peeking from behind a rock » si la gêne vient des autres, bande vide en haut. Texte par `scripts/thumb.py` (2 à 4 mots + « !! », jaune Impact, contour noir).

## 6. Image QC (phrase à donner à l'agent)

« Héros : tête blanche ronde à petits yeux-points, cheveux noirs en bataille, tunique léopard, membres fins, lance ; pas d'yeux globuleux hors miniature ; tribu = mêmes silhouettes plus petites ; aucune bulle, aucun texte, aucun chiffre ; décor peint avec profondeur ; palette du temps respectée (néon seulement au temps 8). » Rejeter aussi : visage réaliste, personnage en double, décor plat, tunique qui change de motif.
