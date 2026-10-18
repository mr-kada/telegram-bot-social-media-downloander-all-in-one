import http.client
import json, asyncio


# Establishing the connection to the RapidAPI host
conn = http.client.HTTPSConnection("social-download-all-in-one.p.rapidapi.com")

# API KEY
API_KEY = "1eb84db7c2mshfe959c731c39c1dp1adf87jsn8c3f611b2111"


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
