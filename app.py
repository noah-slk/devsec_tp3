import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# INTENTIONAL VULNERABILITY #3: Hardcoded secret key
# DO NOT use hardcoded secrets in production!
# Correct approach: Read from environment variable or secret manager
SECRET_KEY = os.getenv('SECRET_KEY')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
# Note: Max upload size is not restricted (another potential issue)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit


@app.route('/')
def index():
    """Serve the main meme generator page."""
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'memeforge'})


@app.route('/upload', methods=['POST'])
def upload():
    """
    File upload endpoint - INTENTIONAL VULNERABILITY #2
    
    This endpoint accepts file uploads without:
    - File extension validation
    - MIME type validation
    - Content-type verification
    - File content scanning
    
    Students should add proper validation before processing uploads.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Read file into memory - do not save to disk
        file_content = file.read()
        file_size = len(file_content)
        
        # Get MIME type from request (can be spoofed - part of the vulnerability)
        content_type = file.content_type or 'unknown'
        
        # Extract file extension from filename (can be spoofed - part of the vulnerability)
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'no extension'
        
        # Return metadata about the file
        # NOTE: We do NOT validate the file content or save it to disk or database
        # This demonstrates the vulnerability: accepting files without proper validation
        return jsonify({
            'success': True,
            'filename': file.filename,
            'content_type': content_type,
            'extension': file_ext,
            'size_bytes': file_size,
            'message': 'File received (not validated or saved)'
        })
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500


# INTENTIONAL VULNERABILITY #4: Debug mode enabled
# DO NOT run with debug=True in production!
# Correct approach: Use environment variable and run under WSGI server (Gunicorn)
if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    app.run(debug=debug, host=host, port=port)

