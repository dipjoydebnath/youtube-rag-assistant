import os
import re
import tempfile
import subprocess
import yt_dlp
import imageio_ffmpeg
from dotenv import load_dotenv
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Get absolute path to the bundled FFmpeg binary
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

def extract_video_id(url: str) -> str:
    pattern = r"(?:v=|\/|be\/|embed\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def split_and_compress_audio(input_path: str, output_dir: str, chunk_time_sec: int = 300) -> list:
    """
    Splits audio into 5-minute chunks and compresses them to lightweight 64k MP3s 
    to guarantee they stay well under Groq's 25MB limit.
    """
    output_pattern = os.path.join(output_dir, "chunk_%03d.mp3")
    
    cmd = [
        FFMPEG_EXE,
        "-i", input_path,
        "-f", "segment",
        "-segment_time", str(chunk_time_sec),
        "-ac", "1",           # Convert to Mono channel (smaller size)
        "-ar", "16000",       # 16kHz sample rate (perfect for speech)
        "-b:a", "64k",        # Compress audio bitrate to 64k
        "-y",
        output_pattern
    ]
    
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    chunks = sorted([
        os.path.join(output_dir, f) for f in os.listdir(output_dir) 
        if f.startswith("chunk_") and f.endswith(".mp3")
    ])
    return chunks

def transcribe_audio_with_whisper(url: str) -> str:
    """
    Downloads full audio with yt-dlp, splits & compresses using FFmpeg,
    and sends lightweight chunks to Groq Whisper.
    """
    print("[*] Downloading audio stream...")
    
    full_transcript = []

    with tempfile.TemporaryDirectory() as temp_dir:
        raw_audio_path = os.path.join(temp_dir, 'raw_audio.m4a')
        
        ydl_opts = {
            'format': 'm4a/bestaudio/best',
            'outtmpl': raw_audio_path,
            'ffmpeg_location': FFMPEG_EXE,
            'quiet': True,
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}}
        }
        
        # Download complete audio
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(raw_audio_path):
            return "Error: Could not download video audio."

        # Always split & compress to be 100% safe against 413 limits
        print("[*] Splitting & compressing audio with FFmpeg...")
        chunks_dir = os.path.join(temp_dir, "chunks")
        os.makedirs(chunks_dir, exist_ok=True)
        
        chunk_files = split_and_compress_audio(raw_audio_path, chunks_dir, chunk_time_sec=300)
        
        for idx, chunk_file in enumerate(chunk_files):
            print(f"[*] Transcribing compressed chunk {idx + 1}/{len(chunk_files)} with Groq Whisper...")
            with open(chunk_file, "rb") as file:
                translation = groq_client.audio.translations.create(
                    file=(os.path.basename(chunk_file), file.read()),
                    model="whisper-large-v3",
                    response_format="json"
                )
            full_transcript.append(translation.text)

    return " ".join(full_transcript)

def get_youtube_transcript(url: str) -> str:
    video_id = extract_video_id(url)
    if not video_id:
        return "Error: Invalid YouTube URL format."

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        target_languages = ['en', 'hi', 'bn']
        
        transcript = None
        for lang in target_languages:
            try:
                transcript = transcript_list.find_transcript([lang])
                break
            except Exception:
                continue
        
        if not transcript:
            try:
                transcript = transcript_list.find_generated_transcript(target_languages)
            except Exception:
                pass

        if transcript:
            if transcript.language_code in ['hi', 'bn']:
                transcript = transcript.translate('en')
            fetched_data = transcript.fetch()
            return " ".join([item['text'] for item in fetched_data])

    except Exception:
        pass

    return transcribe_audio_with_whisper(url)