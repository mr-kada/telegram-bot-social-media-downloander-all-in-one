import datetime
import requests, json, re
from bs4 import BeautifulSoup



headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


translate_info = {
    "id": {"arabic": "ايدي"},
    "short Id": {"arabic": "المعرف القصير"},
    "unique Id": {"arabic": "المعرف الفريد"},
    "nickname": {"arabic": "الاسم المستعار"},
    "signature": {"arabic": "التوقيع"},
    "create Time": {"arabic": "وقت الإنشاء"},
    "verified": {"arabic": "موثق"},
    "sec Uid": {"arabic": "المعرف الآمن"},
    "ftc": {"arabic": "اف تي سي"},
    "relation": {"arabic": "العلاقة"},
    "open Favorite": {"arabic": "فتح المفضلة"},
    "risk": {"arabic": "المخاطرة"},
    "comment Setting": {"arabic": "إعدادات التعليقات"},
    "commerce User": {"arabic": "مستخدم التجارة"},
    "ios": {"arabic": "آي أو إس"},
    "android": {"arabic": "أندرويد"},
    "category": {"arabic": "الفئة"},
    "category Button": {"arabic": "زر الفئة"},
    "duet Setting": {"arabic": "إعدادات الدويتو"},
    "stitch Setting": {"arabic": "إعدادات الخياطة"},
    "private Account": {"arabic": "حساب خاص"},
    "secret": {"arabic": "سري"},
    "is A D Virtual": {"arabic": "هل هو إعلان افتراضي"},
    "room Id": {"arabic": "معرف الغرفة"},
    "unique Id Modify Time": {"arabic": "وقت تعديل المعرف الفريد"},
    "tt Seller": {"arabic": "بائع تيك توك"},
    "region": {"arabic": "المنطقة"},
    "download Setting": {"arabic": "إعدادات التنزيل"},
    "show Music Tab": {"arabic": "عرض علامة الموسيقى"},
    "show Question Tab": {"arabic": "عرض علامة الأسئلة"},
    "show Play List Tab": {"arabic": "عرض علامة قائمة التشغيل"},
    "following Visibility": {"arabic": "رؤية المتابعين"},
    "recommend Reason": {"arabic": "سبب التوصية"},
    "now Invitation Card Url": {"arabic": "رابط بطاقة الدعوة الحالية"},
    "nick Name Modify Time": {"arabic": "وقت تعديل الاسم المستعار"},
    "is Embed Banned": {"arabic": "هل التضمين محظور"},
    "can Exp Playlist": {"arabic": "يمكن توسيع قائمة التشغيل"},
    "profile Embed Permission": {"arabic": "إذن تضمين الملف الشخصي"},
    "language": {"arabic": "اللغة"},
    "suggest Account Bind": {"arabic": "اقتراح ربط الحساب"},
    "is Organization": {"arabic": "هل منظمة"},
    "follower Count": {"arabic": "عدد المتابعين"},
    "following Count": {"arabic": "عدد المتابعين"},
    "heart": {"arabic": "الإعجابات"},
    "heart Count": {"arabic": "عدد الإعجابات"},
    "video Count": {"arabic": "عدد الفيديوهات"},
    "digg Count": {"arabic": "عدد الحفر"},
    "friend Count": {"arabic": "عدد الأصدقاء"},
    "title": {"arabic": "العنوان"},
    "desc": {"arabic": "الوصف"},
    "avatar Larger": {"arabic": "الصورة الرمزية الكبيرة"},
    "avatar Medium": {"arabic": "الصورة الرمزية المتوسطة"},
    "avatar Thumb": {"arabic": "الصورة المصغرة"},
    "link": {"arabic": "الرابط"}
}




# Expanded language map
language_map = {
    "en": "الإنجليزية 🇬🇧",
    "ar": "العربية 🇸🇦",
    "fr": "الفرنسية 🇫🇷",
    "es": "الإسبانية 🇪🇸",
    "de": "الألمانية 🇩🇪",
    "zh": "الصينية 🇨🇳",
    "ja": "اليابانية 🇯🇵",
    "it": "الإيطالية 🇮🇹",
    "ru": "الروسية 🇷🇺",
    "hi": "الهندية 🇮🇳",
    "tr": "التركية 🇹🇷",
    "fa": "الفارسية 🇮🇷",
    "he": "العبرية 🇮🇱",
    "ur": "الأردية 🇵🇰",
    "ko": "الكورية 🇰🇷",
    "pt": "البرتغالية 🇵🇹",
}

# Expanded country map with a focus on the Middle East and other countries
country_map = {
    # Middle Eastern countries
    "SA": "المملكة العربية السعودية 🇸🇦",
    "AE": "الإمارات العربية المتحدة 🇦🇪",
    "EG": "مصر 🇪🇬",
    "JO": "الأردن 🇯🇴",
    "LB": "لبنان 🇱🇧",
    "IQ": "العراق 🇮🇶",
    "KW": "الكويت 🇰🇼",
    "QA": "قطر 🇶🇦",
    "OM": "سلطنة عمان 🇴🇲",
    "SY": "سوريا 🇸🇾",
    "YE": "اليمن 🇾🇪",
    "PS": "فلسطين 🇵🇸",
    "BH": "البحرين 🇧🇭",
    "IR": "إيران 🇮🇷",
    "TR": "تركيا 🇹🇷",
    "IL": "إسرائيل 🇮🇱",
    
    # Additional countries
    "US": "الولايات المتحدة الأمريكية 🇺🇸",
    "GB": "المملكة المتحدة 🇬🇧",
    "FR": "فرنسا 🇫🇷",
    "ES": "إسبانيا 🇪🇸",
    "DE": "ألمانيا 🇩🇪",
    "CN": "الصين 🇨🇳",
    "JP": "اليابان 🇯🇵",
    "IN": "الهند 🇮🇳",
    "PK": "باكستان 🇵🇰",
    "KR": "كوريا الجنوبية 🇰🇷",
    "IT": "إيطاليا 🇮🇹",
    "BR": "البرازيل 🇧🇷",
    "RU": "روسيا 🇷🇺",
    "AU": "أستراليا 🇦🇺",
    "ZA": "جنوب أفريقيا 🇿🇦",
    "CA": "كندا 🇨🇦",
    "MX": "المكسيك 🇲🇽",
    "AR": "الأرجنتين 🇦🇷",
    "PT": "البرتغال 🇵🇹",
}



async def get_tiktok_account_info(url):
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


# Function to process JSON data
async def process_json(data, message, link_list):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and value.startswith("http"):
                converted_key = re.sub(r'(?<!^)([A-Z])', r' \1', key)

                if converted_key in translate_info:
                    converted_key = translate_info[converted_key]["arabic"]

                link_list[converted_key] = value
            elif isinstance(value, (dict, list)):
                message, link_list = await process_json(value, message, link_list)
            else:
                converted_key = re.sub(r'(?<!^)([A-Z])', r' \1', key)
                if value == True:
                    fixed_value = "نعم"
                elif value == False:
                    fixed_value = "لا"
                else:
                    fixed_value = value

                if converted_key == "create Time" or converted_key == "unique Id Modify Time" or converted_key == "nick Name Modify Time":
                    try:
                        readable_time = datetime.datetime.fromtimestamp(int(fixed_value)) 
                        fixed_value = readable_time.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        fixed_value = "لم يقم بأي تغيير"

                if converted_key == "language":
                    fixed_value = language_map.get(str(fixed_value), fixed_value)

                if converted_key == "region":
                    fixed_value = country_map.get(str(fixed_value), fixed_value)

                if converted_key in translate_info:
                    converted_key = translate_info[converted_key]["arabic"]

                message += f"← **{converted_key} :** {fixed_value}\n"
    elif isinstance(data, list):
        for i, item in enumerate(data):
            message, link_list = await process_json(item, message, link_list)

    return message, link_list
