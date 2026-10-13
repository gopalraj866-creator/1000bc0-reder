import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NM = ROOT / "node_modules" / "three"
ARGS = ['--use-angle=swiftshader', '--use-gl=angle', '--enable-unsafe-swiftshader',
        '--ignore-gpu-blocklist', '--enable-webgl', '--allow-file-access-from-files',
        '--autoplay-policy=no-user-gesture-required', '--disable-dev-shm-usage']

def route(r):
    """Serve three.js from node_modules (deterministic, no CDN dependency); everything else goes to the network."""
    u = r.request.url
    p = None
    if 'three@0.160.0/build/' in u:
        p = NM / 'build' / u.split('/build/')[1]
    elif 'three@0.160.0/examples/jsm/' in u:
        p = NM / 'examples' / 'jsm' / u.split('/jsm/')[1]
    if p is not None and p.exists():
        return r.fulfill(path=str(p), headers={'access-control-allow-origin': '*'})
    return r.continue_()

def page_url(html, **q):
    from urllib.parse import urlencode
    qs = {k: v for k, v in q.items() if v not in (None, False)}
    qs = {k: ('1' if v is True else v) for k, v in qs.items()}
    return Path(html).resolve().as_uri() + '?' + urlencode(qs)
