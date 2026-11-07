#!/usr/bin/env python3
"""Lay the real clips into their holes, add the chapter mix, loudness-normalise (two-pass loudnorm, -14 LUFS, -1 dBTP).

  python3 tools/compose.py <raw.mp4> <mix.wav> <meta.json> <page_dir> <out.mp4>
"""
import json, os, re, subprocess, sys
raw, mix, meta, pdir, out = sys.argv[1:6]
d = json.load(open(meta)); clips = d['CLIPS']
def loudnorm_args(src):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', src, '-vn', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True)
    m = json.loads(re.search(r'\{[^{}]*"input_i"[^{}]*\}', r.stderr).group(0))
    return (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
            f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
inputs = ['-i', raw, '-i', mix]; fc = []; last = '0:v'
for k, c in enumerate(clips):
    src = os.path.normpath(os.path.join(pdir, c['src'])); inputs += ['-i', src]; j = k + 2; dur = c['t1'] - c['t0']
    lab = ''
    if c.get('label'):   # small caption burned onto the clip, bottom right inside the 5% margin (style from core.js OV.label)
        L = c['labelStyle']; tf = os.path.abspath(f'work/labels/{os.path.basename(out)}.{k}.txt'); os.makedirs(os.path.dirname(tf), exist_ok=True); open(tf, 'w').write(c['label'] + ' ' * (len(c['label'].encode()) - len(c['label'])))   # drawtext drops one trailing char per multi-byte char (·); pad it
        fs = min(L['size'], max(14, c['w'] // 26)); m = 24 if fs == L['size'] else 10   # small tiles get a smaller label, always inside the clip
        lab = (f",drawtext=fontfile={L['font']}:textfile={tf}:fontsize={fs}:fontcolor={L['ink']}:box=1:boxcolor={L['bg']}@{L['bgAlpha']}:boxborderw={fs // 2}"
               f":x=min({1824 - c['x']}\\,w)-tw-{m}:y=min({1026 - c['y']}\\,h)-th-{m}")
    # a shot can outlast its clip: hold the last frame (tpad) rather than show the empty hole
    crop = f"crop={c['crop'][2]}:{c['crop'][3]}:{c['crop'][0]}:{c['crop'][1]}," if c.get('crop') else ''   # [x, y, w, h] in source pixels
    fc.append(f"[{j}:v]trim=start={c['from']:.3f},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={dur + 1:.3f},trim=duration={dur:.3f},setpts=PTS-STARTPTS,fps=30,{crop}scale={c['w']}:{c['h']}{lab},setpts=PTS+{c['t0']:.3f}/TB[c{k}]")
    fc.append(f"[{last}][c{k}]overlay={c['x']}:{c['y']}:enable='between(t,{c['t0']:.3f},{c['t1'] - .001:.3f})':eof_action=pass[o{k}]"); last = f'o{k}'
vmap = f'[{last}]' if clips else '0:v'
fc.append(f"[1:a]{loudnorm_args(mix)},aresample=48000[a]")
cmd = ['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex', ';'.join(fc), '-map', vmap, '-map', '[a]',
       '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '320k', '-ar', '48000',
       '-t', f"{d['DUR']:.3f}", '-movflags', '+faststart', out]
subprocess.run(cmd, check=True); print('composed', out, f'{len(clips)} clips')
