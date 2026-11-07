#!/usr/bin/env python3
"""Chapter audio: voice + light sound effects, all made in code (no samples, no music).

  python3 tools/sfx.py <page.html> <voice.wav> <out_mix.wav> <out_meta.json>

Reads SFX cues, shot spans and CLIPS from the page (window.pageData()). Synths come from the tacdel-motion sound.py
(imported, read only) plus paper rustle, paper tear and a low CRT hum written here. A quiet hum runs under every CRT
shot. Writes a 48 kHz stereo mix (not loudness-normalised; build.sh does that) and the page meta for the compositor.
"""
import json, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit
from kit import page_data
sys.path.insert(0, kit.MOTION_TOOLS)
import sound as S   # synth helpers only (SR, tt, bp, hp, lp, att, SYN)
SR = S.SR; rng = np.random.default_rng(11)

def s_paper(r=1):   # cut paper landing: a soft filtered-noise rustle with two flutters
    t = S.tt(.32); n = rng.standard_normal(len(t)); env = np.exp(-t * 12) * (1 + .6 * np.sin(2 * np.pi * 26 * t))
    return S.att(S.bp(n, 900 * r, 5200) * env * 1.1, .004)
def s_tear(r=1):    # paper tearing: crackly band noise with random grain
    t = S.tt(.55); n = rng.standard_normal(len(t)) * (rng.random(len(t)) < .35); env = np.sin(np.pi * t / t[-1]) ** .7
    return S.bp(n, 1200 * r, 7000) * env * 2.2
def hum(d):         # CRT: 60 Hz mains hum + harmonics, very low
    t = S.tt(d); x = sum(np.sin(2 * np.pi * 60 * k * t) / k ** 1.4 for k in (1, 2, 3, 5)) * .25
    f = np.minimum(1, np.minimum(t / .15, (t[-1] - t) / .15 + 1e-9)); return x * np.clip(f, 0, 1)
SYN = dict(S.SYN, paper=s_paper, tear=s_tear)
FX = .22            # effects bus: light, well under the voice (voice peaks at 0.9)

def main():
    page, voice, out, meta = sys.argv[1:5]
    d = page_data(page)
    if d['ERRS']: sys.exit('page errors: ' + '; '.join(d['ERRS']))
    N = int(round(d['DUR'] * SR)); fx = np.zeros(N)
    def add(x, t, g):
        i = int(t * SR); x = x[:max(0, N - i)] * g
        if i < N and len(x): fx[i:i + len(x)] += x
    for t, name, g in d['SFX']:
        if name not in SYN: sys.exit(f'unknown sfx {name}')
        add(np.asarray(SYN[name](), float), t, g * FX)
    for s in d['SPANS']:
        if s['look'] == 'crt' and s['t1'] - s['t0'] > .2: add(hum(s['t1'] - s['t0']), s['t0'], .03)
    fx = S.lp(fx, 9000)
    v = subprocess.run(['ffmpeg', '-v', 'error', '-i', voice, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    v = np.frombuffer(v, np.float32).astype(float)[:N]; vv = np.zeros(N); vv[:len(v)] = v
    vv *= .9 / (np.abs(vv).max() or 1)   # the takes come in quiet (about -35 LUFS); bring the voice to a 0.9 peak first
    # effects sit well under the voice: duck them a little while the voice is loud
    env = np.convolve(np.abs(vv), np.ones(int(.05 * SR)) / int(.05 * SR), 'same'); duck = 1 - .45 * np.clip(env / (env.max() or 1) * 4, 0, 1)
    mix = vv + fx * duck
    st = np.stack([mix, mix], 1); peak = np.abs(st).max() or 1
    if peak > .98: st *= .98 / peak
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-i', '-', '-c:a', 'pcm_s24le', out], input=st.astype(np.float32).tobytes(), check=True)
    json.dump(d, open(meta, 'w'))
    print(f'{os.path.basename(page)}: {d["DUR"]} s, {len(d["SFX"])} sfx, {sum(s["look"] == "crt" for s in d["SPANS"])} crt shots, {len(d["CLIPS"])} clips')

if __name__ == '__main__':
    main()
