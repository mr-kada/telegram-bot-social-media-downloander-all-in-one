from scripts.paid_API import PaidAPI_Downloander
import requests


async def facebook_download_best_quality_video(url, unique_id):


    data = await PaidAPI_Downloander(url)

    if data == None:
        return None
    else:
        path = data.get("medias")[0].get("url")
    
    session = requests.Session()
    path = await download_file(session, path, unique_id, "mp4")
    return path

    # ydl_opts = {
    #     'format': '(bestvideo[height<=1080]+bestaudio/best[height<=1080])',
    #     'outtmpl': f'{unique_id}.%(ext)s',
    #     'merge_output_format': 'mp4',
    #     'postprocessors': [{
    #         'key': 'FFmpegVideoConvertor',
    #         'preferedformat': 'mp4',
    #     }],
    #     'noplaylist': True,
    # }

    # try:
    #     # Download the video with yt-dlp
    #     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    #         ydl.download([url])
        
    #     return f'{unique_id}.mp4'
    # except Exception as error:return None



async def download_file(session, download_url, unique_id, extension):
    file_name = f"{unique_id}.{extension}"

    try:
        with session.get(download_url, stream=True) as response:
            if response.status_code == 200:
                with open(file_name, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                return file_name
            else:
                return download_url
    except Exception as error: 
        return None
