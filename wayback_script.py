import wayback
import re
from wayback import WaybackClient
from bs4 import BeautifulSoup
import requests
import urllib
from lxml.html.clean import Cleaner
import pandas as pd
import WPUtils as wp

# this function is used to clean the html restored
def sanitize(dirty_html):
  cleaner = Cleaner(page_structure=True,
                meta=True,
                embedded=True,
                links=True,
                style=True,
                processing_instructions=True,
                inline_style=True,
                scripts=True,
                javascript=True,
                comments=True,
                frames=True,
                forms=True,
                annoying_tags=True,
                remove_unknown_tags=True,
                safe_attrs_only=True,
                safe_attrs=frozenset(['src','color', 'href', 'title', 'class', 'name', 'id']),
                remove_tags=('span', 'font', 'div')
                )

  return cleaner.clean_html(dirty_html)

# this function is used to list all urls that are available and returns a 200
def available_archived_urls(site):
  headers = {
      'authority': 'web.archive.org',
      'accept': '*/*',
      'accept-language': 'en-US,en;q=0.9',
      'dnt': '1',
      'referer': 'https://web.archive.org/web/sitemap/djangutech.com',
      'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"Windows"',
      'sec-fetch-dest': 'empty',
      'sec-fetch-mode': 'cors',
      'sec-fetch-site': 'same-origin',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
  }

  response = requests.get(
      f'https://web.archive.org/web/timemap/json?url={site}&fl=timestamp:4,original,urlkey&matchType=prefix&filter=statuscode:200&filter=mimetype:text/html&collapse=urlkey&collapse=timestamp:4&limit=100000',
      headers=headers,
  )

  return  response.json()

# this function is used to retrieve an archived url in a possibly html format
def get_archived_content(url):
  
  client = WaybackClient()
  results = client.search(url)
  record = next(results)
  archived_url = record.view_url
  page = requests.get(archived_url)

  soup = BeautifulSoup(page.text, 'lxml')

  # find the title of the page
  title = soup.find('title').text

  # Find the following img tag after the h1 tag
  h1_tag = soup.find('h1')
  first_img_after_h1 = h1_tag.find_next('img')
  image_url = first_img_after_h1.get('src')

# clean the image url
  cleaned_url = urllib.parse.urlparse(image_url)
  cleaned_url = urllib.parse.ParseResult(scheme=cleaned_url.scheme, netloc=cleaned_url.netloc, path=cleaned_url.path, params='', query='', fragment='')
  clean_image_url = urllib.parse.urlunparse(cleaned_url)

  # Create a new HTML document with the extracted elements
  relevant_elements = soup.find_all(['h1', 'h2', 'h3', 'p'])
  cleaned_html = "<html><head></head><body>"
  cleaned_html += "".join(str(element) for element in relevant_elements)
  cleaned_html += "</body></html>"
  cleaned_html = sanitize(cleaned_html)

  # return the title, the cleaned html and the image url in dictionary format
  return {'title': title, 'content': cleaned_html, 'image_url': clean_image_url}

# function to clean urls
def clean_url(url):
  pattern = r'(https?://[^\/]+)'
  cleaned_url = re.sub(pattern, '', url)
  return cleaned_url

def recover(url):
  # get the content of the first url
  content = get_archived_content(url)

  # get the category id
  category_id = wp.get_cat_id('Uncategorized', logs)

  # get the image id
  try:
    image_id = wp.get_img_id(content['image_url'], logs)
  except:
    image_id = None
    pass

  # create the post data
  post_data = {
      'title': content['title'],
      'content': content['content'],
      'status': 'publish',
      'categories': [category_id],
      'featured_media': image_id
  }

  # upload the content
  upload = wp.upload_content(post_data, logs)

  if upload.status_code == 201:
    print("Recovered content has been uploaded successfully")
  else:
    print(upload.status_code)
  
  print("Trying to redirect the old url to the new one")
  url_to = upload.json()['guid']['rendered']
  url_to = clean_url(url_to)
  url_from = clean_url(url)
  print(wp.redirect(url_from, url_to, logs))

if __name__ == '__main__':

  logs = {
      'wpUN': 'groupetravail237',
      'wpPW': 'AfjR VVnj GlTz z6qp s2cy R6I7',
      'wpDomain': 'wayback-resurection.000webhostapp.com',
  }
  
  url = "http://www.rvlf.fr/telltale-behind-the-scenes-1-et-2-du-jeu-bttf-rvlf-★-retour-vers-le-futur-bttf-★-back-to-the-future/Jeu-retour-vers-le-futur-2010"

  recover(url)
