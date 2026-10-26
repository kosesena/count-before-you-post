#!/bin/sh
# Fetch the stock clips listed in experiments/videos/SOURCES.md (960x540, faststart).
set -e
cd "$(dirname "$0")/videos"
fetch() {
  curl -sL -A "Mozilla/5.0" -o "raw-$1" "$2"
  ffmpeg -loglevel error -y -i "raw-$1" -c copy -movflags +faststart "$1"
  rm "raw-$1"
}
fetch conveyor-5903898.mp4 https://videos.pexels.com/video-files/5903898/5903898-sd_960_540_30fps.mp4
fetch sorting-10472351.mp4 https://videos.pexels.com/video-files/10472351/10472351-sd_960_540_25fps.mp4
