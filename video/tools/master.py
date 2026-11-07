#!/usr/bin/env python3
"""Master: results/final/<slug>_master.mp4 (slug from chapters/video.json) + voice_full.wav + chapters.txt + captions.srt + work/timeline.json.

Video: the finished chapter MP4s joined without re-encoding (all 1920x1080, 30 fps, same encoder settings).
Audio: the chapters' un-normalised mixes (work/audio/NN_mix.wav, each exactly DUR long) joined, then one two-pass
loudnorm over the whole master (-14 LUFS integrated, -1 dBTP). voice_full.wav: the voice tracks (mismatch lines muted)
on the master timeline, normalised the same way. Captions: the voiced sentences (muted ones left out), timed on the takes with timing.py.
"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit
ROOT = kit.ROOT; os.chdir(ROOT)
MASTER = f"results/final/{kit.video()['slug']}_master.mp4"
OUT = 'results/final'; W = 'work/master'; os.makedirs(W, exist_ok=True)
NN = sorted(kit.chapters())
pages = {n: next(f for f in os.listdir('chapters') if f.startswith(n + '_') and f.endswith('.html')) for n in NN}
metas = {n: json.load(open(f'work/audio/{n}_meta.json')) for n in NN}
chap_mp4 = {n: f'{OUT}/chapters/{pages[n][:-5]}.mp4' for n in NN}
for n in NN:
    if not os.path.exists(chap_mp4[n]): sys.exit(f'missing {chap_mp4[n]}')
run = lambda *a: subprocess.run(list(a), check=True)

def loudnorm(src, dst, extra=()):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', src, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    m = json.loads(re.search(r'\{[^{}]*"input_i"[^{}]*\}', r.stderr).group(0))
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000")
    run('ffmpeg', '-v', 'error', '-y', '-i', src, '-af', af, *extra, dst)

# timeline
t0, starts = 0.0, {}
for n in NN: starts[n] = t0; t0 += metas[n]['DUR']
total = t0
# video concat (stream copy)
open(f'{W}/v.txt', 'w').write(''.join(f"file '{os.path.abspath(chap_mp4[n])}'\n" for n in NN))
run('ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{W}/v.txt', '-an', '-c', 'copy', f'{W}/video.mp4')
# audio: joined mixes -> loudnorm
open(f'{W}/a.txt', 'w').write(''.join(f"file '{os.path.abspath(f'work/audio/{n}_mix.wav')}'\n" for n in NN))
run('ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{W}/a.txt', '-c:a', 'pcm_s24le', f'{W}/mix.wav')
loudnorm(f'{W}/mix.wav', f'{W}/mix_norm.wav', ('-c:a', 'pcm_s24le'))
run('ffmpeg', '-v', 'error', '-y', '-i', f'{W}/video.mp4', '-i', f'{W}/mix_norm.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '320k',
    '-ar', '48000', '-t', f'{total:.3f}', '-movflags', '+faststart', MASTER)
# voice only, on the master timeline
for n in NN:
    run('ffmpeg', '-v', 'error', '-y', '-i', f'voice/{n}.wav', '-af', f"apad=whole_dur={metas[n]['DUR']:.3f}", '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s24le', f'{W}/vo_{n}.wav')
open(f'{W}/vo.txt', 'w').write(''.join(f"file '{os.path.abspath(f'{W}/vo_{n}.wav')}'\n" for n in NN))
run('ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{W}/vo.txt', '-c:a', 'pcm_s24le', f'{W}/vo.wav')
loudnorm(f'{W}/vo.wav', f'{OUT}/voice_full.wav', ('-c:a', 'pcm_s24le'))

tc = lambda s: f'{int(s // 60)}:{int(s % 60):02d}'
TITLES = {k: v[1] for k, v in kit.chapters().items()}
open(f'{OUT}/chapters.txt', 'w').write(''.join(f'{tc(starts[n])} {TITLES[n]}\n' for n in NN))
# captions: voiced sentences only (from the page CAPS = timing.py output)
mutes = json.load(open('voice/mutes.json')) if os.path.exists('voice/mutes.json') else []; srt, caps = [], []
def stc(s): ms = int(round(s * 1000)); return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'
sys.path.insert(0, kit.SHORTS_TOOLS); import timing   # chunk timing on the take that plays
for n in NN:
    for txt, a, b in timing.chunk_times(timing.load_words(f'voice/{n}.words.json'), timing.load_chunks(f'chapters/{n}.chunks.txt')):
        if any(m['chapter'] == n and m['start'] - .1 <= a <= m['end'] for m in mutes): continue
        caps.append([starts[n] + a, starts[n] + b + .15, txt])
caps.sort()
for i, c in enumerate(caps):   # never two captions on screen at once: end each one before the next starts
    if i + 1 < len(caps): c[1] = min(c[1], caps[i + 1][0] - .02)
    srt.append(f"{i + 1}\n{stc(c[0])} --> {stc(c[1])}\n{c[2]}\n")
open(f'{OUT}/captions.srt', 'w').write('\n'.join(srt))
# timeline: chapter starts, recording slots, real clips, mutes, long shots (shorts.py reads it)
tl = {'total': total, 'chapters': {n: {'start': starts[n], 'dur': metas[n]['DUR'], 'file': chap_mp4[n]} for n in NN},
      'recs': [{**s['rec'], 'chapter': n, 'start': starts[n] + s['t0'], 'chapter_t0': s['t0'], 'len': s['t1'] - s['t0']} for n in NN for s in metas[n]['SPANS'] if s.get('rec')],
      'clips': [{'chapter': n, 'src': c['src'], 'start': starts[n] + c['t0'], 'len': c['t1'] - c['t0']} for n in NN for c in metas[n]['CLIPS']],
      'mutes': [{**m, 'master_start': starts[m['chapter']] + m['start']} for m in mutes],
      'long_shots': [{'chapter': n, 'name': s['name'], 'look': s['look'], 'len': round(s['t1'] - s['t0'], 2)} for n in NN for s in metas[n]['SPANS'] if s['t1'] - s['t0'] > 10]}
json.dump(tl, open('work/timeline.json', 'w'), indent=1)
print(f'master {total:.2f} s ({tc(total)}), {len(srt)} captions, recs {len(tl["recs"])}, clips {len(tl["clips"])}, shots > 10 s: {len(tl["long_shots"])}')
