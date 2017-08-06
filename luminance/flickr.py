import json
import os
import flickrapi

api_key = ''
api_secret = ''

with open(os.getcwd() + '/secrets.json') as data_file:
    secrets = json.load(data_file)
    api_key = secrets['flickr']['key']
    api_secret = secrets['flickr']['secret']

flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')
