import http.client
import json

# Establishing the connection to the RapidAPI host
conn = http.client.HTTPSConnection("social-download-all-in-one.p.rapidapi.com")

x_url = "https://x.com/abodantee/status/1874217094906339460?s=46&t=lUD4RZ5AySQ-xonRvtUzKg"
tiktok_url = "https://www.tiktok.com/@yeuphimzz/video/7237370304337628442"
likee = "https://l.likee.video/v/Jsve8k"

jaco = "https://l.jaco.live/LS088kFzdo"

snap_chat = "https://snapchat.com/t/M7vKfeua"

pin = "https://www.pinterest.com/pin/68539225572073486/"

tiktok_url = "https://www.tiktok.com/@bbjdi____107/photo/7450251418180554000?_d=secCgYIASAHKAESPgo8DOwJydrYPfPkJbo4cj5muKDt1%2F%2FywHvFOvlBhnFEtmltNOQCAGpIy%2BGdzsW7tfXGcQr8cZz2p6KVmVmXGgA%3D&_r=1&checksum=7961cd854f45bbc0d238123baaec13a378fe2ae61c822ada17061c3d6cccf28d&cover_exp=v0&link_reflow_popup_iteration_sharer=%7B%22click_empty_to_play%22%3A1%2C%22dynamic_cover%22%3A1%2C%22follow_to_play_duration%22%3A-1%2C%22profile_clickable%22%3A1%7D&preview_pb=0&sec_user_id=MS4wLjABAAAA3jjLolaa4CSl4lWGb9X0ioAVcqJAdF39ySDZnLitajRp4hJHIlZ-8_HVKlud887D&share_app_id=1233&share_item_id=7450251418180554000&share_link_id=540F4688-5462-4534-AA8F-C782356E6B2E&sharer_language=en&social_share_type=14&source=h5_m&timestamp=1734687713&tt_from=copy&u_code=db6gef8j70ia5e&ug_btm=b2001%2Cb2001&ug_photo_idx=0&user_id=6799939677551805446&utm_campaign=client_share&utm_medium=ios&utm_source=copy"


fb = "https://fb.watch/wRB7GNoc4A/"

yt = "https://www.youtube.com/watch?v=A9CGF6BTd7Y"


acc_tiktok = "https://www.tiktok.com/@bbjdi____107/"

reel_tg = "https://www.instagram.com/reel/DI_wjeiMizy/?igsh=bHJoNTU1dXh4ZnY="

# JSON payload for the POST request
payload = json.dumps({
    "url": acc_tiktok
})

# Headers including the API key and content type
headers = {
    'x-rapidapi-key': "1eb84db7c2mshfe959c731c39c1dp1adf87jsn8c3f611b2111",
    'x-rapidapi-host': "social-download-all-in-one.p.rapidapi.com",
    'Content-Type': "application/json"
}

# Sending the POST request
conn.request("POST", "/v1/social/autolink", payload, headers)

# Reading the response
res = conn.getresponse()
data = res.read()

# Printing the decoded response
print(data.decode("utf-8"))
