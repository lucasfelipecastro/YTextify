import os
from pytube import YouTube
import whisper
import ffmpeg
import yt_dlp

AUDIO_DIR = "audio"
TRANSCRIPT_DIR = "transcripts"

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

def download_audio(youtube_url, output_dir="audio"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_dir}/audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    return os.path.join(output_dir, "audio.mp3")


def transcribe_audio(audio_path, output_path=TRANSCRIPT_DIR):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)

    video_title = os.path.splitext(os.path.basename(audio_path))[0]
    transcript_file = os.path.join(output_path, f"{video_title}.txt")

    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(result["text"])

    return transcript_file

def process_video(youtube_url):
    audio_path = download_audio(youtube_url)
    transcript_path = transcribe_audio(audio_path)
    return transcript_path

if __name__ == "__main__":
    url = input("Enter the YouTube video URL: ")
    transcript = process_video(url)
    print(f"Transcription saved at: {transcript}")
