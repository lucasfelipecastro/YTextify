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

    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        video_title = "audio"
        if info:
            video_title = info.get("title", "audio").replace(" ", "_").replace("/", "_")


    audio_temp_path = os.path.join(output_dir, "audio_temp.webm")
    audio_final_path = os.path.join(output_dir, f"{video_title}.mp3")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': audio_temp_path,
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    ffmpeg.input(audio_temp_path).output(audio_final_path, format='mp3', acodec='libmp3lame').run(overwrite_output=True)

    os.remove(audio_temp_path)

    return audio_final_path, video_title


def transcribe_audio(audio_path, video_title, output_path=TRANSCRIPT_DIR):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)

    safe_title = video_title.replace(" ", "_").replace("/", "_")
    transcript_file = os.path.join(output_path, f"{safe_title}.txt")

    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(str(result["text"]))

    return transcript_file



def process_video(youtube_url):
    audio_path, title = download_audio(youtube_url)
    transcript_path = transcribe_audio(audio_path, title)
    return transcript_path


if __name__ == "__main__":
    url = input("Enter the YouTube video URL: ")
    transcript = process_video(url)
    print(f"Transcription saved at: {transcript}")
