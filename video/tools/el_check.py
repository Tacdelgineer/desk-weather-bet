#!/usr/bin/env python3
"""Print only the voice name, model support and remaining credits. Never prints keys or ids."""
import json, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit
sys.path.insert(0, kit.MOTION_TOOLS)
import voice
key, vid = voice.creds()
def get(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'xi-api-key': key}), timeout=30))
v = get(f'https://api.elevenlabs.io/v1/voices/{vid}')
print('voice name:', v.get('name'), '| category:', v.get('category'))
s = get('https://api.elevenlabs.io/v1/user/subscription')
print('credits used/limit:', s.get('character_count'), '/', s.get('character_limit'), '| tier:', s.get('tier'))
