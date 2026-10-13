#!/usr/bin/env bash
# usage: assemble.sh <chunks_dir> <audio.webm> <total_seconds> <out.mp4>
set -euo pipefail
CH="$1"; AUD="$2"; TOT="$3"; OUT="$4"
ls "$CH"/chunk_*.mp4 | sort | sed "s|^|file '$(pwd)/|; s|$|'|" > "$CH/list.txt"
ffmpeg -y -loglevel error -f concat -safe 0 -i "$CH/list.txt" -c copy "$CH/video_only.mp4"
FO=$(python3 -c "print(max(0,$TOT-4))")
ffmpeg -y -loglevel error -i "$CH/video_only.mp4" -i "$AUD" \
  -filter_complex "[1:a]afade=t=in:d=1.5,afade=t=out:st=$FO:d=4,aresample=48000[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t "$TOT" -movflags +faststart "$OUT"
echo "wrote $OUT"; ls -lh "$OUT"
