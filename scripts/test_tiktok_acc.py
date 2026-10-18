import datetime
import requests, json, re
from bs4 import BeautifulSoup



headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}



def get_tiktok_account_info(url):
    session = requests.Session()

    try:
        response = session.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        script_tag = soup.find("script", id="__UNIVERSAL_DATA_FOR_REHYDRATION__", type="application/json")
        if script_tag:
            json_data = script_tag.string
            parsed_data = json.loads(json_data)
            user_information = parsed_data["__DEFAULT_SCOPE__"]["webapp.user-detail"]
            user_data = user_information["userInfo"]["user"]
            user_stats = user_information["userInfo"]["stats"]
            shareMeta = user_information["shareMeta"]

            user_data["user_stats"] = user_stats
            user_data["shareMeta"] = shareMeta

            return user_data
        else:
            return None

    except Exception as error:None




print(get_tiktok_account_info("https://www.tiktok.com/@manal.kasmii"))