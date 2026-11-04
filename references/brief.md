# Brief de pré-production : deux tours au plus

Sans `brief.json` validé, on n'écrit pas. Tour 1 : cadrage en une salve (ou une ligne de confirmation si le sujet est donné). Tour 2 : choix d'un angle parmi les 3 du **Story architect**. Dans Claude Code, poser les questions avec **AskUserQuestion** (un seul appel, option recommandée en premier) ; ailleurs, une liste numérotée dans un seul message.

## Tour 1 : cadrage

| # | Question | Options (la première = défaut) | Clé |
|---|---|---|---|
| 1 | **Le geste** (seulement s'il manque) : quel geste quotidien du spectateur ramène-t-on 200 000 ans en arrière ? | libre : « fermer sa porte », « se laver », « dormir », « s'éclairer » ; ou « comme la vidéo X » | `subject` |
| 2 | **Durée** | `12 min` (défaut, ≈ 2 000 mots) · `11 min` · `14 min` · `16 min` (maximum) | `duration_min` |
| 3 | **Livrable** | production complète (défaut : script, images Flow, voix, montage avec musique, miniature, fiche de publication, Short) · script + shot list · script seul | `deliverable` |

Paramètres annoncés avec leur défaut, sans question (l'utilisateur les change dans la même réponse) :

| Paramètre | Défaut | Clé |
|---|---|---|
| Style | `troll-caveman` (norme 6), jamais un autre ; images par Google Flow piloté par Playwright (`scripts/flow`, `PLAYWRIGHT_DIR`) | `style`, `thumbnail_style` |
| Costume | « wearing a ragged leopard-spotted fur tunic, barefoot » ; par étape si la chaîne change d'époque (Rome : « the same white stick figure wearing a short white tunic ») | `character.costume`, `character.costumes_by_stage` |
| Décor | neutre : « each scene in its own place as described below, drawn as a fully painted set with depth and dramatic light » | `setting` |
| Voix | ElevenLabs `Brian`, `eleven_multilingual_v2`, style « deep, urgent documentary storyteller, steady pace, no pauses », `+0%` (clé `ELEVENLABS_API_KEY` dans le `.env`, demandée à l'utilisateur si absente) ; edge-tts seulement pour un pilote sur demande | `voice` |
| Musique | un drone sombre libre de droits fourni par l'utilisateur (`music.mp3` dans le dossier de travail) ; sans fichier, le montage est livré sans musique et la fiche le dit | `music` |
| Montage | `ffmpeg` (défaut) ou `hyperframes` (sous-titres animés mot à mot + titres cinétiques, rendu ≈ 1 h pour 12 min) | `editor`, `captions` (true/false) |
| Ton | « terrifying then grateful » (peur, gêne, ironie, gratitude) | `tone` |
| Série | numéro et vidéos déjà publiées **sur la chaîne de l'utilisateur** (pour ne pas refaire un geste) ; les 6 sujets de la chaîne de référence sont à refaire en anglais, c'est le but | `series` |

Si le sujet est déjà donné : une ligne de confirmation (« Fermer sa porte à clé, 12 min, production complète, troll-caveman, Brian : je lance les 3 angles ») et on passe au tour 2.

## Tour 2 : choix de l'angle

1. Lancer le **Story architect** (`agents.md`) avec le geste, les règles du format (structure et normes du `SKILL.md`), le brief du tour 1 et les vidéos déjà publiées.
2. Lancer en parallèle le **Packaging strategist** sur les 3 amorces du geste (`scripts/yt/keywords.py`) : un angle dont le titre n'a aucune requête réelle derrière lui est écarté ou reformulé. Présenter ses 3 angles : titre en deux questions, le geste d'ouverture en deux phrases, la chaîne des civilisations en 4 étapes, le piège, le twist moderne, 3 faits avec source probable, le moment gênant, une ligne de risque.
3. Une seule question : « Quel angle ? » A (Recommandé), B, C, autre.
4. Écrire `brief.json`, le relire en 3 lignes, passer aux faits.

## Format de `brief.json`

```json
{
  "format": "ancient-humans-video",
  "subject": "locking your bedroom door at night: privacy from the tribe of 20 to 50 to the hallway and the lock",
  "style": "troll-caveman",
  "thumbnail_style": "troll-caveman",
  "character": {"costume": "wearing a ragged leopard-spotted fur tunic, barefoot",
                "costumes_by_stage": [{"stage": "rome", "costume": "wearing a short plain white tunic"}], "sheet": null, "name": null},
  "setting": "each scene in its own place as described below, drawn as a fully painted set with depth and dramatic light",
  "voice_language": "en",
  "voice": {"engine": "eleven", "name": "Brian", "style": "deep, urgent documentary storyteller, steady pace, no pauses", "rate": "+0%", "model": "eleven_multilingual_v2"},
  "music": "music.mp3",
  "duration_min": 12,
  "tone": "terrifying then grateful",
  "deliverable": "script+production",
  "scenario": {"choice": "A", "title": "How Did Ancient Humans Get Privacy? And What Happened at Night in the Cave?",
               "gesture": "closing your door and turning the key twice", "trap": "walls and farming", "modern_twist": "the phone in your bed",
               "chain": ["tribe 200,000 years ago", "Çatalhöyük 9,000 years", "Roman foricae", "Egyptian tombs", "Greek idiotes", "Hammurabi", "pass-through palaces", "the hallway and the lock"]},
  "series": {"episode": 1, "previous_videos": []},
  "validated_by_user": true
}
```
