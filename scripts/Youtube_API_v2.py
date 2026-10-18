import requests






def download_video(session, headers, download_url, output_path):
    try:
        # Send GET request to the video download URL
        response = session.get(download_url, headers=headers, stream=True)

        # Check if the request was successful
        if response.status_code == 200:
            # Open the output file in write-binary mode
            with open(output_path, 'wb') as file:
                # Stream the content in chunks and write to the file
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            print(f"Video downloaded successfully and saved to {output_path}")
        else:
            print(f"Failed to download video. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")


def youtube_download_best_quality_video(url, unique_id):
    session = requests.Session()

    # Step 1: GET request to retrieve the CSRF token
    token_url = "https://y2meta.net/api/get-token"
    response = session.get(token_url)

    # Extract the CSRF token from the response
    csrf_token = response.json().get("csrfToken")

    # Step 2: POST request to analyze the YouTube video
    analyze_url = "https://y2meta.net/api/analyze"
    headers = {
        # "Content-Type": "application/json",
        # "Accept": "application/json, text/plain, */*",
        # "Accept-Encoding": "gzip, deflate, br, zstd",
        # "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        # "Cookie": "i18n_y2meta=en; fpestid=HC2_NC5y1TjwmX-Ieiy-aPXtBLbU-WtaVpsWW2Eoe2fUbpESWFXB7K_9mMiBH9JXZfWBGA; h3=Fe26.2**c13134055e183ab0805a025fa9206e27054a318e289c09c7a4718922e9a035f3*etgnrwxh-ZnX8P1hR_9sxg*R0-Eqcdy7bmmyQzFzm9HDtYuc-znwTTWFckm1aQcQyHD5yqtMHKLg95yZVlpu6i17OzLnL1Twq3R20r9JH9KRVCbkLl33HDjz49PdXNay3X0F07n8LP_Grjjx9uVKwMTokt2KqSbkSc84ewxt7IyPRgsau_fCOlqkIXjw5YXzLSYAdO2gPieY_QvPWL2T1as**3623916eabdf8730e5ef3f850e1312e8952b5e030fab3927dc1aa83e0c16a3ec*Ijxv45b8o_tgCTVQwPsa4jkIoyU-EKsgYBSGp29NPl8",
        "Origin": "https://y2meta.net",
        "Referer": "https://y2meta.net/",
        "Sc-Token": csrf_token,  # CSRF token from GET request
        "Sec-Ch-Ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    }

    # Prepare payload for the POST request
    payload = {
        "q": "https://www.youtube.com/watch?v=How73-4H130"  # Replace with your YouTube URL
    }

    # Send the POST request
    response = session.post(analyze_url, headers=headers, data=payload)

    # Check the response
    if response.status_code == 200:
        videos_data = response.json()['optionDownloads'][1]['list'][0]
        requestId, trackId, resolution = videos_data['requestId'], videos_data['trackId'], videos_data['resolution']
        convert_url = 'https://y2meta.net/api/convertfile'

        convert_payload = {
            "data": requestId,
            "trackId": trackId
        }

        response = session.post(convert_url, headers=headers, data=convert_payload)
        download_data = response.json()

        update_api = 'https://y2meta.net/api/update-client'
        update_payload = {
            "cdn": download_data["cdn"], 
            "clientId": "LsExxk03j0pk1S7pAudB",
            "requestId": requestId,
            "socketServer": download_data["socketServerUrl"],
            "trackId": trackId
        }
        response = session.post(update_api, headers=headers, data=update_payload)
        print (response.text)
        download_url = f'{download_data["cdn"]}/api/v1/downloadfile?dm=y2meta.net&id={download_data["requestId"]}&t={resolution}'

        download_video(session, headers, download_url, 'iiiiid.mp4')

        print("Analysis Response:", videos_data, download_url)
    else:
        print("Error:", response.status_code, response.text)




# https://line.1010diy.com/web/free-mp3-finder/detailV1?url=https://www.youtube.com/watch?v=0cDjtfL4FOw

youtube_download_best_quality_video('https://www.youtube.com/watch?v=0cDjtfL4FOw', 'iddiii')