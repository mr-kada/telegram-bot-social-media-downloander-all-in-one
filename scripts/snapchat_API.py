import requests, os, json 
from bs4 import BeautifulSoup
from scripts.paid_API import PaidAPI_Downloander



async def get_snapchat_info(json_dict):
    not_exist = 'غير متاح'
    user_data = {
        "username": not_exist,
        "title": not_exist,
        "subscriberCount": not_exist,
        "bio": not_exist,
        "websiteUrl": not_exist,
        "profilePictureUrl": not_exist,
        "address": not_exist
    }

    try:
        data = json_dict["props"]["pageProps"]["userProfile"]["publicProfileInfo"]
        user_data["username"] = data["username"]
        user_data["title"] = data["title"]
        user_data["subscriberCount"] = data["subscriberCount"]
        user_data["bio"] = data["bio"]
        user_data["websiteUrl"] = data["websiteUrl"]
        user_data["profilePictureUrl"] = data["profilePictureUrl"]
        user_data["address"] = data["address"]
    except:pass

    return user_data


async def download_media(json_dict):
    paths = []
    try:
        for i in json_dict["props"]["pageProps"]["story"]["snapList"]:
            file_url = i["snapUrls"]["mediaUrl"]

            if not file_url:
                continue

            paths.append(file_url)

            # r = requests.get(file_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})

            # if "image" in r.headers['Content-Type']:
            #     file_name = r.headers['ETag'].replace('"', '') + ".jpeg"
            # elif "video" in r.headers['Content-Type']:
            #     file_name = r.headers['ETag'].replace('"', '') + ".mp4"
            # else:
            #     continue

            # if os.path.isfile(file_name):
            #     continue

            # if r.status_code == 200:
            #     with open(file_name, 'wb') as f:
            #         for chunk in r:
            #             f.write(chunk)
            #     # print (f"Downloaded {file_name}")
            #     paths.append(file_name)
            # else:pass
                # print("[-] Cannot make connection to download media!")
    except Exception as error:pass
        # print("[-] No stories found for the last 24h.\n")
    return paths



async def get_json(url):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/103.0.2'}
    r = requests.get(url, headers=headers)

    if not r.ok:
        print("Oh Snap! No connection with Snap!")
        return None

    soup = BeautifulSoup(r.content, "html.parser")
    snaps = soup.find(id="__NEXT_DATA__").string.strip()
    data = json.loads(snaps)

    return data



async def SnapchatDownload(url, save_path):

    data = await PaidAPI_Downloander(url)
    print(data)

    if data == None:
        return None
    else:
        paths = []
        for video in data.get("medias"):
            paths.append(video.get("url"))
        
        return paths



# url = "https://snapchat.com/t/M7vKfeua"
# json_dict = get_json(url)
# if json_dict:
#     download_media(json_dict)