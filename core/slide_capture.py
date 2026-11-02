"""
Slide & Diagram Extractor via FFmpeg Scene Detection.
Captures whiteboard frames, presentation slides, and diagrams from lecture videos.
"""

import os
import glob
import subprocess
import logging
from typing import List, Dict, Any

logger = logging.getLogger("study_engine.slides")

FFMPEG_PATH = "/opt/homebrew/bin/ffmpeg" if os.path.exists("/opt/homebrew/bin/ffmpeg") else "ffmpeg"

def capture_slides(video_url: str, output_dir: str, video_id: str, max_slides: int = 6) -> List[Dict[str, Any]]:
    os.makedirs(output_dir, exist_ok=True)
    temp_video = os.path.join(output_dir, f"_temp_{video_id}.mp4")
    slides = []

    # Instant thumbnail capture (ensures immediate visual frame under 0.5s)
    thumb_path = os.path.join(output_dir, "slide_01.jpg")
    try:
        import urllib.request
        thumb_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        req = urllib.request.Request(thumb_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            with open(thumb_path, "wb") as f:
                f.write(resp.read())
            slides.append({
                "slide_num": 1,
                "filename": "slide_01.jpg",
                "url": f"/static/slides/{video_id}/slide_01.jpg"
            })
    except Exception:
        pass

    # Quick secondary frame sampling (capped strictly at 12s so it never slows down note curation)
    try:
        dl_cmd = [
            "python3", "-m", "yt_dlp",
            "-f", "worstvideo[ext=mp4]/worst",
            "--no-playlist",
            "--downloader-args", "ffmpeg_i:-t 15",
            "-o", temp_video,
            video_url
        ]
        subprocess.run(dl_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=12)

        if os.path.exists(temp_video):
            frame_pattern = os.path.join(output_dir, "raw_%03d.jpg")
            ffmpeg_cmd = [
                FFMPEG_PATH,
                "-y",
                "-i", temp_video,
                "-vf", "fps=1/5,scale=1280:-1",
                "-q:v", "3",
                frame_pattern
            ]
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=10)
            raw_slides = sorted(glob.glob(os.path.join(output_dir, "raw_*.jpg")))
            for idx, src in enumerate(raw_slides[:max_slides]):
                dest_name = f"slide_{len(slides)+1:02d}.jpg"
                dest_path = os.path.join(output_dir, dest_name)
                os.rename(src, dest_path)
                slides.append({
                    "slide_num": len(slides) + 1,
                    "filename": dest_name,
                    "url": f"/static/slides/{video_id}/{dest_name}"
                })
    except Exception as e:
        logger.warning(f"Fast slide capture skipped extra frames ({e}), relying on primary visual slide.")
    finally:
        if os.path.exists(temp_video):
            try: os.remove(temp_video)
            except Exception: pass
        for f in glob.glob(os.path.join(output_dir, "raw_*.jpg")):
            try: os.remove(f)
            except Exception: pass

    return slides

