"""
High-Fidelity Studio Neural Audio Narrator for StudyEngine Notes.
Powered by Edge-TTS (Microsoft Azure Neural Voices).
Zero API keys required, broadcast-grade clarity, natural human cadence,
no cracking, and exact sentence-level timing boundaries.
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import edge_tts

logger = logging.getLogger("study_engine.narrator")

BASE_DIR = Path(__file__).parent.parent
AUDIO_CACHE_DIR = BASE_DIR / "data" / "audio_cache"
AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)

VOICES = {
    "christopher": {
        "id": "en-US-ChristopherNeural",
        "name": "Christopher (US Male - Deep & Warm)",
        "label": "Christopher (Warm Narrator)",
        "desc": "Audible / documentary style, deep and soothing"
    },
    "jenny": {
        "id": "en-US-JennyNeural",
        "name": "Jenny (US Female - Natural & Soothing)",
        "label": "Jenny (Soothing Studio)",
        "desc": "Warm, crystal-clear studio narrator, very easy on the ears"
    },
    "ryan": {
        "id": "en-GB-RyanNeural",
        "name": "Ryan (UK Male - BBC Cadence)",
        "label": "Ryan (BBC British Male)",
        "desc": "Articulate, crisp British cadence, Oxford style"
    },
    "sonia": {
        "id": "en-GB-SoniaNeural",
        "name": "Sonia (UK Female - Soft & Articulate)",
        "label": "Sonia (Soft British Female)",
        "desc": "Gentle, polite British voice with pristine diction"
    },
    "neerja": {
        "id": "en-IN-NeerjaNeural",
        "name": "Neerja (Indian English - Warm & Natural)",
        "label": "Neerja (Natural Indian English)",
        "desc": "Authentic, fluent Indian English, ideal for IIMB curriculum"
    },
    "guy": {
        "id": "en-US-GuyNeural",
        "name": "Guy (US Male - Crisp & Conversational)",
        "label": "Guy (Conversational US)",
        "desc": "Crisp, modern, engaging male voice"
    }
}

DEFAULT_VOICE = "christopher"

def list_curated_voices() -> List[Dict[str, str]]:
    return [
        {
            "key": k,
            "id": v["id"],
            "name": v["name"],
            "label": v["label"],
            "desc": v["desc"]
        }
        for k, v in VOICES.items()
    ]

def prepare_speakable_text(title: str, notes_md: str) -> str:
    """
    Cleans markdown into smooth, pleasant, phonetically natural spoken text.
    Replaces math symbols, arrows, abbreviations, and table noise.
    """
    cleaned_lines = [f"{title}."]

    for line in notes_md.split('\n'):
        line = line.strip()
        if not line:
            continue
        # Skip raw markdown code blocks, tables, dividers
        if line.startswith('```') or line.startswith('|') or line.startswith('---'):
            continue
        # Clean heading markers, bullet points, numbers
        clean = re.sub(r'^[#*\-+\d.]+\s*', '', line).strip()
        # Clean formatting asterisks, backticks, tildes
        clean = re.sub(r'[*_`~]', '', clean)
        # Clean links [text](url) -> text
        clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean)
        # Spoken representations for mathematical and logical symbols
        clean = clean.replace('→', ' leads to ').replace('←', ' comes from ')
        clean = clean.replace('≠', ' is not equal to ')
        clean = clean.replace('≤', ' is less than or equal to ').replace('≥', ' is greater than or equal to ')
        clean = clean.replace('&', ' and ')
        clean = re.sub(r'\bvs\.?\b', 'versus', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\be\.g\.?,?\b', 'for example,', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\bi\.e\.?,?\b', 'that is,', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\betc\.?\b', 'et cetera,', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\s+', ' ', clean).strip()

        if len(clean) >= 3:
            if not clean.endswith(('.', '?', '!', ':')):
                clean += '.'
            cleaned_lines.append(clean)

    return ' '.join(cleaned_lines)

async def synthesize_topic_audio(topic_id: str, title: str, notes_md: str, voice_key: str = "christopher") -> Dict[str, Any]:
    """
    Synthesizes neural audio with sentence boundaries and saves to disk cache.
    """
    if voice_key not in VOICES:
        voice_key = DEFAULT_VOICE

    voice_info = VOICES[voice_key]
    voice_id = voice_info["id"]

    mp3_path = AUDIO_CACHE_DIR / f"{topic_id}_{voice_key}.mp3"
    json_path = AUDIO_CACHE_DIR / f"{topic_id}_{voice_key}.json"

    # Return cached if exists
    if mp3_path.exists() and json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception:
            pass

    speakable_text = prepare_speakable_text(title, notes_md)
    if not speakable_text.strip():
        speakable_text = f"Notes for {title}."

    logger.info(f"Synthesizing studio neural audio for topic {topic_id} ({voice_key})...")
    communicate = edge_tts.Communicate(speakable_text, voice_id)

    sentences = []
    audio_data = bytearray()

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.extend(chunk["data"])
        elif chunk["type"] == "SentenceBoundary":
            start_sec = round(chunk["offset"] / 10000000.0, 2)
            dur_sec = round(chunk["duration"] / 10000000.0, 2)
            sentences.append({
                "text": chunk["text"],
                "start": start_sec,
                "end": round(start_sec + dur_sec, 2),
                "duration": dur_sec
            })

    # Save audio file
    with open(mp3_path, "wb") as f:
        f.write(audio_data)

    total_duration = sentences[-1]["end"] if sentences else 0.0

    metadata = {
        "topic_id": topic_id,
        "title": title,
        "voice": voice_key,
        "voice_name": voice_info["name"],
        "audio_url": f"/api/audio/{topic_id}_{voice_key}.mp3",
        "total_duration": total_duration,
        "sentence_count": len(sentences),
        "sentences": sentences
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    logger.info(f"Successfully generated studio neural audio for {topic_id}: {total_duration:.1f}s ({len(audio_data)} bytes)")
    return metadata

def get_cached_topic_audio(topic_id: str, voice_key: str = "christopher") -> Optional[Dict[str, Any]]:
    if voice_key not in VOICES:
        voice_key = DEFAULT_VOICE
    json_path = AUDIO_CACHE_DIR / f"{topic_id}_{voice_key}.json"
    mp3_path = AUDIO_CACHE_DIR / f"{topic_id}_{voice_key}.mp3"
    if json_path.exists() and mp3_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None
