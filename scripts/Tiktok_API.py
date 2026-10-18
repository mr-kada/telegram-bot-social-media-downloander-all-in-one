from scripts.paid_API import PaidAPI_Downloander



async def download_tiktok_video(url, unique_id):

    data = await PaidAPI_Downloander(url)

    if data == None:
        return None
    else:
        paths = []
        for video in data.get("medias"):
            paths.append(video.get("url"))
        
        return paths


    # ydl_opts = {
    #     'format': 'bestvideo+bestaudio/best',
    #     'outtmpl': f'{unique_id}.%(ext)s',
    #     'merge_output_format': 'mp4',
    #     'noplaylist': True,
    # }

    # try:
    #     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    #         ydl.download([url])
    #     return f'{unique_id}.mp4'
    # except Exception as error:return None
