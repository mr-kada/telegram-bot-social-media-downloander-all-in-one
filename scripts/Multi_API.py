import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


WEBSITE_URL = 'https://steptodown.com/'
API_URL = 'https://steptodown.com/wp-json/aio-dl/video-data/'


async def get_token_from_url(session):
    try:
        response = session.get(WEBSITE_URL)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            token_input = soup.find('input', {'id': 'token'})
            
            if token_input:
                token_value = token_input.get('value')
                return token_value
            else:return None
        else:return None
    except Exception as error:return None


async def download_file(session, download_url, unique_id, extension):
    file_name = f"{unique_id}.{extension}"
    print (file_name, download_url)

    try:
        with session.get(download_url, stream=True) as response:
            if response.status_code == 200:
                with open(file_name, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                return file_name
            else:
                # path = await download_with_selenium(download_url, file_name)
                return download_url
    except Exception as error: 
        return None


async def multi_download_video(video_url, unique_id):
    session = requests.Session()

    token = await get_token_from_url(session)

    # Form data to send in the POST request
    data = {
        'url': video_url,
        'token': token,
    }

    # Make the POST request
    response = session.post(API_URL, data=data, timeout=300)

    # Check the response
    if response.status_code == 200:
        try:
            data = response.json()
            download_url = data['medias'][-1]['url']
            extension = data['medias'][-1]['extension']
            # path = await download_file(session, download_url, unique_id, extension)
            return download_url

        except Exception as error:
            print ('data:', error)
            return None
    else:
        print ('response:', response.text)
        return None

