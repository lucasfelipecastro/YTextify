from pytube import YouTube
import yt_dlp, ffmpeg, whisper, os, time, re, warnings
from tqdm import tqdm
from colorama import init, Fore
from urllib.parse import urlparse, parse_qs

warnings.filterwarnings("ignore", category=UserWarning, module='whisper')
AUDIO_DIR = "audio"
TRANSCRIPT_DIR = "transcripts"

os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

init(autoreset=True)

def sanitize_filename(title):
    return re.sub(r'[^\w\-_. ]', '_', title).replace(" ", "_").strip()

def extract_video_id(youtube_url):
    parsed_url = urlparse(youtube_url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed_url.query).get("v", [None])[0]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path.strip("/")
    return None

def check_existing_transcript(title: str, model_name: str) -> str | None:
    filename = f"{title}_{model_name}.txt"
    filepath = os.path.join("transcripts", filename)
    if os.path.exists(filepath):
        print(f"{Fore.RED}[INFO] Transcript already exists: '{filename}'")
        return filepath
    return None

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

def skip_line():
    print()
    return

def download_audio(youtube_url, output_dir="audio"):
    video_id = extract_video_id(youtube_url)
    if not video_id:
        raise ValueError(f"{Fore.RED}[ERROR] Could not extract video ID from URL.")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        raw_title = info.get("title", "audio") if info else "audio"
        safe_title = sanitize_filename(raw_title)
        skip_line()
        print(f"{Fore.LIGHTGREEN_EX}[INFO] Downloading audio for video: {safe_title}")

    final_path = os.path.join(output_dir, f"{safe_title}.mp3")
    if os.path.exists(final_path):
        print(f"{Fore.YELLOW}[INFO] Audio file already exists for this video in {final_path}. Skipping download.")
        skip_line()
        print(f"{Fore.CYAN}Choose another template to transcribe the audio already downloaded to your machine:")
        return final_path, safe_title

    # downloading audio from youtube with temporary name
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, 'temp_audio.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])

    temp_path = os.path.join(output_dir, "temp_audio.mp3")
    if not os.path.exists(temp_path):
        raise FileNotFoundError("MP3 file not found after download.")

    os.rename(temp_path, final_path)
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
    skip_line()
    print(f"{Fore.LIGHTGREEN_EX}[INFO] Transcribing audio: {title}")
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path)
    detected_language = result.get('language', 'unknown')
    if isinstance(detected_language, str):
        skip_line()
        print(f"{Fore.LIGHTGREEN_EX}[INFO] Language detected: {detected_language.upper()}")
    else:
        skip_line()
        print("[INFO] Language detected: UNKNOWN")
    
    filename = f"{title}_{model_name}.txt"
    transcript_file = os.path.join(output_path, filename)

    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(str(result["text"]))

    print(f"{Fore.LIGHTGREEN_EX}Transcription completed. Check the .txt file in {output_path}.")
    return transcript_file

def process_video(youtube_url):
    video_id = extract_video_id(youtube_url)
    if not video_id:
        skip_line()
        print(f"{Fore.RED}[ERROR] Could not extract video ID from URL.")
        return

    audio_path, safe_title = download_audio(youtube_url)

    model_name = choose_model()
    transcript_filename = f"({model_name})_{safe_title}.txt"
    transcript_path = os.path.join(TRANSCRIPT_DIR, transcript_filename)

    if os.path.exists(transcript_path):
        skip_line()
        print(f"{Fore.CYAN}[INFO] Transcript already exists for this video ({model_name}).")
        choice = input("Do you want to transcribe using a different model? (y/N): ").strip().lower()
        if choice != "y":
            skip_line()
            print(f"{Fore.LIGHTGREEN_EX}[INFO] Skipping transcription.")
            return transcript_path
        
        model_name = choose_model()
        transcript_filename = f"({model_name})_{safe_title}.txt"
        transcript_path = os.path.join(TRANSCRIPT_DIR, transcript_filename)

    transcript_path = transcribe_audio(audio_path, model_name, safe_title)
    return transcript_path


if __name__ == "__main__":
    url = input(f"{Fore.CYAN}Enter the YouTube video URL: ")
    process_video(url)
