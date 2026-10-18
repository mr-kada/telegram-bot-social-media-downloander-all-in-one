import http.client
import json, asyncio


# Establishing the connection to the RapidAPI host
conn = http.client.HTTPSConnection("social-download-all-in-one.p.rapidapi.com")

# READ CONFIGS
with open("config.json", "r", encoding="utf-8") as file:
    config = json.load(file)


# API KEY
API_KEY = config["ALL_IN_ONE_API"]


# API
async def PaidAPI_Downloander(url):
    payload = json.dumps({
        "url": url
    })

    headers = {
        'x-rapidapi-key': API_KEY,
        'x-rapidapi-host': "social-download-all-in-one.p.rapidapi.com",
        'Content-Type': "application/json"
    }

    # Sending the POST request
    full_data, counter = None, 0

    while counter < 2:
        try:
            conn.request("POST", "/v1/social/autolink", payload, headers)
            res = conn.getresponse()
            data = res.read()

            full_data = json.loads(data.decode("utf-8"))
            break
        except Exception as error:pass
        counter += 1
        await asyncio.sleep(1)

    return full_data
