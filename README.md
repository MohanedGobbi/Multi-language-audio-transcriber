🎙️ Multi-Language Audio Transcriber
A powerful, user-friendly desktop application for transcribing audio and video files using OpenAI's Whisper model. Support for 16+ languages with offline transcription capabilities.

✨ Features

🌍 Multi-Language Support: 16+ languages including Arabic, English, Spanish, French, German, and more
🔄 Auto-Detection: Automatically detects the audio language
🎥 Multiple Input Sources:

YouTube URLs (automatically downloads audio)
Local audio files (MP3, WAV, M4A, FLAC, OGG, AAC)
Local video files (MP4, WebM, MKV, AVI, MOV, WMV)


🔒 Fully Offline: No data sent to external servers after initial model download
⚡ Multiple Model Sizes: Choose between speed and accuracy
📝 Flexible Output: Plain text or timestamped transcriptions
🌐 Translation: Option to translate any language to English
💾 Export Options: Save as TXT or SRT subtitle files
📋 Copy to Clipboard: Easy sharing and editing
⏱️ Real-time Timer: Track transcription progress
🎨 Modern GUI: Clean, intuitive interface

🚀 Quick Start
Prerequisites

Python 3.8 or higher
FFmpeg (required for audio processing)

Installation

Clone the repository:

bash   git clone https://github.com/yourusername/multi-language-transcriber.git
   cd multi-language-transcriber

Install Python dependencies:

bash   pip install -r requirements.txt

Install FFmpeg:

Windows: Download from FFmpeg.org or use winget install ffmpeg
macOS: brew install ffmpeg
Linux: sudo apt install ffmpeg (Ubuntu/Debian) or equivalent for your distro


Run the application:

bash   python main.py
📖 Usage
Transcribing YouTube Videos

Select "YouTube URL" option
Paste the YouTube video URL
Choose your preferred language and model
Click "Start Transcription"

Transcribing Local Files

Select "Local File" option
Click "Browse" to select your audio/video file
Configure settings as needed
Click "Start Transcription"

Settings Explained
Language Options:

Auto-detect: Let Whisper automatically identify the language (recommended)
Specific Language: Choose from 16+ supported languages for better accuracy

Model Sizes:

Tiny: Fastest, lower accuracy (~39 MB)
Base: Good balance of speed and accuracy (~74 MB) - Recommended
Small: Better accuracy, slower (~244 MB)
Medium: High accuracy (~769 MB)
Large: Best accuracy, slowest (~1550 MB)

Additional Options:

Translate to English: Convert any language transcription to English
Include timestamps: Add time markers to each text segment

🌐 Supported Languages
Arabic, English, Spanish, French, German, Italian, Portuguese, Russian, Chinese, Japanese, Korean, Turkish, Hindi, Dutch, Polish, and more through auto-detection.
📁 Output
Transcriptions are automatically saved to the output/ folder with timestamped filenames:

Format: filename_YYYYMMDD_HHMMSS_transcript.txt
Encoding: UTF-8 (supports all languages and special characters)

⚙️ Technical Details

Engine: OpenAI Whisper (latest version)
GUI Framework: tkinter (built-in with Python)
YouTube Support: yt-dlp (most reliable YouTube downloader)
Audio Processing: FFmpeg
Threading: Non-blocking UI during transcription

🔧 Troubleshooting
Common Issues
"yt-dlp not found" error:
bashpip install yt-dlp
"FFmpeg not found" error:

Ensure FFmpeg is installed and accessible from command line
Try running ffmpeg -version to verify installation

Out of memory errors:

Use a smaller model (Tiny or Base)
Close other applications to free up RAM
For very long audio files, consider splitting them first

Poor transcription quality:

Try a larger model (Medium or Large)
Ensure audio quality is good (clear speech, minimal background noise)
Select the specific language instead of auto-detect

Performance Tips

First run: Models are downloaded automatically (internet required)
CPU vs GPU: Currently CPU-optimized; GPU support may be added in future versions
Large files: Processing time varies based on audio length and model size
Memory usage: Larger models require more RAM (Large model needs ~4GB)

🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.
Development Setup

Fork the repository
Create your feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request

📜 License
This project is licensed under the MIT License - see the LICENSE file for details.
🙏 Acknowledgments

OpenAI for the incredible Whisper model
yt-dlp developers for the robust YouTube downloading capability
FFmpeg team for audio/video processing tools
Python tkinter for the GUI framework

📞 Support
If you encounter any issues or have questions:

Check the Issues page
Create a new issue with detailed description
Include your OS, Python version, and error messages


⭐ Star this repository if you found it helpful!
📊 Stats

Model Downloads: Automatic on first use
Offline Capable: Yes (after initial setup)
Languages Supported: 16+ with auto-detection
File Formats: All common audio/video formats
Platform Support: Windows, macOS, Linux
