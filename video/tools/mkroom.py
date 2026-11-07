#!/usr/bin/env python3
"""Build chapters/NN_name.html for a footage page (manual-mode rooms: no voice yet, fixed length), or a voiced page.

  python3 tools/mkroom.py NN [NN ...]      (no args: every entry in chapters/chapters.json)

chapters.json entry: "NN": ["file_name", "Title", seconds, ["tx file", ...]]. Only the listed chapters/tx/*.js files are
loaded (the satellite frame files are large). If voice/NN.words.json exists its words are loaded for cue(); otherwise
WORDS is empty and shots use plain seconds. Project tool (the kit's mkpage.py needs a voice take for every page).
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit
ROOT = kit.ROOT
CH = kit.chapters(); TITLE = kit.video()['title']
for n in sys.argv[1:] or sorted(CH):
    name, title, dur, tx = CH[n]
    wf = f'{ROOT}/voice/{n}.words.json'
    words = json.load(open(wf))['words'] if os.path.exists(wf) else []
    open(f'{ROOT}/chapters/{n}.words.js', 'w').write('window.WORDS = ' + json.dumps(words, separators=(',', ':')) + ';\n')
    # the voice clock (tools/warp.py): DUR becomes the video length, WARP maps video time -> footage time
    W = json.load(open(f'{ROOT}/chapters/{n}.warp.json')) if os.path.exists(f'{ROOT}/chapters/{n}.warp.json') else None
    warp = W['warp'] if W else []
    if W: dur = W['video_dur']
    # sentences of the take, for captions (master.py)
    tf = f'{ROOT}/voice/text/{n}.txt'
    sents = [s.strip() for s in re.split(r'(?<=[.?!])\s+', ' '.join(open(tf).read().split())) if s.strip()] if os.path.exists(tf) else []
    open(f'{ROOT}/chapters/{n}.chunks.txt', 'w').write('\n'.join(sents) + ('\n' if sents else ''))
    for t in tx: assert os.path.exists(f'{ROOT}/chapters/tx/{t}'), f'missing chapters/tx/{t} (run prep_goes.py?)'
    TXS = '\n'.join(f'<script src="tx/{t}"></script>' for t in tx)
    page = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{n} {title}</title>
<!--
  {TITLE} · {n} · {title} · 1920x1080 · 30 fps · built by tools/mkroom.py (shots in {n}_scenes.js; looks in ../styles/)
  KEYS  Space play/pause · R restart · Left/Right shot · H hide controls   URL  ?clean · ?t=12
-->
<link rel="stylesheet" href="../styles/fonts.css">
</head>
<body>
<canvas id="c" width="1920" height="1080"></canvas>
<div id="hud"><div id="bar"><div id="fill"></div></div><div id="row"><span id="info"></span><span>Space · R · ← → · H</span></div></div>
<script>
const TITLE = {json.dumps(n + ' · ' + title, ensure_ascii=False)}, VOICE = {json.dumps(f'../voice/{n}.wav' if words else '')};
const DUR = {dur};
const WARP = {json.dumps(warp)};
</script>
<script src="{n}.words.js"></script>
<script src="data.js"></script>
<script src="../styles/core.js"></script>
<script src="../styles/riso.js"></script>
<script src="../styles/papercut.js"></script>
<script src="../styles/crt.js"></script>
{TXS}
<script src="common.js"></script>
<script src="{n}_scenes.js"></script>
<script>start();</script>
</body>
</html>
'''
    out = f'{ROOT}/chapters/{n}_{name}.html'; open(out, 'w').write(page); print(out, 'DUR', dur, 'words', len(words))
