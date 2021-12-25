from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
import re

API_KEY = 'AIzaSyAnvb2bMX3tT3PdStNOJQuWKrMrdHyX5dI'
SAMPLE_ID = 'mPn5WDCyr2o'

youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_comments(id = SAMPLE_ID):
    request = youtube.commentThreads().list(
            part="snippet",
            videoId=str(id),
            maxResults=10
        )
    response = request.execute()
    return [item['snippet']['topLevelComment']['snippet']['textOriginal'] for item in response['items']]

def get_video_id(url):
    if type(url) != str or re.match(r'https://www.youtube.com/watch', url) == None:
        return False

    url_data = urlparse(url)
    query = parse_qs(url_data.query)
    video_id = query["v"][0]
    return video_id