from __future__ import print_function
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()
from os import environ
import io
import json
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import db
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__)
CORS(app)

@app.route("/optimisePrompt", methods=["POST"])
def optimisePrompt():
    data = request.get_json()
    prompt = data["prompt"]
    EDENAI_API_KEY = environ.get('EDENAI_API_KEY')
    headers = {"Authorization": f"Bearer {EDENAI_API_KEY}"}
    url ="https://api.edenai.run/v2/text/prompt_optimization"
    payload = {
        "providers": "openai",
        "text": prompt,
        # "Alabasta Bakery is a chain that delivers delicious bakery items like cakes, breads, pastries, cookies and many similar packaged items. Need to create an image for email advertisement for the upcoming Indian Independence day for all the users getting 20 percent discount on all the products.",
        "target_provider" : "google"
    }
    response = requests.post(url, json=payload, headers=headers)

    result = json.loads(response.text)
    # print(result['openai'])
    return result['openai']

def generateImg(prompt):
    API_URL = "https://api.edenai.run/v2/image/generation"
    EDENAI_API_KEY = environ.get('EDENAI_API_KEY')
    headers  = {"Authorization": f"Bearer {EDENAI_API_KEY}"}
    provider = "openai"
    payload = {
    "providers": provider,
    "text": prompt,
    "resolution" : "512x512"
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)

    result = json.loads(response.text)
    image_url = result[provider]['items'][0]['image_resource_url']
    return image_url

def generateCaption(prompt):
    url = "https://api.textcortex.com/v1/texts/ads"
    payload = {
        "description": prompt,
        "max_tokens": 250,
        "mode": "general",
        "model": "chat-sophos-1",
        "n": 1,
        "name": "rakugen",
        "source_lang": "en",
        "target_lang": "en",
        "temperature": 0.65
    }
    TEXT_CORTEX_API = environ.get('TEXT_CORTEX_API')

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TEXT_CORTEX_API}"
    }

    response = requests.post(url, json=payload, headers=headers)
    caption = response.json()["data"]["outputs"][0]["text"]
    return caption
    
def generateImg2(prompt):
    res = requests.get(f'https://www.genpictures.com/api/image?prompt={prompt}')
    image = 'data:image/jpg;base64,'+res.json()['imageData']
    return image

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = data["prompt"]
    # prompt = "To generate a advertisement for Bakery on Indian Independence day for social media posts"
    img_url = generateImg2(prompt)
    text = generateCaption(prompt)
    
    res = {}
    res["img_url"] = img_url
    res["caption"] = text
    
    return res

@app.route("/upcoming-events", methods=["POST"])
def fetch_upcoming_events():
    data = request.get_json()
    events = gcal_list_events()
    buisnessName = data["buisness-name"]
    rows = []
    for event in events:
        prompt = "To generate a marketing campaign on the occasion of " + event["summary"] + " with attractive sales on varied products at "+ buisnessName
        row = {}
        row["event"] = event["summary"]
        row["prompt"] = prompt
        rows.append(row)
    res = {}
    res["upcomingEvents"] = rows
    return res


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def gcal_list_events():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        events_result = service.events().list(calendarId='en.indian#holiday@group.v.calendar.google.com', timeMin=now,
                                              maxResults=3, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return []

        # Prints the start and name of the next 10 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(event['summary'])
        
        return events

    except HttpError as error:
        print('An error occurred: %s' % error)
        return []

# @app.route("/genImage2", methods=["POST"])
# def generateImages2():
#     data = request.get_json()
#     prompt = data["prompt"]
#     res = requests.get(f'https://www.genpictures.com/api/image?prompt={prompt}')
#     image = 'data:image/jpg;base64,'+res.json()['imageData']
#     resp = {}
#     resp["image"] = image
#     return resp

# Hugging Face Method

# @app.route("/genImage", methods=["POST"])
# def generateImages():
#     data = request.get_json()
#     # print(data)
#     API_URL = environ.get('IMG_API_URL')
#     API_TOKEN = environ.get('IMG_API_TOKEN')
#     print(API_URL)
#     print(API_TOKEN)
#     headers = {"Authorization": f"Bearer {API_TOKEN}"}
#     try:
#         image_bytes = handle_hfquery(API_URL, headers, {
#             "inputs": "advertisement image without text for bakery house on indian independence day",
#         })
#         image = Image.open(io.BytesIO(image_bytes))
#         image.save("temp.jpg")
#     except:
#         print("Some Error")
#     resp = {}
#     resp["status"] = "WIP"
#     return resp

# def post_request(API_URL, headers, payload):
#     response = requests.post(API_URL, headers=headers, json=payload)
#     return response

# def handle_hfquery(API_URL, headers, payload):
#     response = requests.post(API_URL, headers=headers, json=payload)
#     print(response)
#     return response.content

@app.route('/add_campaign', methods=["POST"])
def add_campaign():
    post_data = request.get_json()
    try:
        campaign_doc = {
                        'title': post_data['title'],
                        'raw_prompt': post_data['raw_prompt'],
                        'engineered_prompt': post_data['engineered_prompt'],
                        'generated_content': post_data['generated_content'],
                        'base64_img': post_data['base64_img'],
                        'created_date': post_data['created_date'],
                        'schedule_date': post_data['schedule_date'],
                        'medium': post_data['medium']
                    }
        db.db.campaigns.insert_one(campaign_doc)
        return jsonify({"response": "success"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/update_campaign', methods=['POST'])
def query_records():
    post_data = request.get_json()
    id = post_data['_id']
  
    if db.db.campaigns.count_documents({ "_id": ObjectId(id) }, limit = 1) == 0:
        return jsonify({'error': 'campaign not found'})
    try:
        campaign_doc = {
                        'title': post_data['title'],
                        # 'raw_prompt': post_data['raw_prompt'],
                        # 'engineered_prompt': post_data['engineered_prompt'],
                        'generated_content': post_data['generated_content'],
                        # 'base64_img': post_data['base64_img'],
                        # 'created_date': post_data['created_date'],
                        'schedule_date': post_data['schedule_date'],
                        'medium': post_data['medium']
                    }
        response = db.db.campaigns.update_one(
            { "_id": ObjectId(id) },
            { "$set": campaign_doc }
        )
        return jsonify({"response": "success"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
   
    else:
        return jsonify({"response": "success"}), 200
    
@app.route('/delete_campaign', methods=["DELETE"])
def delete_campaign():
    post_data = request.get_json()
    id = post_data['_id']
    print(id)
    if db.db.campaigns.count_documents({ "_id": ObjectId(id) }, limit = 1) == 0:
        return jsonify({'error': 'campaign does not exist'})

    try:
        response = db.db.campaigns.delete_one( { "_id": ObjectId(id) } )

        return jsonify({"response": "success"}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/searchwithID', methods=["GET"])
def search_campaign_ID():
    args = request.args
    _id = args.get('_id')
    try:
        campaign_record = db.db.campaigns.find_one({"_id": ObjectId(_id) }, {"base64_img": 1})
        return jsonify({"base64_img": campaign_record["base64_img"]}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/search', methods=["GET"])
def search_campaign():
    try:
        campaign_records = db.db.campaigns.find({}, {"base64_img": 0})
        records = []
        list_cur = list(campaign_records)
  
        # Converting to the JSON
        json_data = dumps(list_cur, indent = 2)
        print(json_data)
        return json_data

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# import time
# import atexit
# from apscheduler.schedulers.background import BackgroundScheduler

# def print_date_time():
#     print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))


# scheduler = BackgroundScheduler()
# scheduler.add_job(func=print_date_time, trigger="interval", seconds=10)
# scheduler.start()

# # Shut down the scheduler when exiting the app
# atexit.register(lambda: scheduler.shutdown())

# def main():
#     print(compare_with_base())

# if __name__ == '__main__':
#     main()