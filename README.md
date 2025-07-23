# Whisper Transcription Web App

A modern web application for transcribing audio and video files using OpenAI's Whisper model (local or API).

## Features

- **Flexible Processing**: Choose between local Whisper model or OpenAI's API
- **Local Processing**: Uses Whisper model running on your machine (no API keys needed)
- **Cloud Processing**: Optionally use OpenAI's Whisper API for faster and more accurate transcriptions
- **Multiple Formats**: Supports audio (MP3, WAV, M4A, AAC, OGG) and video (MP4, AVI, MOV, MKV, FLV, WebM)
- **Language Support**: Auto-detection or manual selection from 13+ languages
- **SRT Export**: Generate subtitle files in SRT format
- **Modern UI**: Beautiful, responsive interface with drag-and-drop support
- **Progress Tracking**: Real-time transcription progress indicator

## Quick Start (Windows)

### Option 1: Automatic Setup
1. **Double-click `setup.bat`** - This will install everything and optionally run the app

### Option 2: Manual Steps
1. **Double-click `install.bat`** - This will create a virtual environment and install all dependencies
2. **Double-click `run.bat`** - This will start the application

## Using OpenAI Whisper API

For better accuracy and faster processing, you can use OpenAI's Whisper API:

1. Get your API key from [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. Set the following environment variables:
   ```bash
   # Windows (Command Prompt)
   set OPENAI_API_KEY=your-api-key-here
   set USE_OPENAI_API=true
   
   # Windows (PowerShell)
   $env:OPENAI_API_KEY="your-api-key-here"
   $env:USE_OPENAI_API="true"
   
   # Linux/macOS
   export OPENAI_API_KEY=your-api-key-here
   export USE_OPENAI_API=true
   ```
3. Restart the application

## Manual Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install FFmpeg** (required for audio/video processing):
   - **Windows**: Download from https://ffmpeg.org/download.html
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

## Usage

1. **Start the application:**
   ```bash
   python app.py
   ```
   
   Or use the batch files:
   - **Windows**: Double-click `run.bat`

2. **Open your browser** and go to `http://localhost:5000`

3. **Upload a file** by dragging and dropping or clicking "Choose File"

4. **Select options:**
   - Language: Auto-detect or choose specific language
   - Format: Text only or Text + SRT subtitles

5. **Click "Start Transcription"** and wait for processing

6. **Download results:**
   - Copy transcribed text to clipboard
   - Download SRT subtitle file (if selected)

## Supported File Types

**Audio:** MP3, WAV, M4A, AAC, OGG
**Video:** MP4, AVI, MOV, MKV, FLV, WebM

## Technical Details

- **Backend**: Flask web framework
- **AI Model**: OpenAI Whisper (base model for balanced speed/accuracy)
- **Frontend**: Vanilla JavaScript with modern CSS
- **File Size Limit**: 500MB maximum
- **Processing**: Runs entirely on your local machine

## Model Information

The app uses Whisper's "base" model by default, which provides a good balance of speed and accuracy. You can modify `app.py` to use other models:

- `tiny`: Fastest, least accurate
- `base`: Good balance (default)
- `small`: Better accuracy, slower
- `medium`: High accuracy, much slower
- `large`: Best accuracy, very slow

## Troubleshooting

- **"No module named 'whisper'"**: Run `pip install -r requirements.txt`
- **FFmpeg errors**: Ensure FFmpeg is installed and in your PATH
- **Large file issues**: Check file size limit (500MB) and available disk space
- **Slow processing**: Consider using a smaller Whisper model or upgrading hardware

## License

This project uses OpenAI's Whisper model. Please refer to their license terms.
