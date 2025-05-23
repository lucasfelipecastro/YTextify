# 🎙️ YTextify — YouTube Video Transcriber via Terminal

**YTextify** is a command-line tool written in Python that downloads YouTube videos and automatically transcribes their audio using AI. It’s perfect for generating subtitles, creating documentation, or studying spoken content.

## ✨ Features

- 📥 Download YouTube videos via `yt-dlp` to extract the best quality audio stream.
- 🧠 Transcribe audio using OpenAI's `whisper` model. Choose from base, small, medium, or large for different speed/accuracy needs.
- ✅ Terminal-based interface — Simple and fast CLI workflow, no need for graphical setup.
- 🔍 Safe filename handling — Sanitizes video titles to prevent filesystem issues.
- 💬 Auto language detection — Detects spoken language automatically during transcription.
- 📁 Organized output — Saves transcripts in a structured transcripts/ directory with video titles.
- 📊 Custom logging — Generates per-video log files in the logs/ directory for debugging or review.
- 🛑 Dependency checks — Validates that ffmpeg, yt-dlp, and whisper are working correctly before starting.
- 💡 Helpful prompts & color feedback — Improves UX with colorful messages and helpful next steps using colorama.
- ✂️ Skips redundant downloads — Detects and skips audio downloads when the file already exists.
- 📄 Detailed process logs saved separately per video in the logs/ folder for debugging.
- 🤝 Developer contact info displayed — Encourages feedback and collaboration.

## 🖥️ Compatibility

> ⚠️ This tool is currently designed and tested only on **Windows** systems.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/lucasfelipecastro/ytextify.git
cd ytextify
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the tool
```bash
python ytextify.py
```
You will be prompted to enter a YouTube URL. The video will be downloaded and transcribed, and the output will be saved in the transcripts/ folder.


### ⚠️ Important Notes

  - Transcription time depends on video length. Do not close the terminal until the process finishes.

  - CPU usage is supported, but GPU acceleration is recommended for better performance.

  - Some videos may not be downloadable due to restrictions. The app will show an error if that happens.



## ℹ️ Troubleshooting: FFmpeg not found?
If you see an error like `[ERROR] FFmpeg not found. Please install FFmpeg and add it to your system PATH.`, follow these steps:

### 🛠️ How to Add FFmpeg to Windows PATH

1. **Download FFmpeg**  
   Go to the official site: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)  
   - Click on “Windows” → choose “Windows builds from gyan.dev” or another trusted provider.
   - Download the **release full build** `.zip` file.

2. **Extract and Move**  
   - Extract the `.zip` file using right-click → “Extract All...”
   - Rename the folder to `ffmpeg` and move it to a permanent location like `C:\ffmpeg`.

3. **Copy the `bin` Path**  
   - Navigate to `C:\ffmpeg\bin`
   - Copy the full path (e.g., `C:\ffmpeg\bin`) — this is the folder you must add to PATH.

4. **Add to System PATH**  
   - Press `Win + S` and search for “Environment Variables”.
   - Open **Edit the system environment variables**.
   - Click **Environment Variables** → under “System variables”, select `Path` → click **Edit**.
   - Click **New**, then paste the path you copied.
   - Click **OK** to apply.

5. **Test in Terminal**  
   Open a new terminal window and run:
   ```bash
   ffmpeg -version
   ```

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
