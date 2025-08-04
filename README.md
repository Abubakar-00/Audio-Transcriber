# Audio Transcriber 🎵➡️📝

A powerful web-based audio transcription tool that leverages Groq's Whisper API to convert audio files into text with support for multiple languages and export formats.

![Preview](<img width="1453" height="681" alt="image" src="https://github.com/user-attachments/assets/5bd0ddd5-0dc5-46a5-868d-4187fdbb750e" />
)

## ✨ Features

- **🎯 Batch Audio Processing**: Upload and transcribe multiple audio files simultaneously
- **🌍 Multi-language Support**: Supports Urdu, English, and other languages via Groq's Whisper models  
- **📁 Directory Upload (Including Kaldi Method)**: Upload entire folders of audio files with webkitdirectory support
- **📊 Multiple Export Formats**: 
  - Excel (.xlsx) with structured data
  - JSON for programmatic use
  - TXT OR Kaldi with speaker identification
- **🎨 Clean UI**: Simple, responsive interface built with HTML and Tailwind CSS
- **🔒 Secure File Handling**: Automatic cleanup of uploaded files
- **⚡ Real-time Processing**: Live transcription status updates and can edit transcription before saving
- **🐳 Docker Ready**: Containerized for easy deployment

## 🚀 Quick Start with Docker

### Using Docker Hub Image

```bash
# With environment file
docker run -p 8000:8000 --env-file .env abubakar00/audio-transcriber:latest

# With inline environment variable
docker run -p 8000:8000 -e GROQ_API_KEY=your_real_key_here abubakar00/audio-transcriber:latest
```

Then open your browser and navigate to `http://localhost:8000`

## 🛠️ Local Development Setup

### Prerequisites

- Python 3.8+
- Groq API Key ([Get one here](https://console.groq.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Abubakar-00/Audio-Transcriber.git
   cd Audio-Transcriber
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   echo "GROQ_API_KEY=your_groq_api_key_here" > .env
   ```

4. **Run the application**
   ```bash
   python server.py
   ```

5. **Access the application**
   Open `http://localhost:8000` in your browser

## 🐳 Docker Development

### Build and Run Locally

```bash
# Build the image
docker build -t audio-transcriber .

# Run with environment file
docker run -p 8000:8000 --env-file .env audio-transcriber

# Or run with inline environment variable
docker run -p 8000:8000 -e GROQ_API_KEY=your_key_here audio-transcriber
```

## 📋 Usage

1. **Upload Audio Files**: 
   - Click "Choose Files" to select individual audio files
   - Or click "Upload Folder" to upload an entire directory of audio files

2. **Configure Settings**:
   - Select transcription model (default: whisper-large-v3)
   - Choose language (default: Urdu)

3. **Transcribe**: Click "Transcribe All" to process your audio files

4. **Export Results**:
   - **Excel**: Structured spreadsheet with filename and transcription columns
   - **JSON**: Machine-readable format for further processing
   - **TXT**: Tab-separated format with speaker identification

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Your Groq API key for Whisper access | ✅ Yes |
| `PORT` | Server port (default: 8000) | ❌ No |

### Supported Audio Formats

- MP3, WAV, M4A, FLAC, OGG
- Maximum file size depends on Groq API limits

## 🏗️ Architecture

```
Audio Transcriber
├── server.py          # Main HTTP server with transcription logic
├── index.html         # Frontend UI with Tailwind CSS
├── Dockerfile         # Container configuration
├── requirements.txt   # Python dependencies
└── tests/
    └── test_server.py # Unit tests
```

## 🔄 CI/CD Pipeline

This project features a robust **CI/CD pipeline** using GitHub Actions:

- **Automated Testing**: Runs unit tests on every push and pull request
- **Code Quality**: Linting with flake8 for consistent code style
- **Docker Integration**: Automated container builds and deployments

See `.github/workflows/ci.yml` for the complete pipeline configuration.

## 🧪 Testing

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=.

# Lint code
flake8 .
```

## 📁 Project Structure

```
.
├── .github/workflows/
│   └── ci.yml              # CI/CD pipeline configuration
├── tests/
│   └── test_server.py      # Unit tests
├── .flake8                 # Linting configuration
├── audio_transcriber.py    # CLI older Version
├── Dockerfile              # Docker container setup
├── index.html              # Web interface
├── requirements-dev.txt    # Development dependencies
├── requirements.txt        # Production dependencies
├── server.py              # Main HTTP server
└── README.md              # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Groq](https://groq.com/) for providing the Whisper API
- [Tailwind CSS](https://tailwindcss.com/) for the beautiful UI components
- OpenAI for the original Whisper model
