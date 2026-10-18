import yt_dlp 
import os
from moviepy.editor import VideoFileClip



async def get_video_length_and_size(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    
    # Get video duration
    try:
        clip = VideoFileClip(file_path)
        duration_seconds = clip.duration  # Duration in seconds
        clip.close()

        # Ensure duration_seconds is an integer
        duration_seconds = int(duration_seconds)

        # Convert seconds to HH:MM:SS format
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        seconds = duration_seconds % 60
        duration = f"{hours:02}:{minutes:02}:{seconds:02}"

    except Exception as e:
        duration = 'غير متاح'
    
    # Get video size
    try:
        size = os.path.getsize(file_path)  # Size in bytes
    except Exception as e:
        size = 'غير متاح'
    
    # Convert size to human-readable format
    try:
        size_in_mb = size / (1024 * 1024)
        size_in_mb = round(size_in_mb, 2)
    except:size_in_mb = 'غير متاح'
    
    return {
        "duration_seconds": duration,
        "size_bytes": size,
        "size_mb": size_in_mb
    }



async def youtube_download_best_quality_video_1080p(url, unique_id):
    ydl_opts = {
        'format': '(bestvideo[height<=1080]+bestaudio/best[height<=1080])',
        'outtmpl': f'{unique_id}.%(ext)s',
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'noplaylist': True,
        'proxy': 'socks5://127.0.0.1:9050',
    }

    try:
        # Download the video with yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        return f'{unique_id}.mp4'
    except Exception as error:return None




async def youtube_download_up_to_720p(url, unique_id):
    ydl_opts = {
        'format': '(bestvideo[height<=720]+bestaudio/best[height<=720])/bestvideo[height<=480]+bestaudio/best[height<=480]/best',
        'outtmpl': f'{unique_id}_720p.%(ext)s',
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'noplaylist': True,
        'add_header': ['User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)'],
        'proxy': 'socks5://127.0.0.1:9050',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return f'{unique_id}_720p.mp4'
    except Exception as error:
        return None



async def youtube_download_up_to_480p(url, unique_id):
    ydl_opts = {
        'format': '(bestvideo[height<=480]+bestaudio/best[height<=480])',
        'outtmpl': f'{unique_id}_480p.%(ext)s',
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'noplaylist': True,
        'add_header': ['User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)'],
        'proxy': 'socks5://127.0.0.1:9050',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return f'{unique_id}_480p.mp4'
    except Exception as error:return None

