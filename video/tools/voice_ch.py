#!/usr/bin/env python3
"""One ElevenLabs generation per chapter, with the channel's final voice settings, plus word timings.

  python3 tools/voice_ch.py [NN ...]              (default: every chapter in the script)
  python3 tools/voice_ch.py --text-only [NN ...]  (only voice/text/NN.txt, no API call, no credits)

Text = the chapter's Voice block in the script (SCRIPT env var, default video.json "script"), ⟦…⟧ markers removed.
Both script layouts work: "## NN. Title / **Voice** / … / **Shots**" and "NN · Title / Voice / … / Shots".
Settings: FINAL_VOICE.md at the repo root (MODEL and SETTINGS below must match; eleven_v4 takes no style or speaker boost). Writes voice/raw/NN.mp3,
voice/raw/NN.words.json, voice/text/NN.txt. Creds via tacdel-motion voice.py (env or ~/.tacdel.env).
Prints a short summary only: no keys, ids or audio. Every call spends credits: voice a chapter again only when its
take fails the check (wrong word, swallowed word, a line changed by the fact check).
"""
import base64, json, os, re, sys, urllib.error, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit
sys.path.insert(0, kit.MOTION_TOOLS)
import voice  # creds() and words_from_alignment()

ROOT = kit.ROOT
MODEL = 'eleven_v4'
SETTINGS = {'stability': 0.69, 'similarity_boost': 0.78, 'speed': 0.93}
LAYOUTS = [r'^## (\d+)\. .*?\n\*\*Voice\*\*\n(.*?)\n\*\*Shots\*\*', r'^(\d{2}) · .*?\nVoice\n(.*?)\nShots\n']


def blocks():
    name = os.environ.get('SCRIPT') or kit.video().get('script', 'SCRIPT.md')
    txt = open(os.path.join(ROOT, name), encoding='utf-8').read()
    out = {}
    for pat in LAYOUTS:
        for m in re.finditer(pat, txt, re.S | re.M):
            body = re.sub(r'\s*⟦[^⟧]*⟧', '', m.group(2))
            paras = [' '.join(p.split()) for p in body.split('\n\n') if p.strip()]
            out[f'{int(m.group(1)):02d}'] = '\n\n'.join(paras)
    if not out: sys.exit(f'no Voice blocks found in {name}')
    return out


def speak(text, key, vid):
    body = {'text': text, 'model_id': MODEL, 'voice_settings': SETTINGS}
    req = urllib.request.Request(f'https://api.elevenlabs.io/v1/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_192',
                                 data=json.dumps(body).encode(), headers={'xi-api-key': key, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=600) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f'ElevenLabs HTTP {e.code}: {e.read().decode("utf-8", "replace")[:200]}')


def main():
    args = sys.argv[1:]; text_only = '--text-only' in args; args = [a for a in args if a != '--text-only']
    B = blocks(); want = args or sorted(B)
    if not text_only: key, vid = voice.creds()
    os.makedirs(os.path.join(ROOT, 'voice/raw'), exist_ok=True); os.makedirs(os.path.join(ROOT, 'voice/text'), exist_ok=True)
    for n in want:
        text = B[n]; open(os.path.join(ROOT, f'voice/text/{n}.txt'), 'w').write(text + '\n')
        if text_only: print(f'{n}: {len(text.split())} words -> voice/text/{n}.txt'); continue
        d = speak(text, key, vid)
        open(os.path.join(ROOT, f'voice/raw/{n}.mp3'), 'wb').write(base64.b64decode(d['audio_base64']))
        w = voice.words_from_alignment(d.get('alignment') or d['normalized_alignment'])
        json.dump({'words': w}, open(os.path.join(ROOT, f'voice/raw/{n}.words.json'), 'w'))
        nw = len(re.sub(r'<[^>]+>', ' ', text).split()); secs = w[-1]['end'] if w else 0
        print(f'{n}: {nw} words, {len(text)} chars, {secs:.1f} s, {nw / secs * 60:.0f} wpm', flush=True)


if __name__ == '__main__':
    main()
