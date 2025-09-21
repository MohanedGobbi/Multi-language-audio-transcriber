import whisper
import os
import sys
import subprocess
import glob
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path
import time

class TranscriberGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Language Audio Transcriber")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Variables
        self.whisper_model = None
        self.current_model_name = None
        self.is_transcribing = False
        self.start_time = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Multi-Language Audio/Video Transcriber", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Input method selection
        input_frame = ttk.LabelFrame(main_frame, text="Choose Input Method", padding="15")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        input_frame.columnconfigure(1, weight=1)
        
        self.input_method = tk.StringVar(value="youtube")
        
        # YouTube URL option
        ttk.Radiobutton(input_frame, text="YouTube URL", variable=self.input_method, 
                       value="youtube", command=self.on_input_method_change).grid(
                       row=0, column=0, sticky=tk.W, pady=8)
        
        self.url_entry = ttk.Entry(input_frame, width=50)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=8)
        self.url_entry.insert(0, "Paste YouTube URL here...")
        self.url_entry.bind("<FocusIn>", self.clear_url_placeholder)
        self.url_entry.bind("<FocusOut>", self.restore_url_placeholder)
        
        # Local file option
        ttk.Radiobutton(input_frame, text="Local File (MP3/MP4/etc)", variable=self.input_method, 
                       value="file", command=self.on_input_method_change).grid(
                       row=1, column=0, sticky=tk.W, pady=8)
        
        file_frame = ttk.Frame(input_frame)
        file_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=8)
        file_frame.columnconfigure(0, weight=1)
        
        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path, state="disabled")
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.browse_button = ttk.Button(file_frame, text="Browse", command=self.browse_file, state="disabled")
        self.browse_button.grid(row=0, column=1, padx=(5, 0))
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Transcription Settings", padding="15")
        settings_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)
        
        # Language selection
        ttk.Label(settings_frame, text="Language:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.language_var = tk.StringVar(value="auto")
        language_values = [
            ("Auto-detect", "auto"),
            ("Arabic", "ar"),
            ("English", "en"),
            ("Spanish", "es"),
            ("French", "fr"),
            ("German", "de"),
            ("Italian", "it"),
            ("Portuguese", "pt"),
            ("Russian", "ru"),
            ("Chinese", "zh"),
            ("Japanese", "ja"),
            ("Korean", "ko"),
            ("Turkish", "tr"),
            ("Hindi", "hi"),
            ("Dutch", "nl"),
            ("Polish", "pl")
        ]
        
        self.language_combo = ttk.Combobox(settings_frame, textvariable=self.language_var, 
                                          values=[f"{name} ({code})" for name, code in language_values], 
                                          state="readonly", width=20)
        self.language_combo.grid(row=0, column=1, sticky=(tk.W), padx=(0, 20))
        self.language_combo.set("Auto-detect (auto)")
        
        # Model selection
        ttk.Label(settings_frame, text="Model:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        
        self.model_var = tk.StringVar(value="base")
        model_values = [
            ("Tiny (fastest)", "tiny"),
            ("Base (recommended)", "base"), 
            ("Small (better quality)", "small"),
            ("Medium (high quality)", "medium"),
            ("Large (best quality)", "large")
        ]
        
        self.model_combo = ttk.Combobox(settings_frame, textvariable=self.model_var,
                                       values=[f"{name}" for name, code in model_values],
                                       state="readonly", width=25)
        self.model_combo.grid(row=0, column=3, sticky=(tk.W))
        self.model_combo.set("Base (recommended)")
        
        # Additional options
        options_frame = ttk.Frame(settings_frame)
        options_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.translate_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Translate to English", 
                       variable=self.translate_var).grid(row=0, column=0, sticky=tk.W, padx=(0, 20))
        
        self.timestamps_var = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Include timestamps", 
                       variable=self.timestamps_var).grid(row=0, column=1, sticky=tk.W)
        
        # Transcribe button
        self.transcribe_button = ttk.Button(main_frame, text="Start Transcription", 
                                           command=self.start_transcription, style="Accent.TButton")
        self.transcribe_button.grid(row=3, column=0, pady=(0, 15))
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Status and timer frame
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="Ready to transcribe", font=("Arial", 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.timer_label = ttk.Label(status_frame, text="", font=("Arial", 10))
        self.timer_label.grid(row=0, column=1, sticky=tk.E)
        
        # Output text area
        output_frame = ttk.LabelFrame(main_frame, text="Transcription Output", padding="10")
        output_frame.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, height=10, wrap=tk.WORD, font=("Consolas", 10))
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=7, column=0, pady=(0, 5))
        
        self.save_button = ttk.Button(buttons_frame, text="Save Transcript", 
                                     command=self.save_transcript, state="disabled")
        self.save_button.grid(row=0, column=0, padx=(0, 10))
        
        self.copy_button = ttk.Button(buttons_frame, text="Copy to Clipboard", 
                                     command=self.copy_transcript, state="disabled")
        self.copy_button.grid(row=0, column=1)
        
    def on_input_method_change(self):
        if self.input_method.get() == "youtube":
            self.url_entry.config(state="normal")
            self.file_entry.config(state="disabled")
            self.browse_button.config(state="disabled")
        else:
            self.url_entry.config(state="disabled")
            self.file_entry.config(state="normal")
            self.browse_button.config(state="normal")
    
    def clear_url_placeholder(self, event):
        if self.url_entry.get() == "Paste YouTube URL here...":
            self.url_entry.delete(0, tk.END)
    
    def restore_url_placeholder(self, event):
        if not self.url_entry.get():
            self.url_entry.insert(0, "Paste YouTube URL here...")
    
    def browse_file(self):
        file_types = [
            ("All supported", "*.mp3 *.mp4 *.wav *.m4a *.flac *.ogg *.webm *.mkv *.avi *.mov *.wmv"),
            ("Audio files", "*.mp3 *.wav *.m4a *.flac *.ogg *.aac"),
            ("Video files", "*.mp4 *.webm *.mkv *.avi *.mov *.wmv *.flv"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Select Audio/Video File",
            filetypes=file_types
        )
        
        if filename:
            normalized_path = os.path.normpath(filename)
            if os.path.exists(normalized_path) and os.path.isfile(normalized_path):
                self.file_path.set(normalized_path)
            else:
                messagebox.showerror("Error", f"Selected file is not accessible:\n{normalized_path}")
                self.file_path.set("")
    
    def get_language_code(self):
        selection = self.language_var.get()
        if "auto" in selection:
            return None  # Let Whisper auto-detect
        # Extract language code from selection like "Arabic (ar)"
        return selection.split("(")[-1].strip(")")
    
    def get_model_code(self):
        selection = self.model_var.get()
        model_mapping = {
            "Tiny (fastest)": "tiny",
            "Base (recommended)": "base",
            "Small (better quality)": "small", 
            "Medium (high quality)": "medium",
            "Large (best quality)": "large"
        }
        return model_mapping.get(selection, "base")
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def update_timer(self):
        if self.start_time and self.is_transcribing:
            elapsed = time.time() - self.start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.timer_label.config(text=f"Time: {minutes:02d}:{seconds:02d}")
            self.root.after(1000, self.update_timer)
        else:
            self.timer_label.config(text="")
    
    def download_audio(self, youtube_url, output_path="downloads"):
        """Download audio from YouTube using yt-dlp"""
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Create a safer filename template
        output_template = os.path.join(output_path, "%(title).100s.%(ext)s")
        cmd = [
            "yt-dlp",
            "-f", "bestaudio/best",
            "--extract-audio",
            "--audio-format", "mp3",
            "-o", output_template,
            "--no-playlist",
            youtube_url,
        ]

        self.update_status("Downloading audio from YouTube...")
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            # Find the downloaded MP3 file
            mp3_files = glob.glob(os.path.join(output_path, "*.mp3"))
            if mp3_files:
                audio_file = max(mp3_files, key=os.path.getctime)  # Get newest file
                title = os.path.splitext(os.path.basename(audio_file))[0]
                return audio_file, title
            else:
                raise FileNotFoundError("Download failed, no MP3 file found.")
                
        except subprocess.CalledProcessError as e:
            error_output = e.stderr.decode() if e.stderr else str(e)
            raise Exception(f"yt-dlp error: {error_output}")
    
    def transcribe_audio(self, file_path, model_size="base", language=None):
        """Transcribe audio file using Whisper - simplified approach"""
        self.update_status(f"Loading Whisper model '{model_size}'...")
        
        # Load model if needed
        if self.whisper_model is None or self.current_model_name != model_size:
            try:
                self.whisper_model = whisper.load_model(model_size)
                self.current_model_name = model_size
                self.update_status(f"Model '{model_size}' loaded successfully")
            except Exception as e:
                raise Exception(f"Failed to load model: {str(e)}")
        
        self.update_status("Transcribing audio... Please wait.")
        
        try:
            # Simple transcription with minimal options for reliability
            transcribe_options = {
                "verbose": False,
                "task": "translate" if self.translate_var.get() else "transcribe",
            }
            
            # Only set language if not auto-detect
            if language:
                transcribe_options["language"] = language
            
            result = self.whisper_model.transcribe(file_path, **transcribe_options)
            
            if self.timestamps_var.get():
                # Format with timestamps
                formatted_text = ""
                if "segments" in result:
                    for segment in result["segments"]:
                        start = segment.get("start", 0)
                        end = segment.get("end", 0)
                        text = segment.get("text", "").strip()
                        start_time = f"{int(start//60):02d}:{int(start%60):02d}"
                        end_time = f"{int(end//60):02d}:{int(end%60):02d}"
                        formatted_text += f"[{start_time} - {end_time}] {text}\n"
                    return formatted_text if formatted_text else result["text"]
                else:
                    return result["text"]
            else:
                return result["text"]
                
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def start_transcription(self):
        if self.is_transcribing:
            return
        
        # Validate input
        if self.input_method.get() == "youtube":
            url = self.url_entry.get().strip()
            if not url or url == "Paste YouTube URL here...":
                messagebox.showerror("Error", "Please enter a YouTube URL")
                return
            if not ("youtube.com" in url or "youtu.be" in url or "youtube" in url):
                messagebox.showerror("Error", "Please enter a valid YouTube URL")
                return
        else:
            file_path = self.file_path.get().strip()
            if not file_path:
                messagebox.showerror("Error", "Please select an audio/video file")
                return
            if not os.path.exists(file_path):
                messagebox.showerror("Error", f"File not found: {file_path}")
                return
            if not os.path.isfile(file_path):
                messagebox.showerror("Error", f"Selected path is not a file: {file_path}")
                return
        
        # Start transcription
        self.is_transcribing = True
        self.start_time = time.time()
        self.transcribe_button.config(state="disabled")
        self.progress.start(8)
        self.output_text.delete(1.0, tk.END)
        self.save_button.config(state="disabled")
        self.copy_button.config(state="disabled")
        self.update_timer()
        
        thread = threading.Thread(target=self.transcription_worker, daemon=True)
        thread.start()
    
    def transcription_worker(self):
        try:
            # Create output directory
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            audio_file = None
            title = "transcription"
            temp_file = False
            
            if self.input_method.get() == "youtube":
                url = self.url_entry.get().strip()
                audio_file, title = self.download_audio(url)
                temp_file = True
            else:
                audio_file = os.path.normpath(self.file_path.get().strip())
                title = Path(audio_file).stem
            
            # Get transcription settings
            model_size = self.get_model_code()
            language = self.get_language_code()
            
            # Transcribe
            transcript = self.transcribe_audio(audio_file, model_size, language)
            
            if not transcript.strip():
                raise Exception("Transcription returned empty result")
            
            # Save transcript
            safe_title = "".join(c if c.isalnum() or c in " _-.()" else "_" for c in title)[:100]
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_title}_{timestamp}_transcript.txt"
            self.output_file = os.path.join(output_dir, filename)
            
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(transcript)
            
            # Update UI in main thread
            self.root.after(0, lambda: self.transcription_complete(transcript, temp_file, audio_file))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.transcription_error(error_msg))
    
    def transcription_complete(self, transcript, temp_file, audio_file):
        self.progress.stop()
        self.is_transcribing = False
        self.transcribe_button.config(state="normal")
        self.save_button.config(state="normal")
        self.copy_button.config(state="normal")
        
        # Show final time
        if self.start_time:
            total_time = time.time() - self.start_time
            minutes = int(total_time // 60)
            seconds = int(total_time % 60)
            self.timer_label.config(text=f"Completed in {minutes:02d}:{seconds:02d}")
        
        # Display transcript
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, transcript)
        
        self.update_status(f"✅ Transcription complete! Saved to output folder")
        
        # Clean up temporary file
        if temp_file and audio_file and os.path.exists(audio_file):
            try:
                os.remove(audio_file)
            except:
                pass
        
        # Show success message
        word_count = len(transcript.split())
        messagebox.showinfo("Success", 
                           f"Transcription completed!\n\n"
                           f"Words: {word_count:,}\n"
                           f"Saved to: {os.path.basename(self.output_file)}")
    
    def transcription_error(self, error_msg):
        self.progress.stop()
        self.is_transcribing = False
        self.transcribe_button.config(state="normal")
        self.update_status("❌ Transcription failed")
        
        # Show error with helpful suggestions
        if "yt-dlp" in error_msg:
            error_msg += "\n\nTip: Make sure yt-dlp is installed: pip install yt-dlp"
        elif "model" in error_msg.lower():
            error_msg += "\n\nTip: Try a smaller model size if you're running out of memory"
        
        messagebox.showerror("Transcription Error", error_msg)
    
    def save_transcript(self):
        if not hasattr(self, 'output_file'):
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Transcript As",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"), 
                ("SRT subtitles", "*.srt"),
                ("All files", "*.*")
            ],
            initialname=os.path.basename(self.output_file)
        )
        
        if file_path:
            try:
                content = self.output_text.get(1.0, tk.END).strip()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Success", f"Transcript saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{e}")
    
    def copy_transcript(self):
        try:
            content = self.output_text.get(1.0, tk.END).strip()
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.update_status("✅ Transcript copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy text:\n{e}")

def main():
    # Check dependencies
    try:
        import whisper
    except ImportError:
        print("Error: whisper not installed. Run: pip install openai-whisper")
        sys.exit(1)
    
    # Create and setup the GUI
    root = tk.Tk()
    
    # Try to set a modern theme
    try:
        style = ttk.Style()
        available_themes = style.theme_names()
        if 'winnative' in available_themes:
            style.theme_use('winnative')
        elif 'clam' in available_themes:
            style.theme_use('clam')
    except:
        pass
    
    app = TranscriberGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Set minimum size
    root.minsize(600, 500)
    
    root.mainloop()

if __name__ == "__main__":
    main()