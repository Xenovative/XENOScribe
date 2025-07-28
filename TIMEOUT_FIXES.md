# XENOScribe Timeout Fixes for Long Audio Files

## Problem
Users experienced 500 errors when transcribing long audio files (>1 hour) due to timeout issues in various components.

## Solutions Implemented

### 1. Nginx Configuration Updates
- **Proxy timeouts extended to 1 hour**:
  - `proxy_send_timeout`: 300s → 3600s
  - `proxy_read_timeout`: 300s → 3600s
  - `send_timeout`: 300s → 3600s
- **Connection timeout optimized**: 60s (reasonable for initial connection)

### 2. Flask Application Enhancements
- **Added comprehensive logging**:
  - File size logging for better monitoring
  - Processing duration tracking
  - Start/end time logging
- **Enhanced error handling**:
  - Specific timeout error responses (504 status)
  - Memory error detection (413 status)
  - Better error messages for users
- **Timeout wrapper functions** (for future use):
  - Custom timeout decorator
  - Signal-based timeout handling

### 3. Systemd Service Configuration
- **Resource limits increased**:
  - `LimitNOFILE`: 65536 (file descriptors)
  - `LimitNPROC`: 4096 (processes)
- **Process management**:
  - `KillMode`: mixed (graceful shutdown)
  - `KillSignal`: SIGTERM
  - Proper timeout settings

### 4. Frontend Improvements
- **Smart progress indication**:
  - File size-based time estimation
  - Slower progress for large files
  - Warning messages for files >100MB
- **Better error handling**:
  - Network error detection
  - Timeout-specific messages
  - Warning vs error message styling
- **User feedback**:
  - Estimated processing time display
  - File size warnings
  - Clear error categorization

## Configuration Files Updated
1. `deploy/setup_server.sh` - Nginx and systemd configuration
2. `app.py` - Flask application timeout handling
3. `templates/index.html` - Frontend improvements

## Recommended Usage
- **Small files (<100MB)**: Normal processing
- **Large files (100MB-1GB)**: Warning displayed, extended processing time
- **Very large files (>1GB)**: May require server with more memory

## Monitoring
Check logs for transcription performance:
```bash
sudo journalctl -u xenoscribe -f
```

Look for:
- File size and processing duration
- Memory usage warnings
- Timeout errors

## Future Improvements
- Implement chunked processing for very large files
- Add progress streaming for real-time updates
- Consider background job processing for extremely long files
