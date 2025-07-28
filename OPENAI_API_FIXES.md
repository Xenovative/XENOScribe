# XENOScribe OpenAI API Error Fixes

## Problem
OpenAI Whisper API was returning 400 "Bad Request" errors with the message "something went wrong reading your request" when processing certain files.

## Root Causes Identified
1. **Improper file handling**: Files weren't being sent with proper MIME types
2. **Missing file size validation**: Files exceeding OpenAI's 25MB limit
3. **Invalid filenames**: Files with problematic characters or extensions
4. **No fallback mechanism**: When OpenAI API failed, the entire transcription failed

## Solutions Implemented

### 1. Enhanced OpenAI API Function
- **File size validation**: Check against OpenAI's 25MB limit
- **Proper MIME types**: Send files with correct content-type headers
- **File tuple format**: Use proper (filename, file_object, mime_type) format
- **Better error handling**: Detailed logging of API errors

### 2. Automatic Fallback System
- **Smart fallback**: When OpenAI API fails, automatically switch to local Whisper
- **Seamless transition**: Users don't need to retry manually
- **Logging**: Clear indication when fallback occurs

### 3. Comprehensive File Validation
- **Filename validation**: Ensure secure, valid filenames
- **Extension checking**: Verify files have proper extensions
- **Empty file detection**: Reject zero-byte files
- **File integrity**: Verify files are saved correctly

### 4. Improved Error Messages
- **Specific error codes**: Different HTTP status codes for different issues
- **User-friendly messages**: Clear explanations of what went wrong
- **Detailed logging**: Server-side logging for debugging

## Technical Details

### OpenAI API File Format
```python
# Before (problematic)
file=audio_file

# After (correct)
file=(filename, audio_file, mime_type)
```

### File Size Limits
- **OpenAI API**: 25MB maximum
- **Local Whisper**: Limited by available system memory
- **Automatic routing**: Large files use local Whisper

### Supported File Types
- Audio: mp3, wav, m4a, aac, ogg
- Video: mp4, avi, mov, mkv, webm, flv

### Error Handling Flow
1. **File validation** → Reject invalid files immediately
2. **OpenAI API attempt** → Try OpenAI first if configured
3. **Automatic fallback** → Switch to local Whisper on API failure
4. **User notification** → Clear error messages if all methods fail

## Configuration
Set these environment variables for optimal performance:

```bash
# Use OpenAI API for files under 25MB
USE_OPENAI_API=true
OPENAI_API_KEY=your-api-key

# Fallback to local Whisper model
WHISPER_MODEL=base  # or small, medium, large
```

## Monitoring
Check logs for API performance:
```bash
sudo journalctl -u xenoscribe -f | grep -E "(OpenAI|API|fallback)"
```

Look for:
- OpenAI API success/failure rates
- Fallback activations
- File validation rejections
- Processing time comparisons

## Benefits
- ✅ **Reliability**: Automatic fallback ensures transcription always works
- ✅ **Performance**: OpenAI API for small files, local for large files
- ✅ **User Experience**: No manual retries needed
- ✅ **Cost Optimization**: Reduces API calls for problematic files
- ✅ **Better Debugging**: Detailed error logging
