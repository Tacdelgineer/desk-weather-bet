#!/usr/bin/env python3
"""voice/raw/NN.mp3 + voice/raw/NN.words.json -> voice/NN.wav + voice/NN.words.json (what the pages and the mix use).

All edits come from voice/edits.json (every key optional), so the same take can be re-cut without new credits:
  "mutes":  [[NN, exact spoken line], ...]  lines that fail the fact check, replaced by silence of the same length
            (first word start -30 ms to last word end +40 ms) until re-voiced. Written to voice/mutes.json.
  "pauses": [[NN, phrase, seconds], ...]    a silent beat inserted just before the phrase (a title card, a visual
            pause, a payoff landing); every later word time shifts by that much.
  "leads":  {NN: seconds}                   silence before the first word: the payoff shot plays before the hook line.

  python3 tools/mute.py [NN ...]     (no args: every chapter)
"""
import json, re, subprocess, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit
ROOT = kit.ROOT; E = kit.edits()
MUTES = [tuple(m) for m in E.get('mutes', [])]
PAUSES = [tuple(p) for p in E.get('pauses', [])]
LEADS = E.get('leads', {})
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())


def find(w, line):
    toks = [norm(x) for x in line.split() if norm(x)]
    for i in range(len(w) - len(toks) + 1):
        if [norm(x['text']) for x in w[i:i + len(toks)]] == toks: return i, i + len(toks) - 1
    raise SystemExit(f'not found: {line}')


def build(n, w, spans, pauses, lead=0):
    src, dst = f'{ROOT}/voice/raw/{n}.mp3', f'{ROOT}/voice/{n}.wav'
    chain = ','.join([f"volume=enable='between(t,{a:.3f},{b:.3f})':volume=0" for a, b in spans] or ['anull']) + ',aresample=48000'
    pad = f',adelay={round(lead * 1000)}:all=1' if lead else ''
    if not pauses:
        return ['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', chain + pad, '-ac', '1', '-ar', '48000', dst]
    cuts = [0] + [p for p, _ in pauses]; k = len(cuts)
    fc = f'[0:a]{chain},aformat=channel_layouts=mono,asplit={k}' + ''.join(f'[s{i}]' for i in range(k)) + ';'
    for i, c0 in enumerate(cuts):
        c1 = cuts[i + 1] if i + 1 < k else None
        fc += f'[s{i}]atrim=start={c0:.3f}' + (f':end={c1:.3f}' if c1 else '') + f',asetpts=PTS-STARTPTS[a{i}];'
        if c1 is not None: fc += f'aevalsrc=0:d={pauses[i][1]}:s=48000[z{i}];'
    fc += ''.join(f'[a{i}]' + (f'[z{i}]' if i + 1 < k else '') for i in range(k)) + f'concat=n={2 * k - 1}:v=0:a=1{pad}[o]'
    return ['ffmpeg', '-v', 'error', '-y', '-i', src, '-filter_complex', fc, '-map', '[o]', '-ac', '1', '-ar', '48000', dst]


ALL = sorted(kit.chapters()); todo = sys.argv[1:] or ALL
mj = f'{ROOT}/voice/mutes.json'
out = [m for m in json.load(open(mj)) if m['chapter'] not in todo] if todo != ALL and os.path.exists(mj) else []
for n in todo:
    w = json.load(open(f'{ROOT}/voice/raw/{n}.words.json'))['words']
    mutes = [m for m in MUTES if m[0] == n]
    spans = [(w[a]['start'] - .03, w[b]['end'] + .04) for _, line in mutes for a, b in [find(w, line)]]
    pauses = []
    for ch, ph, s in PAUSES:
        if ch != n: continue
        i = find(w, ph)[0]; pauses.append((max(w[i]['start'] - .05, w[i - 1]['end'] + .02), s))
    pauses.sort()
    lead = LEADS.get(n, 0); shift = lambda t: lead + t + sum(s for at, s in pauses if t >= at)
    subprocess.run(build(n, w, spans, pauses, lead), check=True)
    w2 = [{**x, 'start': round(shift(x['start']), 3), 'end': round(shift(x['end']), 3)} for x in w]
    json.dump({'words': w2}, open(f'{ROOT}/voice/{n}.words.json', 'w'))
    for (a, b), (_, line) in zip(spans, mutes): out.append({'chapter': n, 'line': line, 'start': round(shift(a), 2), 'end': round(shift(b), 2)})
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'{ROOT}/voice/{n}.wav'], capture_output=True, text=True).stdout)
    print(n, f'{d:.2f}s', 'lead', lead, 'pauses', len(pauses), 'mutes', len(spans))
json.dump(sorted(out, key=lambda m: (m['chapter'], m['start'])), open(mj, 'w'), indent=1)
