import os
from pytube import YouTube
import whisper
import ffmpeg

AUDIO_DIR = "audio"
TRANSCRIPT_DIR = "transcripts"

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
