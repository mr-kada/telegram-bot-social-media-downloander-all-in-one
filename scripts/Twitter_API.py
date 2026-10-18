from scripts.paid_API import PaidAPI_Downloander


async def TwitterDownload(url, save_path):

    data = await PaidAPI_Downloander(url)

    if data == None:
        return None
    else:
        path = data.get("medias")[0].get("url")
        return path

    
