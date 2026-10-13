# Earth 10,000 BC — GitHub Actions renderer

Renders `earth-10000bc.html` to an MP4 (with soundtrack) on GitHub's runners — no GPU, no keeping a browser tab open.

## Use
1. Create a new GitHub repo and push everything in this folder (`earth-10000bc.html`, `tools/`, `package.json`, `.github/`).
2. **Actions → Render Earth 10,000 BC → Run workflow.**
   - `vertical` off = 8:00 video, on = 52 s Shorts cut (9:16).
   - Defaults: 1080p, 30 fps, 20 parallel shards.
3. When it finishes, download the `Earth_10000BC_8min` artifact (kept 14 days).

## How it works
- **render**: each shard loads the page in headless Chromium (software WebGL), renders its slice of frames deterministically via `window.__renderFrame(t)`, and encodes it to an mp4 chunk (x264 CRF 14).
- **audio**: records the generated ambient soundtrack in real time (8 min) with WebAudio.
- **assemble**: concatenates the chunks, adds the soundtrack with a 1.5 s fade-in and 4 s fade-out.

## Time / cost
No GPU on runners, so frames render slowly: roughly 10 s per 1080p frame per runner (measured ~2.5 s at 540p on 2 cores).
8 min × 30 fps = 14,400 frames ≈ 40 runner-hours → with 20 shards ≈ 2 h wall-clock.
- **Public repo:** free and unlimited minutes.
- **Private repo:** the free plan has only 2,000 min/month, so the full video won't fit. Use a public repo, a paid plan, or lower settings (`height` 720, `fps` 24 → about 2.2× fewer minutes).
- Each job has a 6 h limit; if a shard times out, raise `shards` (max 20 parallel; extra shards queue).

## Notes
- Three.js is installed from npm and the Earth/grass textures are downloaded from GitHub at run time.
- Frames are deterministic, so shard boundaries are seamless.
- Test locally: `npm install && pip install playwright && playwright install chromium`, then
  `python3 tools/render_shard.py --start 0 --end 30 --height 540 --out chunks`
