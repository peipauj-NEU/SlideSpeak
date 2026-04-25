#!/usr/bin/env python3
"""
Generate per-slide MP3 audio files from a slide-change-delimited transcript
using Google Text-to-Speech (gTTS).  No local TTS engine required.

Markers consumed:
  [SLIDE CHANGE]  – splits transcript into per-slide sections
  [PAUSE=…]       – stripped (gTTS handles natural pacing)
"""

import os
import re

from gtts import gTTS


def _clean_slide_text(text: str) -> str:
    """Remove processing markers so they are not spoken aloud."""
    text = re.sub(r'\[SLIDE CHANGE\]', '', text)
    text = re.sub(r'\[PAUSE=\d+\]', '', text)
    return text.strip()


def process_transcript(transcript_file: str, output_dir: str, lang: str = "en") -> list[str]:
    """
    Read *transcript_file*, split at [SLIDE CHANGE], and write one MP3 per
    slide section into *output_dir*.

    Returns the list of generated MP3 file paths.
    """
    os.makedirs(output_dir, exist_ok=True)

    with open(transcript_file, "r", encoding="utf-8") as fh:
        transcript = fh.read()

    sections = re.split(r'\[SLIDE CHANGE\]', transcript)
    generated: list[str] = []

    for i, section in enumerate(sections, start=1):
        text = _clean_slide_text(section)
        if not text:
            continue
        out_path = os.path.join(output_dir, f"slide{i}.mp3")
        tts = gTTS(text=text, lang=lang)
        tts.save(out_path)
        print(f"  Saved {out_path}")
        generated.append(out_path)

    return generated
