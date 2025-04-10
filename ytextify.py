from pytube import YouTube
import yt_dlp, ffmpeg, whisper, os, time, threading, re
from tqdm import tqdm
from colorama import init, Fore, Style

AUDIO_DIR = "audio"
TRANSCRIPT_DIR = "transcripts"

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

init(autoreset=True)

def sanitize_filename(title):
    return re.sub(r'[^\w\-_. ]', '_', title).replace(" ", "_")

def choose_model():
    print("\nSelect Whisper model:")
    print("1. base   → Fast, low accuracy")
    print("2. small  → Balanced speed and accuracy")
    print("3. medium → Slower, more accurate")
    print("4. large  → Best accuracy, very slow & uses lots of RAM")

    model_map = {
        "1": "base",
        "2": "small",
        "3": "medium",
        "4": "large"
    }

    choice = input("Enter model number [1-4]: ").strip()
    return model_map.get(choice, "base")  # default to "base" if invalid

def download_audio(youtube_url, output_dir="audio"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        raw_title = info.get("title", "audio") if info else "audio"
        safe_title = sanitize_filename(raw_title)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    downloaded_mp3 = None
    for file in os.listdir(output_dir):
        if file.lower().endswith(".mp3"):
            downloaded_mp3 = os.path.join(output_dir, file)
            break

    if not downloaded_mp3:
        raise FileNotFoundError("MP3 file not found after download.")

    final_path = os.path.join(output_dir, f"{safe_title}.mp3")
    os.rename(downloaded_mp3, final_path)

    return final_path, safe_title

spinner_done = False

def spinner(message="Transcribing audio..."):
    symbols = ['|', '/', '-', '\\']
    idx = 0
    while not spinner_done:
        print(f"\r{Fore.CYAN}{message} {symbols[idx % len(symbols)]}", end="")
        idx += 1
        time.sleep(0.1)

def transcribe_audio(audio_path, model_name, title, output_path=TRANSCRIPT_DIR):
    print("Transcribing... Please wait.")
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path)
    detected_language = result.get('language', 'unknown')
    if isinstance(detected_language, str):
        print(f"[INFO] Language detected: {detected_language.upper()}")
    else:
        print("[INFO] Language detected: UNKNOWN")
    
    transcript_file = os.path.join(TRANSCRIPT_DIR, f"{title}.txt")

    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(str(result["text"]))

    print("Transcription completed.")
    return transcript_file


def process_video(youtube_url):
    model_name = choose_model()
    audio_path, title = download_audio(youtube_url)
    transcript_path = transcribe_audio(audio_path, model_name, title)
    return transcript_path


if __name__ == "__main__":
    url = input("Enter the YouTube video URL: ")
    process_video(url)
