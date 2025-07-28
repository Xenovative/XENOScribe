import os
import tempfile
import whisper
import openai
import hashlib
import signal
import time
from flask import Flask, request, jsonify, render_template, send_file, session, redirect, url_for
from werkzeug.utils import secure_filename
import logging
from datetime import datetime
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from functools import wraps

# Load environment variables first
load_dotenv()

# Configure logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xenoscribe.log')
log_level = os.getenv('LOG_LEVEL', 'INFO')

# Ensure log directory exists
os.makedirs(os.path.dirname(log_file), exist_ok=True)

# Configure logging
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_file)
    ]
)

logger = logging.getLogger(__name__)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='assets', static_url_path='/assets')

# Parse MAX_CONTENT_LENGTH safely
def parse_max_content_length():
    max_content = os.getenv('MAX_CONTENT_LENGTH', '').split('#')[0].strip()  # Remove comments
    try:
        return int(max_content) if max_content else 2 * 1024 * 1024 * 1024  # Default 2GB
    except ValueError:
        return 2 * 1024 * 1024 * 1024  # Default 2GB on error

app.config['MAX_CONTENT_LENGTH'] = parse_max_content_length()
app.secret_key = os.urandom(24)  # For session management

# Configuration
class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    USE_OPENAI_API = os.getenv('USE_OPENAI_API', 'false').lower() == 'true'
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'base')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', os.path.join(tempfile.gettempdir(), 'xenoscribe_uploads'))
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'mp3,wav,mp4,avi,mov,mkv,flv,webm,m4a,aac,ogg').split(','))

app.config.from_object(Config)

# Authentication configuration
app.config['USERS'] = {
    os.getenv('ADMIN_USERNAME', 'admin'): {
        'password': hashlib.sha256(os.getenv('ADMIN_PASSWORD', 'admin123').encode()).hexdigest(),
        'name': 'Admin'
    }
}

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
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")

def with_timeout(timeout_seconds):
    """Decorator to add timeout to functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Set up the timeout
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
            
            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Cancel the alarm
                return result
            except TimeoutError:
                logger.error(f"Function {func.__name__} timed out after {timeout_seconds} seconds")
                raise
            finally:
                signal.signal(signal.SIGALRM, old_handler)
        return wrapper
    return decorator

def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format"""
    if seconds is None:
        return "00:00:00,000"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

def get_segment_value(segment, key, default=None):
    """Safely get value from segment whether it's a dict or object"""
    if hasattr(segment, key):  # Object access
        return getattr(segment, key, default)
    return segment.get(key, default)  # Dictionary access

def generate_srt(segments):
    """Generate SRT format from Whisper segments"""
    if not segments:
        return ""
        
    srt_content = ""
    for i, segment in enumerate(segments, 1):
        start = get_segment_value(segment, 'start', 0)
        end = get_segment_value(segment, 'end', 0)
        text = get_segment_value(segment, 'text', '').strip()
        
        if not text:  # Skip empty segments
            continue
            
        start_time = format_timestamp(start)
        end_time = format_timestamp(end)
        srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
    return srt_content.strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    user = app.config['USERS'].get(username)
    if user and user['password'] == hashlib.sha256(password.encode()).hexdigest():
        session['user'] = {
            'username': username,
            'name': user['name']
        }
        return jsonify({'message': 'Login successful', 'user': session['user']})
    
    return jsonify({'error': 'Invalid username or password'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    session.pop('user', None)
    return jsonify({'message': 'Logout successful'})

@app.route('/api/check_auth')
def check_auth():
    if 'user' in session:
        return jsonify({'authenticated': True, 'user': session['user']})
    return jsonify({'authenticated': False})

def transcribe_file_with_openai(file_path: str, language: str = None) -> Dict[str, Any]:
    """Transcribe audio file using OpenAI's Whisper API"""
    with open(file_path, 'rb') as audio_file:
        response = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language if language != 'auto' else None,
            response_format='verbose_json',
            timestamp_granularities=["segment"]
        )
    
    # Extract the data we need from the response
    text = getattr(response, 'text', '')
    language = getattr(response, 'language', language if language != 'auto' else 'en')
    
    # Handle segments safely
    segments = []
    if hasattr(response, 'segments'):
        segments = [{
            'id': i,
            'start': getattr(segment, 'start', 0),
            'end': getattr(segment, 'end', 0),
            'text': getattr(segment, 'text', '').strip()
        } for i, segment in enumerate(getattr(response, 'segments', []))]
    
    return {
        'text': text,
        'language': language,
        'segments': segments
    }

@app.route('/transcribe', methods=['POST'])
@login_required
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
        
        # Get file size for logging
        file_size = os.path.getsize(temp_path)
        logger.info(f"Transcribing file: {filename} (Size: {file_size / (1024*1024):.1f} MB)")
        
        start_time = time.time()
        
        try:
            # Transcribe using OpenAI API if configured
            if Config.USE_OPENAI_API and Config.OPENAI_API_KEY:
                logger.info("Using OpenAI Whisper API for transcription")
                result = transcribe_file_with_openai(temp_path, language)
            else:
                # Fall back to local Whisper model
                logger.info(f"Using local Whisper model: {Config.WHISPER_MODEL}")
                model = whisper.load_model(Config.WHISPER_MODEL)
                result = model.transcribe(temp_path, language=language if language != 'auto' else None)
                
                # Format segments to match OpenAI's response format
                segments = [{
                    'id': i,
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip()
                } for i, segment in enumerate(result.get('segments', []))]
                
                result = {
                    'text': result.get('text', ''),
                    'language': language if language != 'auto' else 'en',
                    'segments': segments
                }
            
            # Generate SRT if requested
            if output_format.lower() == 'srt':
                srt_content = generate_srt(result.get('segments', []))
                response_data = {
                    'filename': os.path.splitext(filename)[0] + '.srt',
                    'srt': srt_content
                }
            else:
                response_data = {
                    'text': result.get('text', ''),
                    'language': result.get('language', language if language != 'auto' else 'en'),
                    'segments': result.get('segments', [])
                }
            
            # Log completion time
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"Transcription successful for {filename} (Duration: {duration:.1f}s)")
            
            response = jsonify(response_data)
            return response
            
        except TimeoutError:
            logger.error(f"Transcription timed out for {filename}")
            return jsonify({'error': 'Transcription timed out. File may be too large or complex.'}), 504
        except Exception as e:
            logger.error(f"Error during transcription of {filename}: {str(e)}")
            # Check if it's a memory error
            if 'memory' in str(e).lower() or 'out of memory' in str(e).lower():
                return jsonify({'error': 'File too large for available memory. Try a smaller file or use a more powerful server.'}), 413
            return jsonify({'error': f'Transcription failed: {str(e)}'}), 500
            
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_path}: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error in transcribe: {str(e)}")
        return jsonify({'error': str(e)}), 500

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
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, host=host, port=port)
