"""Shared paths and config for the chapter kit tools (see ../README.md).

ROOT is the project's video/ folder (the parent of tools/). The sibling skills tacdel-shorts (render.cjs, timing.py)
and tacdel-motion (voice.py, sound.py) are found under TACDEL_SKILLS (default ~/ai-dev-skills/skills), and Playwright
under NODE_PATH (default: node_modules next to that skills folder).
"""
import json, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.expanduser(os.environ.get('TACDEL_SKILLS', '~/ai-dev-skills/skills'))
SHORTS_TOOLS = os.path.join(SKILLS, 'tacdel-shorts', 'tools')
MOTION_TOOLS = os.path.join(SKILLS, 'tacdel-motion', 'tools')
NODE_PATH = os.environ.get('NODE_PATH') or os.path.join(os.path.dirname(SKILLS), 'node_modules')


def load(rel, default=None):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p) and default is not None: return default
    return json.load(open(p, encoding='utf-8'))


def chapters():
    """chapters/chapters.json: {"NN": ["file_name", "Title"], ...}; keys starting with _ are comments."""
    return {k: v for k, v in load('chapters/chapters.json').items() if not k.startswith('_')}


def video():
    """chapters/video.json: {"title": "...", "slug": "my_video", "script": "SCRIPT.md"}."""
    return load('chapters/video.json')


def edits():
    """voice/edits.json: {"mutes": [[NN, line]], "pauses": [[NN, phrase, s]], "leads": {NN: s}} (all optional)."""
    return load('voice/edits.json', {})


def page_data(page):
    """window.pageData() of a chapter page, read in headless Chromium: DUR, ERRS, SFX, CLIPS, WINS, SPANS."""
    js = ("const { chromium } = require('playwright'); (async () => { const b = await chromium.launch(); const p = await b.newPage();"
          f"await p.goto('file://{os.path.abspath(page)}?clean'); await p.waitForFunction(() => window.READY, null, {{ timeout: 15000 }});"
          "console.log(await p.evaluate(() => pageData())); await b.close(); })();")
    env = dict(os.environ, NODE_PATH=NODE_PATH)
    return json.loads(subprocess.run(['node', '-e', js], capture_output=True, text=True, check=True, env=env).stdout.strip().splitlines()[-1])
