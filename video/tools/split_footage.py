#!/usr/bin/env python3
"""8.4 naming contract for the CapCut edit: cut each rendered chapter into its shots.

  python3 tools/split_footage.py

From results/final/chapters/NN_name.mp4 + work/audio/NN_meta.json (SPANS, video time) writes, under the repo's
results/: final_footage/wide/NN_chapter_shot.mp4 (1920x1080) and final_footage/vertical/… (1080x1920: the wide frame
over a blurred copy of itself), final_footage/ORDER.txt (NN | chapter | shot | one line | seconds), stat cards to
film-stats/S#_name_{wide,vertical}.mp4 and chart stills to filmpack/*.png. Video only (the voice lives in the master).
"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit
V = kit.ROOT; REPO = os.path.dirname(V); OUT = f'{REPO}/results'
for d in ('final_footage/wide', 'final_footage/vertical', 'film-stats', 'filmpack'): os.makedirs(f'{OUT}/{d}', exist_ok=True)
slug = lambda s: re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')[:40]
run = lambda *a: subprocess.run(['ffmpeg', '-v', 'error', '-y', *a], check=True)
# safe to re-run: skip an output that already exists and plays (a half-written file from an interrupted run is redone)
ok = lambda f: os.path.exists(f) and subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True).returncode == 0
def make(out, *a):
    if not ok(out): run(*a, out)
VERT = "split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:3,eq=brightness=-0.25[bg];[b]scale=1080:-2[fg];[bg][fg]overlay=0:(H-h)/2"
order, s_n = [], 0
for n, (name, title, *_) in sorted(kit.chapters().items()):
    src = f'{V}/results/final/chapters/{n}_{name}.mp4'; meta = json.load(open(f'{V}/work/audio/{n}_meta.json'))
    for k, sp in enumerate(meta['SPANS']):
        t0, t1 = sp['t0'], min(sp['t1'], meta['DUR']); shot = f"{k + 1:02d}_{slug(sp['name'])}"; base = f'{n}_{name}_{shot}'
        cut = ['-ss', f'{t0:.3f}', '-t', f'{t1 - t0:.3f}', '-i', src, '-an']
        make(f'{OUT}/final_footage/wide/{base}.mp4', *cut, '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', '30')
        make(f'{OUT}/final_footage/vertical/{base}.mp4', *cut, '-vf', VERT, '-c:v', 'libx264', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', '30')
        order.append(f"{n} | {name} | {shot} | {sp['name']}{' (RECORDING SLOT ' + sp['rec']['id'] + ')' if sp.get('rec') else ''} | {t1 - t0:.2f}")
        if sp['name'].startswith('stat card'):
            s_n += 1; sc = f'S{s_n}_{slug(sp["name"].replace("stat card", ""))}'
            for kind in ('wide', 'vertical'): make(f'{OUT}/film-stats/{sc}_{kind}.mp4', '-i', f'{OUT}/final_footage/{kind}/{base}.mp4', '-c', 'copy')
        if any(w in sp['name'] for w in ('race', 'Brier', 'per station', 'before/after', 'every miss', 'stress', 'judge vs')):
            make(f'{OUT}/filmpack/{base}.png', '-sseof', '-0.2', '-i', f'{OUT}/final_footage/wide/{base}.mp4', '-frames:v', '1')
open(f'{OUT}/final_footage/ORDER.txt', 'w').write('NN | chapter | shot | one line | seconds\n' + '\n'.join(order) + '\n')
print(len(order), 'shots,', s_n, 'stat cards')
