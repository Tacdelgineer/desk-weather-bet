#!/usr/bin/env python3
"""Word timings for a take that didn't come from the API (a web-app take, a self-recorded one): no credits.

  python3 tools/align.py <audio> <text.txt> <out.words.json>

faster-whisper (small.en, CPU) hears the words with timestamps; each script word is then matched to the recognised
words in order. Script words it didn't match (e.g. "seventy-two" heard as "72") share the gap between their matched
neighbours. Output has the same shape as voice_ch.py's: {"words": [{"text", "start", "end"}, ...]}.
Also the way to check any take: a low "matched" count means a swallowed or wrong word.
"""
import difflib, json, os, re, subprocess, sys, tempfile

norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower().replace('’', "'"))
# audio decoded by ffmpeg (faster-whisper's own decoder breaks on some PyAV releases)
CODE = ("import json,sys,subprocess,numpy as np; from faster_whisper import WhisperModel; m=WhisperModel('small.en',device='cpu',compute_type='int8');"
        "a=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',sys.argv[1],'-f','f32le','-ac','1','-ar','16000','-'],capture_output=True,check=True).stdout,np.float32);"
        "segs,_=m.transcribe(a,word_timestamps=True,language='en');"
        "json.dump([{'text':w.word.strip(),'start':w.start,'end':w.end} for s in segs for w in s.words],open(sys.argv[2],'w'))")


def align(audio, text, out):
    js = tempfile.mktemp(suffix='.json')
    subprocess.run(['env', '-u', 'VIRTUAL_ENV', 'uv', 'run', '-q', '--no-project', '--with', 'faster-whisper', 'python', '-c', CODE, audio, js], check=True)
    rec = json.load(open(js)); os.remove(js)
    script = re.sub(r'<[^>]+>', ' ', open(text, encoding='utf-8').read()).split()
    a, b = [norm(x['text']) for x in rec], [norm(x) for x in script]
    m = {}
    for ai, bj, n in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        m.update({bj + k: ai + k for k in range(n)})
    out_w = []
    for i, wd in enumerate(script):
        if i in m:
            r = rec[m[i]]; out_w.append({'text': wd, 'start': round(r['start'], 3), 'end': round(r['end'], 3)}); continue
        j0 = max([k for k in m if k < i], default=None); j1 = min([k for k in m if k > i], default=None)
        a0 = rec[m[j0]]['end'] if j0 is not None else 0.0
        a1 = rec[m[j1]]['start'] if j1 is not None else a0 + .4 * (i - (j0 or 0))
        lo, hi = (j0 if j0 is not None else -1), (j1 if j1 is not None else len(script)); k, nk = i - lo, hi - lo
        st = a0 + (a1 - a0) * (k - 1) / (nk - 1); en = a0 + (a1 - a0) * k / (nk - 1)
        out_w.append({'text': wd, 'start': round(st, 3), 'end': round(max(en, st + .05), 3)})
    json.dump({'words': out_w, 'aligned': 'faster-whisper small.en', 'matched': len(m), 'of': len(script)}, open(out, 'w'))
    print(f'aligned {os.path.basename(audio)}: {len(m)}/{len(script)} words matched')


if __name__ == '__main__':
    align(*sys.argv[1:4])
