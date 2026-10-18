import requests, json
from bs4 import BeautifulSoup


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


async def get_tiktok_infoV2(url, method_img=False):
    session = requests.Session()

    try:
        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        script_tag = soup.find("script", id="__UNIVERSAL_DATA_FOR_REHYDRATION__", type="application/json")
        if script_tag:
            json_data = script_tag.string
            parsed_data = json.loads(json_data)

            if method_img == True:
                media_type = "webapp.app-context"
            else:
                media_type = "webapp.video-detail"

            auther = parsed_data["__DEFAULT_SCOPE__"][media_type]["itemInfo"]["itemStruct"]["author"]
            stats = parsed_data["__DEFAULT_SCOPE__"][media_type]["itemInfo"]["itemStruct"]["stats"]
            authorStats = parsed_data["__DEFAULT_SCOPE__"][media_type]["itemInfo"]["itemStruct"]["authorStats"]
            locationCreated = parsed_data["__DEFAULT_SCOPE__"][media_type]["itemInfo"]["itemStruct"]["locationCreated"]
            locationCreated = parsed_data["__DEFAULT_SCOPE__"][media_type]["itemInfo"]["itemStruct"]["locationCreated"]

            account_id = auther["id"]
            account_username = auther["uniqueId"]
            account_neckname = auther["nickname"]
            account_ProfilePic = auther["avatarLarger"]
            account_bio = auther["signature"]
            account_verified = auther["verified"]

            diggCount = stats["diggCount"]
            shareCount = stats["shareCount"]
            commentCount = stats["commentCount"]
            playCount = stats["playCount"]
            collectCount = stats["collectCount"]

            followerCount = authorStats["followerCount"]
            followingCount = authorStats["followingCount"]
            heart = authorStats["heart"]
            heartCount = authorStats["heartCount"]
            videoCount = authorStats["videoCount"]
            account_diggCount = authorStats["diggCount"]
            friendCount = authorStats["friendCount"]


            # print (account_id)
            # print (account_username)
            # print (account_neckname)
            # print (account_ProfilePic)
            # print (account_country)
            # print (account_verified)
            
            # print (diggCount)
            # print (shareCount)
            # print (commentCount)
            # print (playCount)
            # print (collectCount)

            # print (followerCount)
            # print (followingCount)
            # print (heart)
            # print (heartCount)
            # print (videoCount)
            # print (account_diggCount)
            # print (friendCount)

            # print (locationCreated)

            return {
                "id": account_id,
                "account_username": account_username,
                "account_name": account_neckname,
                "profile_image_url": account_ProfilePic,
                "account_verified": account_verified,
                "likes": diggCount,
                "comments": commentCount,
                "favorites": collectCount,
                "shares": shareCount,
                "video_duration": "غير متاح",
                "playCount": playCount,
                "account_bio": account_bio,
                "followerCount": followerCount,
                "followingCount": followingCount,
                "heart": heart,
                "heartCount": heartCount,
                "videoCount": videoCount,
                "account_diggCount": account_diggCount,
                "friendCount": friendCount,
                "locationCreated": locationCreated
            }

        else:
            return None

    except Exception as error:print (error)












# tiktok_url = "https://vt.tiktok.com/ZSjoy8TBq/"
# get_tiktok_infoV2(tiktok_url)