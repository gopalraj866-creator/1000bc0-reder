#!/usr/bin/env python3
"""Render one contiguous slice of frames with headless Chromium (software WebGL) and encode it to an mp4 chunk."""
import argparse, base64, subprocess, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).parent))
from common import ARGS, route, page_url

ap = argparse.ArgumentParser()
ap.add_argument('--html', default='earth-10000bc.html')
ap.add_argument('--shard', type=int, default=0)
ap.add_argument('--shards', type=int, default=1)
ap.add_argument('--fps', type=int, default=30)
ap.add_argument('--height', type=int, default=1080)
ap.add_argument('--total', type=float, default=480.0, help='video length in seconds (480 = full, 52 = shorts)')
ap.add_argument('--vertical', action='store_true')
ap.add_argument('--start', type=int, default=None, help='override first frame (testing)')
ap.add_argument('--end', type=int, default=None, help='override end frame, exclusive (testing)')
ap.add_argument('--out', default='chunks')
a = ap.parse_args()

total_frames = int(round(a.total * a.fps))
s = a.start if a.start is not None else a.shard * total_frames // a.shards
e = a.end if a.end is not None else (a.shard + 1) * total_frames // a.shards
Path(a.out).mkdir(parents=True, exist_ok=True)
out = Path(a.out) / f'chunk_{a.shard:03d}.mp4'
print(f'shard {a.shard}/{a.shards}: frames {s}..{e-1} of {total_frames} -> {out}', flush=True)

ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(a.fps), '-i', '-',
                       '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', '-r', str(a.fps),
                       '-g', str(a.fps * 2), '-movflags', '+faststart', str(out)], stdin=subprocess.PIPE)

def open_page(p):
    b = p.chromium.launch(args=ARGS)
    pg = b.new_page(viewport={'width': 960, 'height': 540})
    pg.on('pageerror', lambda x: print('PAGEERR', str(x)[:300], flush=True))
    pg.route('**/*', route)
    pg.goto(page_url(a.html, render=True, h=a.height, fps=a.fps, vertical=a.vertical))
    pg.wait_for_function('window.__ready===true || window.__fail', timeout=600000)
    fail = pg.evaluate('window.__fail||null')
    if fail: print('WARNING:', fail, flush=True)
    return b, pg

t0 = time.time(); n = s
with sync_playwright() as p:
    b, pg = open_page(p)
    retries = 0
    while n < e:
        try:
            d = pg.evaluate("t=>{window.__renderFrame(t);return document.getElementById('comp').toDataURL('image/png')}", n / a.fps)
            ff.stdin.write(base64.b64decode(d.split(',', 1)[1]))
            n += 1; retries = 0
            if (n - s) % 20 == 0:
                el = time.time() - t0; per = el / (n - s)
                print(f'  frame {n-1} ({n-s}/{e-s})  {per:.1f}s/frame  ETA {per*(e-n)/60:.0f} min', flush=True)
        except Exception as ex:
            retries += 1
            print('frame', n, 'failed:', str(ex)[:200], '- restarting browser', flush=True)
            if retries > 4: raise
            try: b.close()
            except Exception: pass
            b, pg = open_page(p)
    b.close()
ff.stdin.close(); ff.wait()
print('done', out, f'{(time.time()-t0)/60:.1f} min', flush=True)
