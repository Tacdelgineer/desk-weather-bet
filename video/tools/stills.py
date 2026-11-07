#!/usr/bin/env python3
"""Longest stretches with no cut: shot changes, window changes and clip starts/ends all count as cuts.
A stretch is fine when moving real footage fills it (listed as "clip: ..."); "NO CLIP" over the limit needs a cut.

  python3 tools/stills.py [max_seconds=6.2]     (reads every chapter page; lists the stretches over the limit)
"""
import glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from kit import page_data
lim = float(sys.argv[1]) if len(sys.argv) > 1 else 6.2; bad = 0
for page in sorted(glob.glob('chapters/[0-9][0-9]_*.html')):
    d = page_data(page); cuts = {0.0, d['DUR']}
    for x in d['SPANS'] + d['WINS'] + d['CLIPS']: cuts |= {round(x['t0'], 2), round(x['t1'], 2)}
    cuts = sorted(c for c in cuts if 0 <= c <= d['DUR'])
    for a, b in zip(cuts, cuts[1:]):
        if b - a > lim:
            moving = [os.path.basename(c['src']) for c in d['CLIPS'] if c['t0'] <= a + .05 and c['t1'] >= b - .05]
            print(f"{os.path.basename(page)[:2]} {a:6.2f}-{b:6.2f} ({b - a:4.1f} s) {'clip: ' + ', '.join(moving) if moving else 'NO CLIP'}"); bad += 1
print(f'{bad} stretches over {lim} s')
