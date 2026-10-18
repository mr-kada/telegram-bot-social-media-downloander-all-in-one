import requests, re, os


JACO_URL = "https://jaco.live"
API_URL = "https://api.jaco.live/live/2/live_play/c/get.json?id="



async def download_file(session, download_url, unique_id, extension):
    file_name = f"{unique_id}{extension}"
    try:
        with session.get(download_url, stream=True) as response:
            if response.status_code == 200:
                with open(file_name, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                return file_name
            else:
                return None
    except Exception as error:
        return None


async def download_jaco_video(video_url, unique_id):
    session = requests.Session()
    open_url = session.get(video_url)
    match = re.search(r"rid=(\d+)", open_url.url)

    if match:
        rid = match.group(1)
        get_website = session.get(JACO_URL)
        get_video = session.get(f'{API_URL}{rid}', headers=get_website.cookies)

        try:
            data = get_video.json()
            download_url = data['data']['content']['video_info']['media']['play_info']['details'][0]['url']
            extension = os.path.splitext(download_url)[-1]
            path = await download_file(session, download_url, unique_id, extension)
            return path
        except Exception as error:
            print ('JACO:', error)
            return None
    else:
        return None



# download_jaco_video("https://jaco.live/@RiyadhSeason?rid=23118744050261782&vid=1203139179937", "hhhhhhhhh")