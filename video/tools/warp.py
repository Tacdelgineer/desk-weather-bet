#!/usr/bin/env python3
"""Line the locked footage up with the voice: each shot starts on the phrase its SCRIPT.md Shots line names.

  python3 tools/warp.py [NN ...]     (no args: every chapter with a voice take)

For chapter NN: page shot starts come from the page itself (pageData SPANS, built without a warp); voice times from
voice/NN.words.json (after mute.py, leads included). Writes chapters/NN.warp.json:
  {"video_dur": s, "warp": [[video time, page time], ...]}  — anchors at every shot start, then the end.
tools/mkroom.py embeds it (WARP + DUR = video length), so core.js plays the footage on the voice's clock.
Project tool; the shot list's k-th quoted phrase belongs to the page's k-th shot. Shots and phrases must match 1:1.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit
ROOT = kit.ROOT
TAIL = 1.4          # seconds of picture after the last word
MIN_LAST = 3.0      # the last shot is never shorter than this on screen
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())


def shot_cues():
    txt = open(os.path.join(ROOT, kit.video()['script']), encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'^## (\d+)\. .*?\n\*\*Shots\*\*\n(.*?)(?:\n\*\*Check\*\*|\Z)', txt, re.S | re.M):
        cues = []
        for line in m.group(2).splitlines():
            if not line.startswith('- '): continue
            q = re.match(r'- "([^"]+)"', line)
            cues.append(q.group(1) if q else None)      # None = the shot at 0 (before the first word)
        out[f'{int(m.group(1)):02d}'] = cues
    return out


def find(words, phrase, after):
    toks = [norm(t) for t in phrase.split() if norm(t)]
    W = [norm(w['text']) for w in words]
    for i in range(len(W) - len(toks) + 1):
        if words[i]['start'] >= after - 1e-6 and W[i:i + len(toks)] == toks: return words[i]['start']
    raise SystemExit(f'cue not in take: "{phrase}" after {after:.2f}')


CUES = shot_cues(); CH = kit.chapters()
for n in sys.argv[1:] or sorted(n for n in CH if os.path.exists(f'{ROOT}/voice/{n}.words.json') and n in CUES):
    words = json.load(open(f'{ROOT}/voice/{n}.words.json'))['words']
    page = f'{ROOT}/chapters/{n}_{CH[n][0]}.html'
    wf = f'{ROOT}/chapters/{n}.warp.json'
    if os.path.exists(wf): os.remove(wf)
    os.system(f'python3 {ROOT}/tools/mkroom.py {n} > /dev/null')          # page on its own clock, to read the shot starts
    spans = kit.page_data(page)['SPANS']; page_dur = CH[n][2]
    cues = CUES[n]
    assert len(cues) == len(spans), f'{n}: {len(cues)} cues for {len(spans)} shots'
    anchors, after = [[0.0, 0.0]], 0.0
    for c, s in zip(cues[1:], spans[1:]):
        v = find(words, c, after); after = v
        anchors.append([round(v, 3), round(s['t0'], 3)])
    last = spans[-1]; keep = (last['t1'] - last['t0']) if last.get('rec') else MIN_LAST   # a recording slot keeps its full length
    end = max(words[-1]['end'] + TAIL, anchors[-1][0] + keep)
    anchors.append([round(end, 3), float(page_dur)])
    json.dump({'video_dur': round(end, 2), 'warp': anchors}, open(wf, 'w'))
    segs = [(round(b[1] - a[1], 1), round(b[0] - a[0], 1)) for a, b in zip(anchors, anchors[1:])]
    print(n, f'video {end:.1f} s (page {page_dur} s)', 'shots page→video s:', segs)
