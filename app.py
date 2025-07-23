import os
import tempfile
import whisper
import openai
from flask import Flask, request, jsonify, render_template, send_file, session
from werkzeug.utils import secure_filename
import logging
from datetime import datetime
import json
from typing import Optional, Dict, Any

app = Flask(__name__, static_folder='assets', static_url_path='/assets')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB max file size
app.secret_key = os.urandom(24)  # For session management

# Configuration
class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    USE_OPENAI_API = os.getenv('USE_OPENAI_API', 'false').lower() == 'true'
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')

app.config.from_object(Config)

if Config.OPENAI_API_KEY and Config.USE_OPENAI_API:
    openai.api_key = Config.OPENAI_API_KEY
    logger.info("Using OpenAI Whisper API for transcription")
else:
    logger.info(f"Using local Whisper model: {Config.WHISPER_MODEL}")
    model = whisper.load_model(Config.WHISPER_MODEL)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Whisper model (using base model for balance of speed/accuracy)
logger.info("Loading Whisper model...")
model = whisper.load_model("base")
logger.info("Whisper model loaded successfully")

ALLOWED_EXTENSIONS = {'mp3', 'wav', 'mp4', 'avi', 'mov', 'mkv', 'flv', 'webm', 'm4a', 'aac', 'ogg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def generate_srt(segments):
    """Generate SRT format from Whisper segments"""
    srt_content = ""
    for i, segment in enumerate(segments, 1):
        start_time = format_timestamp(segment['start'])
        end_time = format_timestamp(segment['end'])
        text = segment['text'].strip()
        srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
    return srt_content

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_file_with_openai(file_path: str, language: str = None) -> Dict[str, Any]:
    """Transcribe audio file using OpenAI's Whisper API"""
    with open(file_path, 'rb') as audio_file:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language if language != 'auto' else None,
            response_format='verbose_json',
            timestamp_granularities=["segment"]
        )
    
    segments = [{
        'id': i,
        'start': segment['start'],
        'end': segment['end'],
        'text': segment['text'].strip()
    } for i, segment in enumerate(transcript.segments)]
    
    return {
        'text': transcript.text,
        'language': transcript.language,
        'segments': segments
    }

def transcribe():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not supported'}), 400
        
        # Get options
        language = request.form.get('language', 'auto')
        output_format = request.form.get('format', 'text')
        
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        logger.info(f"Transcribing file: {filename}")
        
        # Transcribe with either local model or OpenAI API
        if app.config['USE_OPENAI_API'] and app.config['OPENAI_API_KEY']:
            if language == 'auto':
                result = transcribe_file_with_openai(temp_path)
            else:
                result = transcribe_file_with_openai(temp_path, language)
        else:
            # Local Whisper model
            if language == 'auto':
                result = model.transcribe(temp_path)
            else:
                result = model.transcribe(temp_path, language=language)
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Prepare response based on format
        if output_format == 'srt':
            srt_content = generate_srt(result['segments'])
            response_data = {
                'text': result['text'],
                'srt': srt_content,
                'language': result.get('language', 'en'),
                'segments': result['segments']
            }
        else:
            response_data = {
                'text': result['text'],
                'language': result.get('language', 'en'),
                'segments': result['segments']
            }
        
        logger.info(f"Transcription completed for {filename}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        return jsonify({'error': f'Transcription failed: {str(e)}'}), 500

@app.route('/download-srt', methods=['POST'])
def download_srt():
    try:
        data = request.get_json()
        srt_content = data.get('srt', '')
        filename = data.get('filename', 'transcription.srt')
        
        # Create temporary SRT file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(srt_content)
            temp_path = temp_file.name
        
        return send_file(temp_path, as_attachment=True, download_name=filename, mimetype='text/plain')
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
