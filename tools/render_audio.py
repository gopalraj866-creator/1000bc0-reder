#!/usr/bin/env python3
"""Records the video's ambient soundtrack (real time, ~= video length) with headless Chromium's WebAudio."""
import argparse, base64, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).parent))
from common import ARGS, route, page_url

ap = argparse.ArgumentParser()
ap.add_argument('--html', default='earth-10000bc.html')
ap.add_argument('--total', type=float, default=480.0)
ap.add_argument('--vertical', action='store_true')
ap.add_argument('--out', default='audio.webm')
a = ap.parse_args()
with sync_playwright() as p:
    b = p.chromium.launch(args=ARGS)
    pg = b.new_page(viewport={'width': 640, 'height': 360})
    pg.on('pageerror', lambda x: print('PAGEERR', str(x)[:300], flush=True))
    pg.route('**/*', route)
    pg.goto(page_url(a.html, audio=True, vertical=a.vertical, len=int(a.total)))
    pg.wait_for_function('window.__audioReady===true', timeout=300000)
    print('recording audio in real time for', a.total, 's ...', flush=True)
    pg.set_default_timeout((int(a.total) + 120) * 1000)
    pg.evaluate('window.__audioStart()')
    b64 = pg.evaluate('window.__audioB64')
    Path(a.out).write_bytes(base64.b64decode(b64))
    print('saved', a.out, len(b64) * 3 // 4 // 1024, 'KB')
    b.close()
