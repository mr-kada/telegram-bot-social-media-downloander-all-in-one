import requests
from bs4 import BeautifulSoup


initial_url = "https://ssstik.io/"
post_url = "https://ssstik.io/abc?url=dl"
options_url = "https://r.ssstik.top/b/index.sh"
options_post_url = "https://r.ssstik.top/b/index.sh"


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
}


options_headers = {
    "User-Agent": "Mozilla/5.0",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type",
    "Origin": "https://ssstik.io",
}


async def download_tiktok_image(video_url, save_path):

    try:
        # Use a session to maintain the same context
        with requests.Session() as session:
            session.headers.update(headers)

            # Step 1: Extract the `tt` value
            tt_value = "WkhzVG02" # extract_tt(session, initial_url, headers)

            # Step 2: Submit the form with the extracted `tt` value
            form_data = {
                "id": video_url,
                "locale": "en",
                "tt": tt_value,
            }

            response_content = session.post(post_url, data=form_data)
            # response_content = await submit_form(session, post_url, form_data)

            # Parse and print the result
            soup = BeautifulSoup(response_content.text, "html.parser")
            slides_data = soup.find("input", {"name": "slides_data"})["value"]

            # Extract data
            trending_actions = soup.find('div', id='trending-actions')
            likes = trending_actions.find('div', class_='d-flex flex-1 align-items-center justify-content-start').find_all('div')[-1].text.strip()
            comments = trending_actions.find('div', class_='d-flex flex-1 align-items-center justify-content-center').find_all('div')[-1].text.strip()
            shares = trending_actions.find('div', class_='d-flex flex-1 align-items-center justify-content-end').find_all('div')[-1].text.strip()

            # Find the <img> tag
            img_tag = soup.find('img', class_='u-round u-shadow--black result_author')

            # Extract attributes
            img_src = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None
            img_alt = img_tag['alt'] if img_tag and 'alt' in img_tag.attrs else None

            # Prepare JSON output
            data = {
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "account_name": img_alt,
                "profile_image_url": img_src,
            }

            # Example usage
            options_response = session.options(options_url, headers=options_headers)
            options_response = session.get(options_url, headers=options_headers)
            post_response = session.post(options_post_url, 
                data={
                    "slides_data": slides_data
                }, headers=headers)

            # Step 3: Extract the Final Link
            video_id, username = await get_tiktok_post_id(video_url)
            download_link = f'https://r1.ssstik.top/ssstik/{video_id}'

            data['account_username'] = str(username).replace('@', '')

            download_link = await download_file(session, download_link, save_path, 'mp4')
            print(download_link)
            return [download_link, data]

    except Exception as error:
        print(error)
        return None


async def get_tiktok_post_id(url):
    response = requests.get(url, allow_redirects=True)
    final_url = response.url
    # tiktok_id = final_url.split('/')[-1].split('?')[0]
    # return tiktok_id

    parts = final_url.split('/')
    username = parts[-3] if len(parts) > 3 else None  # Username appears before "photo"
    tiktok_id = parts[-1].split('?')[0] if len(parts) > 1 else None
    
    return tiktok_id, username



async def download_file(session, download_url, unique_id, extension):
    file_name = f"{unique_id}.{extension}"
    print (file_name, download_url)
    
    try:
        with session.get(download_url, stream=True) as response:
            if response.status_code in [200, 206]:
                with open(file_name, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                return file_name
            else:
                return download_url
    except Exception as error:
        print(error)
        return None





# import asyncio, aiohttp

# asyncio.run(download_tiktok_image('https://vt.tiktok.com/ZSBXTVas2/', 'tiktok_image'))




# async def get_final_link(session, SlidesData, video_url):
    # headers = {
    #     "User-Agent": "Mozilla/5.0",
    #     "Access-Control-Request-Method": "POST",
    #     "Access-Control-Request-Headers": "content-type",
    #     "Origin": "https://ssstik.io",
    # }


    
    # options_response = session.options(options_url, headers=headers)

    # # Step 1: Perform an OPTIONS Request
    # options_response = session.get(options_url, headers=headers)
    
    # Check if OPTIONS was successful
    # if options_response.status_code != 204:  # Typically 204 No Content
    #     raise Exception("OPTIONS request failed.")

    # Step 2: Perform a POST Request
    # post_url = "https://r.ssstik.top/b/index.sh"
    # slides_data = {
    #     "slides_data": SlidesData
    # }
    # post_headers = {
    #     "Content-Type": "application/x-www-form-urlencoded",
    #     "User-Agent": "Mozilla/5.0",
    # }
    # post_response = session.post(post_url, data=slides_data, headers=post_headers)
    
    # # Check if POST was successful
    # if post_response.status_code != 200:
    #     raise Exception("POST request failed.")

    # # Step 3: Extract the Final Link
    # video_id = get_tiktok_post_id(video_url)
    # return f'https://r1.ssstik.top/ssstik/{video_id}'


# async def submit_form(session, post_url, form_data):
#     response = session.post(post_url, data=form_data)
#     response.raise_for_status()
#     return response.text





# def get_final_link(session, SlidesData, video_url):
#     headers = {
#         "User-Agent": "Mozilla/5.0",
#         "Access-Control-Request-Method": "POST",
#         "Access-Control-Request-Headers": "content-type",
#         "Origin": "https://ssstik.io",
#     }

#     options_url = "https://r.ssstik.top/b/index.sh"
    
#     options_response = session.options(options_url, headers=headers)

#     # Step 1: Perform an OPTIONS Request
#     options_response = session.get(options_url, headers=headers)
    
#     # Check if OPTIONS was successful
#     if options_response.status_code != 204:  # Typically 204 No Content
#         raise Exception("OPTIONS request failed.")

#     # Step 2: Perform a POST Request
#     post_url = "https://r.ssstik.top/b/index.sh"
#     slides_data = {
#         "slides_data": SlidesData
#     }
#     post_headers = {
#         "Content-Type": "application/x-www-form-urlencoded",
#         "User-Agent": "Mozilla/5.0",
#     }
#     post_response = session.post(post_url, data=slides_data, headers=post_headers)
    
#     # Check if POST was successful
#     if post_response.status_code != 200:
#         raise Exception("POST request failed.")

#     # Step 3: Extract the Final Link
#     video_id = get_tiktok_post_id(video_url)
#     return f'https://r1.ssstik.top/ssstik/{video_id}'



# def extract_tt(session, url, headers):
#     response = session.get(url, headers=headers)
#     response.raise_for_status()

#     soup = BeautifulSoup(response.text, "html.parser")
#     form = soup.find("form", {"id": "_gcaptcha_pt"})

#     print (form)
    
#     if form and "include-vals" in form.attrs:
#         include_vals = form["include-vals"]
#         if "tt:'" in include_vals:
#             return include_vals.split("tt:'")[1].split("'")[0]

#     raise ValueError("`tt` value not found in the page.")




# def main():
#     initial_url = "https://ssstik.io/"
#     post_url = "https://ssstik.io/abc?url=dl"
#     # video_url = "https://vt.tiktok.com/ZS6NsUw35/"
#     video_url = "https://www.tiktok.com/@bbjdi____107/photo/7450460578746780945"

#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
#     }

#     # Use a session to maintain the same context
#     with requests.Session() as session:
#         session.headers.update(headers)

#         # Step 1: Extract the `tt` value
#         tt_value = extract_tt(session, initial_url, headers) # "WkhzVG02"
#         print(f"Extracted tt value: {tt_value}")

#         # Step 2: Submit the form with the extracted `tt` value
#         form_data = {
#             "id": video_url,
#             "locale": "en",
#             "tt": tt_value,
#         }

#         response_content = submit_form(session, post_url, form_data)

#         # Parse and print the result
#         soup = BeautifulSoup(response_content, "html.parser")
#         slides_data = soup.find("input", {"name": "slides_data"})["value"]
#         print (slides_data)
        
#         # Example usage
#         try:
#             download_link = get_final_link(session, slides_data, video_url)
#             print(f"Final download link: {download_link}")
#         except Exception as e:
#             print(f"Error: {e}")


#         # result = soup.find("div", {"id": "target"})

#         # if result:
#         #     print("Extracted result:")
#         #     print(result.text.strip())
#         # else:
#         #     print("No result found in the POST response.")

# if __name__ == "__main__":
#     main()