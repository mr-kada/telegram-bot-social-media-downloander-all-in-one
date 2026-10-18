from scripts.paid_API import PaidAPI_Downloander



async def download_pinterest_video(url, unique_id):

    data = await PaidAPI_Downloander(url)

    if data == None:
        return None
    else:
        path = data.get("medias")[0].get("url")
        return path


    # ydl_opts = {
    #     'format': 'bestvideo+bestaudio/best',  # This will download the best available format
    #     'outtmpl': f'{unique_id}.%(ext)s',
    #     'merge_output_format': 'mp4',  # Ensure video is downloaded as mp4
    #     'noplaylist': True,
    # }

    # try:
    #     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    #         ydl.download([url])
    #     return f'{unique_id}.mp4'
    # except Exception as error:return None
