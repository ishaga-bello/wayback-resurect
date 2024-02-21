
import urllib.parse
import re
import random
import requests
import time
import base64
import json
from urllib import parse as urlparse
from PIL import Image, ImageColor, ImageEnhance
from io import BytesIO
from secrets import token_hex
from datetime import datetime, timedelta

session = requests.Session()
headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
}
session.headers.update(headers)

def header(user, password):
  credentials = user + ':' + password
  token = base64.b64encode(credentials.encode())
  header_json = {'Authorization': 'Basic ' + token.decode('utf-8')}
  return header_json

def get_cat_id(category, logs):
  hed = header(logs['wpUN'],logs['wpPW'])
  data = {'name': category}

  responce = session.post(f"http://{logs['wpDomain']}/wp-json/wp/v2/categories", headers = hed, json = data)

  if responce.status_code == 201:
    category_id = (responce.json()['id'])
  elif responce.status_code == 400:
    category_id = (responce.json()['data']['term_id'])
  else:
    print("There was an error with the category")

  return category_id

def upload_image(url, logs):
  def imgPost(data):
    title = f'pexels-photo-15792909'
    headers = {"Content-Type": "image/jpeg", "Accept": "application/json", 'Content-Disposition': f"attachment; filename={title}-{token_hex(20)}.jpg",}
    auth = (logs['wpUN'], logs['wpPW'])
    return session.post(url = f'http://{logs["wpDomain"]}/wp-json/wp/v2/media', auth=auth, headers=headers, data=data).json()

  data = requests.get(url).content
  image = Image.open(BytesIO(data))
  image = image.convert("RGB")
  enhancer = ImageEnhance.Color(image)
  fI = enhancer.enhance(random.uniform(.5,.5))
  imgData = BytesIO()
  fI.save(imgData, format='JPEG')
  img_data_value = imgData.getvalue()

  return imgPost(img_data_value)


def upload_content(post_data, logs):
  hed = header(logs['wpUN'],logs['wpPW'])
  responce = session.post(f"http://{logs['wpDomain']}/wp-json/wp/v2/posts", headers = hed, json = post_data)
  return responce

# function to control redirection plugin
def redirect(from_url, to_url, logs):
  # Base URL for the Redirection plugin's REST API
  base_url = f"https://{logs['wpDomain']}/wp-json/redirection/v1/"

  # Authentication credentials (replace with your actual credentials)
  username = logs['wpUN']
  password = logs['wpPW']  # Or use an API key if available

  # Data for the redirect you want to create
  json_data = {
      'url': f'{from_url}',
      'title': '',
      'match_data': {
          'source': {
              'flag_regex': False,
              'flag_trailing': True,
              'flag_case': True,
              'flag_query': 'exact',
          },
          'options': {},
      },
      'match_type': 'url',
      'action_type': 'url',
      'position': 0,
      'group_id': 1,
      'action_code': 301,
      'action_data': {
          'url': f'{to_url}',
      },
  }

  # Make a POST request to create the redirect
  response = requests.post(
      base_url + "redirect",
      json=json_data,
      auth=(username, password)
  )

  return response

if __name__ == "__main__":
  data = {
      'title' : 'test',
      'content' : 'test content',
      'status' : 'draft',
  }

  logs = {
    'wpUN': 'groupetravail237',
    'wpPW': 'AfjR VVnj GlTz z6qp s2cy R6I7',
    'wpDomain': 'wayback-resurection.000webhostapp.com',
  }

  base_url = "/2020/11/20/des-opportunites-plus-frequentes-quon-ne-penserait/"
  dest_url = "https://wayback-resurection.000webhostapp.com/this-is-the-title-here/"

  print(redirect(base_url, dest_url, logs))
