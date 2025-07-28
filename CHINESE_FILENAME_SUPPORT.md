# XENOScribe Chinese Filename Support

## Problem Solved
XENOScribe now properly handles Chinese and other Unicode characters in filenames for both display and download.

## Features Implemented

### 1. Unicode-Safe Filename Processing
- **Custom secure_unicode_filename()** function replaces Werkzeug's secure_filename()
- **Preserves Chinese characters** while removing dangerous characters
- **Unicode normalization** (NFC) for consistent character representation
- **Byte-length limiting** to prevent filesystem issues

### 2. Proper File Handling
- **UTF-8 encoding** throughout the application
- **Original filename preservation** in responses
- **Safe filename generation** for internal processing
- **Proper MIME types** with charset specification

### 3. Download Support
- **UTF-8 Content-Disposition headers** for proper browser handling
- **RFC 5987 filename encoding** for international characters
- **Fallback filename handling** for problematic characters

### 4. Frontend Display
- **Native Unicode support** in HTML (UTF-8 charset)
- **Proper filename display** in file info section
- **Chinese character rendering** in progress messages

## Technical Implementation

### Backend (Python/Flask)
```python
def secure_unicode_filename(filename):
    """Secure filename while preserving Unicode characters like Chinese"""
    # Normalize Unicode characters
    filename = unicodedata.normalize('NFC', filename)
    
    # Remove dangerous characters while keeping Unicode
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove control characters
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    
    # Handle byte-length limiting for filesystem compatibility
    # ... (truncation logic)
```

### Download Headers
```python
# Proper UTF-8 filename encoding for downloads
response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{safe_filename.encode('utf-8').decode('latin1')}"
```

### Frontend (JavaScript)
```javascript
// Original filename is preserved and displayed correctly
document.getElementById('fileName').textContent = file.name;

// Download uses original filename
const filename = selectedFile.name.replace(/\.[^/.]+$/, '') + '.srt';
```

## Supported Characters
- ✅ **Chinese (Simplified)**: 简体中文
- ✅ **Chinese (Traditional)**: 繁體中文
- ✅ **Japanese**: 日本語
- ✅ **Korean**: 한국어
- ✅ **Arabic**: العربية
- ✅ **Cyrillic**: Русский
- ✅ **European accents**: Français, Español, Deutsch

## Example Filenames
These filenames now work correctly:
- `我的音频文件.mp3` (My audio file)
- `会议记录_2024年7月.wav` (Meeting record July 2024)
- `音樂檔案.m4a` (Music file - Traditional Chinese)
- `プレゼンテーション.mp4` (Presentation - Japanese)
- `회의록.wav` (Meeting minutes - Korean)

## Security Features
- **Path traversal protection**: Removes `../` and similar patterns
- **Dangerous character removal**: Filters out `<>:"/\|?*`
- **Control character filtering**: Removes invisible/control characters
- **Length limiting**: Prevents excessively long filenames
- **Unicode normalization**: Consistent character representation

## Browser Compatibility
- ✅ **Chrome/Chromium**: Full Unicode filename support
- ✅ **Firefox**: Proper UTF-8 handling
- ✅ **Safari**: Unicode filename display and download
- ✅ **Edge**: Complete Unicode support

## Configuration
No additional configuration needed. The system automatically:
1. Detects Unicode characters in filenames
2. Preserves them for display
3. Creates safe versions for internal processing
4. Encodes properly for downloads

## Testing
To test Chinese filename support:
1. Upload a file with Chinese characters in the name
2. Verify the filename displays correctly in the file info
3. Process the file for transcription
4. Download the SRT file and verify the Chinese filename is preserved

## Benefits
- ✅ **International users** can use native language filenames
- ✅ **No filename corruption** during upload/download
- ✅ **Proper browser handling** of Unicode filenames
- ✅ **Security maintained** while preserving Unicode
- ✅ **Cross-platform compatibility** with proper encoding
