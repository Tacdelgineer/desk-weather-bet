#!/usr/bin/env python3
"""Vertical Shorts (1080x1920, 30 fps) cut from the finished chapters: the wide shot in the middle, a hook on top for the
whole Short, the voiced sentences as captions underneath, a "full video" card at the end. Voice = the long video's take.

  python3 tools/shorts.py            -> results/final/shorts/S#_name.mp4 + shorts.txt (titles, times, captions)

The list lives in chapters/shorts.json:
  {"end_card": "FULL VIDEO ON THE CHANNEL",
   "shorts": [{"id": "S1_name", "chapter": "00", "from": "start phrase" | null, "to": "end phrase",
               "hook": ["LINE ONE", "LINE TWO"], "tail": 0.6}, ...]}
Segments are chosen by spoken phrases (first word of the start phrase → last word of the end phrase), so they follow the
take. "from": null = the chapter's first frame (keeps a payoff that plays before the voice). Hooks say only what the
clip shows; both lines shrink to fit 1000 px. Run with a python that has Pillow.
"""
import json, os, re, subprocess, sys
from PIL import ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit
ROOT = kit.ROOT; os.chdir(ROOT)
sys.path.insert(0, kit.SHORTS_TOOLS); import timing
CH = kit.chapters(); OUT = 'results/final/shorts'; os.makedirs(OUT, exist_ok=True); os.makedirs('work/shorts', exist_ok=True)
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
PAPER, INK, HOT = '0x0f0d0c', '0xf2eadd', '0xff7a21'
CFG = kit.load('chapters/shorts.json'); END_CARD = CFG.get('end_card', 'FULL VIDEO ON THE CHANNEL'); VIDEO_TITLE = kit.video()['title'].upper()
SHORTS = [(s['id'], s['chapter'], s.get('from'), s['to'], s['hook'], *([s['tail']] if 'tail' in s else [])) for s in CFG['shorts']]
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())

def find(words, phrase, after=0.0):
    toks = [norm(x) for x in phrase.split() if norm(x)]
    for i in range(len(words) - len(toks) + 1):
        if words[i]['start'] >= after - 1e-6 and [norm(w['text']) for w in words[i:i + len(toks)]] == toks: return i, i + len(toks) - 1
    sys.exit(f'phrase not found: {phrase}')

def esc(s): return s.replace('\\', '\\\\').replace("'", "’").replace(':', '\\:').replace('%', '\\%')

notes = []
for sid, n, a, b, hook, *tail in SHORTS:
    words = timing.load_words(f'voice/{n}.words.json')
    i0 = find(words, a)[0] if a else 0; _, i1 = find(words, b, words[i0]['start'])
    t0, t1 = max(0, words[i0]['start'] - .25) if a else 0, words[i1]['end'] + (tail[0] if tail else .6); dur = t1 - t0 + 2.2   # + end card
    src = f"results/final/chapters/{n}_{CH[n][0]}.mp4"
    caps = [(txt, s - t0, e - t0) for txt, s, e in timing.chunk_times(words, timing.load_chunks(f'chapters/{n}.chunks.txt')) if s >= t0 - .05 and e <= t1 + .05]
    vf = [f"[0:v]trim=start={t0:.3f}:end={t1:.3f},setpts=PTS-STARTPTS,scale=1080:608,tpad=stop_mode=clone:stop_duration=2.2[w]",
          f"color=c={PAPER}:s=1080x1920:d={dur:.3f}:r=30[bg]", "[bg][w]overlay=0:600[v0]"]
    last = 'v0'; k = 0
    def dt(text, y, size, col, en=None, box=False):
        global last, k
        f = f'work/shorts/{sid}_{k}.txt'; open(f, 'w').write(text)
        e = f":enable='{en}'" if en else ''
        b = f":box=1:boxcolor=0x0e0c0b@0.85:boxborderw=18" if box else ''
        vf.append(f"[{last}]drawtext=fontfile={BOLD}:textfile={f}:fontsize={size}:fontcolor={col}:x=(w-tw)/2:y={y}{b}{e}[v{k + 1}]"); last = f'v{k + 1}'; k += 1
    hs = min(76, int(76 * 1000 / max(ImageFont.truetype(BOLD, 76).getlength(h) for h in hook)))   # both hook lines fit in 1000 px
    dt(hook[0], 250, hs, INK); dt(hook[1], 350, hs, HOT)
    for txt, s, e in caps:   # wrap captions to ~26 chars a line, two lines max per card
        lines, cur = [], ''
        for wd in txt.split():
            if len(cur) + len(wd) + 1 > 26 and cur: lines.append(cur); cur = wd
            else: cur = (cur + ' ' + wd).strip()
        lines.append(cur)
        for j in range(0, len(lines), 2):
            part = lines[j:j + 2]; span = (e - s) / ((len(lines) + 1) // 2); ss = s + span * (j // 2)
            for q, line in enumerate(part): dt(line, 1300 + q * 80, 58, INK, f'between(t,{ss:.3f},{ss + span:.3f})')
    dt(END_CARD, 1600, 54, HOT, f'gte(t,{t1 - t0:.3f})', True)
    dt(VIDEO_TITLE, 1700, 34, INK, f'gte(t,{t1 - t0:.3f})')
    af = f"[0:a]atrim=start={t0:.3f}:end={t1:.3f},asetpts=PTS-STARTPTS,afade=t=out:st={t1 - t0 - .4:.3f}:d=0.4,apad=pad_dur=2.2,loudnorm=I=-14:TP=-1.5:LRA=11[a]"
    out = f'{OUT}/{sid}.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex', ';'.join(vf) + ';' + af, '-map', f'[{last}]', '-map', '[a]',
                    '-c:v', 'libx264', '-crf', '19', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000',
                    '-t', f'{dur:.3f}', '-movflags', '+faststart', out], check=True)
    notes.append(f"{sid}  ({dur:.1f} s)  from chapter {n} {CH[n][1]}, {t0:.1f}-{t1:.1f} s\n  hook: {' / '.join(hook)}\n  " + '\n  '.join(c[0] for c in caps) + '\n')
    print(out, f'{dur:.1f} s', len(caps), 'captions')
open(f'{OUT}/shorts.txt', 'w').write('\n'.join(notes))
