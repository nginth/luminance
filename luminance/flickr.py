import json
import os
import flickrapi

api_key = ''
api_secret = ''

with open(os.getcwd() + '/secrets.json') as data_file:
    secrets = json.load(data_file)
    api_key = secrets['flickr']['key']
    api_secret = secrets['flickr']['secret']

def flickrAPIUser(username):
    return flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json', username=username)

def get_photo_urls(photos):
    template_url = "https://farm{}.staticflickr.com/{}/{}_{}.jpg"
    return [template_url.format(p['farm'], p['server'], p['id'], p['secret']) for p in photos]