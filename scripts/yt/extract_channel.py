#!/usr/bin/env python3
"""Extrait les métadonnées publiques d'une ou plusieurs chaînes YouTube (titres, durées, vues, dates, likes).
Usage: python3 extract_channel.py @handle1 @handle2 ... [--max 15]
Nécessite yt-dlp (pip install yt-dlp). Ajoute --no-check-certificate si un proxy bloque le SSL.
"""
import subprocess, sys, json

args = [a for a in sys.argv[1:] if not a.startswith('--')]
maxn = '15'
if '--max' in sys.argv:
    maxn = sys.argv[sys.argv.index('--max') + 1]

for h in args:
    h = h if h.startswith('@') else '@' + h
    url = f'https://www.youtube.com/{h}/videos'
    # 1) liste rapide (sans dates)
    r = subprocess.run(['yt-dlp', '--no-check-certificate', '--flat-playlist', '-J', url],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
    except Exception:
        print(f'{h}: échec extraction ({r.stderr[-200:]})'); continue
    print(f"\n=== {d.get('channel')} | abonnés: {d.get('channel_follower_count')} | {len(d.get('entries', []))} vidéos listées")
    print('Description:', (d.get('description') or '')[:300].replace('\n', ' '))
    # 2) détails (dates, likes) – peut être limité par YouTube, on reste poli
    r2 = subprocess.run(['yt-dlp', '--no-check-certificate', '--sleep-requests', '1', '--playlist-end', maxn,
                         '--print', '%(upload_date)s | %(duration)s s | %(view_count)s v | %(like_count)s L | %(comment_count)s C | %(title).70s', url],
                        capture_output=True, text=True)
    lines = [l for l in r2.stdout.splitlines() if l.strip()]
    if lines:
        print('\n'.join(lines))
    else:
        for e in d.get('entries', [])[: int(maxn)]:
            print(f"{e.get('duration')} s | {e.get('view_count')} v | {e.get('title')}")
