import yt_dlp, whisper, os, re, warnings, logging, subprocess, sys
from colorama import init, Fore
from urllib.parse import urlparse, parse_qs
from tqdm import tqdm

warnings.filterwarnings('ignore', category=UserWarning, module='whisper')
AUDIO_DIR = 'audio'
TRANSCRIPT_DIR = 'transcripts'
LOG_DIR = 'logs'
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
init(autoreset=True)

def check_dependencies():
    print(f'{Fore.CYAN}[CHECK] Verifying required dependencies...\n')

    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f'{Fore.GREEN}[OK] FFmpeg found in PATH.')
    except FileNotFoundError:
        print(f'{Fore.RED}[ERROR] FFmpeg not found. Please install FFmpeg and add it to your system PATH.')
        sys.exit(1)

    try:
        _ = whisper.load_model('base')
        print(f'{Fore.GREEN}[OK] Whisper model loaded successfully.')
    except Exception as e:
        print(f'{Fore.RED}[ERROR] Failed to load Whisper model: {e}')
        sys.exit(1)

    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            ydl.extract_info('https://www.youtube.com/watch?v=YE7VzlLtp-4', download=False)
        print(f'{Fore.GREEN}[OK] yt_dlp is working correctly.')
    except Exception as e:
        print(f'{Fore.RED}[ERROR] yt_dlp failed to extract video info: {e}')
        logging.exception('yt_dlp test video check failed')
        sys.exit(1)

    print(f'\n{Fore.LIGHTGREEN_EX}[INFO] All dependencies are ready!\n')


# dynamic log configuration
def dynamic_log_config(safe_title):
    log_path = os.path.join(LOG_DIR, f'{safe_title}.log')
    logging.basicConfig(
        filename = log_path,
        level = logging.INFO,
        format = '%(asctime)s - %(levelname)s - %(message)s\n',
        encoding = 'utf-8',
        force= True  # force logger reset when changing files
    )
    logging.info('Logging started for video: %s', safe_title)

def show_contact_info():
    print(f'{Fore.LIGHTYELLOW_EX}✨ Developed by Lucas Felipe')
    print(f'{Fore.LIGHTYELLOW_EX}🔗 GitHub: https://github.com/lucasfelipecastro')
    print(f'{Fore.LIGHTYELLOW_EX}💼 LinkedIn: https://linkedin.com/in/lucasfelipecastro')
    print(f'{Fore.LIGHTYELLOW_EX}📧 Email: lucassantanafelipe@gmail.com')

def sanitize_filename(title):
    return re.sub(r'[^\w\-_. ]', '_', title).replace(' ', '_').strip()

def extract_video_id(youtube_url):
    parsed_url = urlparse(youtube_url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path.strip('/')
    return None

def is_valid_youtube_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        return False
    if parsed.hostname not in ('www.youtube.com', 'youtube.com', 'youtu.be'):
        return False
    video_id = extract_video_id(url)
    return video_id is not None

def check_existing_transcript(title: str, model_name: str) -> str | None:
    filename = f'{title}_{model_name}.txt'
    filepath = os.path.join('transcripts', filename)
    if os.path.exists(filepath):
        print(f"{Fore.RED}[INFO] Transcript already exists: '{filename}'")
        return filepath
    return None

def choose_model():
    print('\nSelect Whisper model:')
    print('1. base   → Fast, low accuracy')
    print('2. small  → Balanced speed and accuracy')
    print('3. medium → Slower, more accurate')
    print('4. large  → Best accuracy, very slow & uses lots of RAM')

    model_map = {
        '1': 'base',
        '2': 'small',
        '3': 'medium',
        '4': 'large'
    }

    choice = input('Enter model number [1-4]: ').strip()
    return model_map.get(choice, 'base')  # default to 'base' if invalid

def skip_line():
    print()
    return

def download_audio(youtube_url, output_dir='audio'):
    try:
        logging.info(f'Attempting to download audio: {youtube_url}')
        video_id = extract_video_id(youtube_url)
        if not video_id:
            raise ValueError(f'{Fore.RED}[ERROR] Could not extract video ID from URL.')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            raw_title = info.get('title', 'audio') if info else 'audio'
            safe_title = sanitize_filename(raw_title)
            dynamic_log_config(safe_title)

            skip_line()
            print(f'{Fore.LIGHTGREEN_EX}[INFO] Downloading audio for video: {safe_title}')

        final_path = os.path.join(output_dir, f'{safe_title}.mp3')
        if os.path.exists(final_path):
            logging.warning(f"Audio already exists for '{safe_title}'. Skipping download.")
            print(f'{Fore.YELLOW}[INFO] Audio file already exists for this video in {final_path}. Skipping download.')
            skip_line()
            print(f'{Fore.CYAN}Choose another template to transcribe the audio already downloaded to your machine:')
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

        temp_path = os.path.join(output_dir, 'temp_audio.mp3')
        if not os.path.exists(temp_path):
            raise FileNotFoundError('MP3 file not found after download.')

        os.rename(temp_path, final_path)
        return final_path, safe_title
    
    except Exception as e:
        skip_line()
        logging.exception('Exception occurred while downloading audio')
        print(f'{Fore.RED}[ERROR] Failed to download audio: {e}')
        return None, None
    
def transcribe_audio(audio_path, model_name, title, output_path=TRANSCRIPT_DIR):
    try:
        logging.info(f'Starting transcription - Title: {title}, Model: {model_name}')
        skip_line()
        print(f'{Fore.LIGHTGREEN_EX}[INFO] Transcribing audio: {title} - model: ({model_name}). Please wait...')

        model = whisper.load_model(model_name)
        result = model.transcribe(audio_path)

        skip_line()
        print(f'{Fore.YELLOW}⚠️ Finalizing transcription. This may take a little longer depending on the video length...')

        detected_language = result.get('language', 'unknown')

        if isinstance(detected_language, str):
            logging.info(f'Detected language: {detected_language.upper()} for title: {title}')
            skip_line()
            print(f'{Fore.LIGHTGREEN_EX}[INFO] Language detected: {detected_language.upper()}')
        else:
            skip_line()
            print('[INFO] Language detected: UNKNOWN')

        filename = f'{title}_{model_name}.txt'
        transcript_file = os.path.join(output_path, filename)
        logging.info(f'Transcription saved: {transcript_file}')

        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(str(result['text']))

        print(f'{Fore.LIGHTGREEN_EX} ➤ Transcription completed. Check the .txt file in {output_path}/.')
        return transcript_file

    except Exception as e:
        logging.exception('Transcription failed')
        print(f'{Fore.RED}[ERROR] Transcription failed: {e}')
        return None

    
def process_video(youtube_url):
    try:
        logging.info(f'Starting process for URL: {youtube_url}')
        video_id = extract_video_id(youtube_url)
        if not video_id:
            skip_line()
            logging.error(f'{Fore.RED}Failed to extract video ID from URL: {youtube_url}')
            return

        audio_path, safe_title = download_audio(youtube_url)

        model_name = choose_model()
        transcript_filename = f'({model_name})_{safe_title}.txt'
        transcript_path = os.path.join(TRANSCRIPT_DIR, transcript_filename)

        if os.path.exists(transcript_path):
            skip_line()
            print(f'{Fore.CYAN}[INFO] Transcript already exists for this video ({model_name}).')
            choice = input('Do you want to transcribe using a different model? (y/N): ').strip().lower()
            if choice != 'y':
                logging.info(f"User skipped transcription for model '{model_name}' and video '{safe_title}'.")
                skip_line()
                print(f'{Fore.LIGHTGREEN_EX}[INFO] Skipping transcription.')
                return transcript_path
            
            model_name = choose_model()
            transcript_filename = f'({model_name})_{safe_title}.txt'
            transcript_path = os.path.join(TRANSCRIPT_DIR, transcript_filename)
            

        transcript_path = transcribe_audio(audio_path, model_name, safe_title)
        logging.info(f'Transcription completed: {transcript_path}')
        return transcript_path
    
    except Exception as e:
        skip_line()
        logging.exception('Failed to process video')
        print(f'{Fore.RED}[ERROR] Failed to process video: {e}')
        return None


if __name__ == '__main__':
    try:
        print(f'{Fore.LIGHTYELLOW_EX}Welcome to YTextify!')
        check_dependencies()
        print(f'{Fore.LIGHTYELLOW_EX}This tool helps you transcribe YouTube videos using Whisper.')
        skip_line()

        print(f'{Fore.LIGHTYELLOW_EX}Please ensure you have the required dependencies installed.')
        
        while True:
            url = input(f'{Fore.CYAN}Enter the Youtube video URL: ').strip()
            if is_valid_youtube_url(url):
                break
            print(f'{Fore.RED}[ERROR] Invalid Youtube URL. Please enter a valid link. \n')

        result_path = process_video(url)
        skip_line()
        skip_line()

        print(f'{Fore.LIGHTYELLOW_EX}Thank you for using YTextify!')

        if result_path:
            print(f'\n{Fore.CYAN}[INFO] Open the transcript file at: {result_path}')
        
        skip_line()

        print(f'{Fore.LIGHTYELLOW_EX}➤ If you have any questions or feedback, feel free to reach out.')
        show_contact_info()

    except KeyboardInterrupt:
        print(f'\n{Fore.RED}[INFO] Process interrupted by user.')
    except Exception as e:
        print(f'{Fore.RED}[ERROR] Unexpected error: {e}')
