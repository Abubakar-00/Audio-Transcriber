import http.server
import socketserver
import urllib.parse
import os
import json
import cgi # For parsing multipart/form-data
import shutil # For creating and deleting directories
import mimetypes # To guess MIME type for serving audio
from groq import Groq
from dotenv import load_dotenv
import datetime
import xlsxwriter

# Load environment variables
load_dotenv()
client = Groq()

PORT = 8000
UPLOAD_DIR = 'uploaded_audios' # Directory to save uploaded files

class MyHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())
        elif self.path.startswith('/serve_audio'):
            # Extract the actual file path from the query parameter
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            file_path = query_components.get('path', [None])[0]

            if file_path and os.path.exists(file_path):
                try:
                    mime_type, _ = mimetypes.guess_type(file_path)
                    if mime_type is None:
                        mime_type = 'application/octet-stream' # Default if type cannot be guessed

                    self.send_response(200)
                    self.send_header('Content-type', mime_type)
                    self.end_headers()
                    with open(file_path, 'rb') as file:
                        self.wfile.write(file.read())
                except Exception as e:
                    self.send_error(500, f"Error serving audio: {str(e)}")
            else:
                self.send_error(404, "Audio file not found or path missing.")
        else:
            super().do_GET() # Serve other static files

    def do_POST(self):
        if self.path == '/upload_audios':
            self.handle_upload_audios()
        elif self.path == '/transcribe':
            self.handle_transcribe()
        elif self.path == '/save_excel':
            self.handle_save_excel()
        elif self.path == '/save_json':
            self.handle_save_json()
        elif self.path == '/save_txt':
            self.handle_save_txt()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_upload_audios(self):
        # Ensure the upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Parse the multipart/form-data
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.headers['Content-Type'],
                     })

        uploaded_files_info = []
        
        # Iterate over all parts of the form data
        if 'audioFiles' in form:
            # If multiple files are uploaded under the same name (e.g., from webkitdirectory)
            if isinstance(form['audioFiles'], list):
                files_to_process = form['audioFiles']
            else:
                files_to_process = [form['audioFiles']] # Single file case

            for field_item in files_to_process:
                if field_item.filename:
                    # Get the original relative path from the client (if available)
                    # For webkitdirectory, field_item.filename can contain the relative path
                    original_filename = field_item.filename
                    
                    # Create a unique path for the uploaded file within UPLOAD_DIR
                    # This handles potential subfolders from webkitdirectory
                    safe_filename = os.path.normpath(original_filename).replace('../', '') # Sanitize path
                    
                    # Construct the full path where the file will be saved
                    save_path = os.path.join(UPLOAD_DIR, safe_filename)
                    
                    # Ensure the directory structure for the file exists
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)

                    try:
                        with open(save_path, 'wb') as f:
                            f.write(field_item.file.read())
                        
                        # Store info about the uploaded file
                        uploaded_files_info.append({
                            "name": os.path.basename(original_filename), # Original filename for ID
                            "display_name": original_filename, # Full relative path for display
                            "path": save_path # Absolute path on server for processing
                        })
                    except Exception as e:
                        print(f"Error saving uploaded file {original_filename}: {e}")
                        # Optionally send an error response or skip this file

        response_data = {"audios": uploaded_files_info}
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_data).encode())

    def handle_transcribe(self):
        content_length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(content_length).decode('utf-8'))
        audios = data['audios'] # These are the paths on the server
        model = data.get('model', 'whisper-large-v3')
        language = data.get('language', 'ur')

        response = {"transcriptions": []}
        for file_path in audios:
            if not os.path.exists(file_path):
                print(f"File not found for transcription: {file_path}")
                response["transcriptions"].append({
                    "name": os.path.basename(file_path),
                    "transcription": f"Error: File not found on server."
                })
                continue

            try:
                with open(file_path, "rb") as file:
                    transcription = client.audio.transcriptions.create(
                        file=(os.path.basename(file_path), file.read()), # Pass filename and content
                        model=model,
                        language=language,
                        temperature=0.0
                    )
                    response["transcriptions"].append({
                        "name": os.path.basename(file_path),
                        "transcription": transcription.text
                    })
            except Exception as e:
                print(f"Error transcribing {file_path}: {e}")
                response["transcriptions"].append({
                    "name": os.path.basename(file_path),
                    "transcription": f"Error: {str(e)}"
                })

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
   
    def handle_save_excel(self):
        content_length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(content_length).decode('utf-8'))
        transcriptions = data['transcriptions']
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcriptions_{timestamp}.xlsx"
            
            # Create an Excel workbook and add a worksheet
            workbook = xlsxwriter.Workbook(filename)
            worksheet = workbook.add_worksheet()
            
            # Add header
            worksheet.write(0, 0, 'File Name')
            worksheet.write(0, 1, 'Transcription')
            
            # Add data
            for row_num, item in enumerate(transcriptions, start=1):
                worksheet.write(row_num, 0, item['name'])
                worksheet.write(row_num, 1, item['transcription'])
            
            workbook.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Transcriptions saved as {filename}".encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error saving Excel: {str(e)}".encode())

    def handle_save_json(self):
        content_length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(content_length).decode('utf-8'))
        transcriptions = data['transcriptions']
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcriptions_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(transcriptions, jsonfile, ensure_ascii=False, indent=4)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Transcriptions saved as {filename}".encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error saving JSON: {str(e)}".encode())

    def handle_save_txt(self):
        content_length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(content_length).decode('utf-8'))
        transcriptions = data['transcriptions']
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transcriptions_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as txtfile:
                for item in transcriptions:
                    # Extract speaker name (assuming format like "Arslan1", "Fatima6", etc.)
                    # This logic might need refinement based on actual speaker naming conventions
                    speaker = ''.join([c for c in item['name'] if not c.isdigit() and c != '/']) # Exclude path separators
                    if not speaker: # Fallback if no speaker name can be extracted
                        speaker = "UnknownSpeaker"
                    # Write in the format: SpeakerName Transcription
                    txtfile.write(f"{speaker}\t{item['transcription']}\n")
            
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Transcriptions saved as {filename}".encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error saving text file: {str(e)}".encode())

# Set up and start the server
if __name__ == "__main__":
    # Clean up previous uploads directory if it exists
    if os.path.exists(UPLOAD_DIR):
        shutil.rmtree(UPLOAD_DIR)
    os.makedirs(UPLOAD_DIR, exist_ok=True) # Recreate it fresh

    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
            print("Server stopped.")
        finally:
            # Clean up the uploaded_audios directory on server shutdown
            if os.path.exists(UPLOAD_DIR):
                shutil.rmtree(UPLOAD_DIR)
            print(f"Cleaned up {UPLOAD_DIR} directory.")

