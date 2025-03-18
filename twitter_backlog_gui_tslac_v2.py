import PySimpleGUI as sg
import zipfile
import os
import time
import re
from os import listdir
from os.path import isfile, join
import datetime
import json
import hashlib
import shutil
import sys
import requests
import threading
import uuid
import lxml.etree as ET
# for creating the metadata file
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from collections import OrderedDict
import errno
import twitter_wall_tool
import yt_dlp

my_icon = b'iVBORw0KGgoAAAANSUhEUgAAAWQAAAFkCAMAAAAgxbESAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAACvlBMVEUAwAAEwQQmySZH0kdn2WeG4Yai6KK17bXI8cjb9tvu++70/PT///9m2WZG0UYlySUFwQU4zjhw3HCf55/N8834/fj3/ffM8sye5543zjcDwQM7zzuD4IPC8ML2/fbB8MGC4II6zjoMwwxY1lip6qnt++2o6qhX1VcLwwsGwQZS1FKr6qv1/fVR1FGI4ojo+eiR5JEryytE0US37bf+//627bZD0UNc11zQ89DP889Z1lkCwAIBwAFN003W9dZe117O885A0EAexx6z7LMiyCJ/339833w5zjnU9NTT9NOK4or9//38/vwoyijS9NItyy1h2GEHwgeZ5pkZxhnH8cfF8cUXxhfg9+Dk+OQvzC/v++/y/PJI0khO0075/vlU1VRa1lr7/vtg2GBl2WVk2WRd111i2GJW1VZB0EEqyirx/PHf99/E8MSY5piT5JMpyiknyifK8srh+OGS5JLi+OJV1VWv668Nww2x7LGQ5JCA4IB63nojySPj+OPl+eUgyCCw67Cq6qpC0EI/0D+U5ZTL8stK0kpQ1FAkySQOww5F0UW47bi07LSW5ZaJ4omF4YXn+edj2GPm+eas6qyy7LKm6abq+upu226l6aVJ0kmV5ZXr+us2zTZ+33697701zTWg6KCd552H4YeE4YTd993a9trw+/DD8MOh6KFy3HK17LUMwgy87rwPxA9M00wKwgq77rsSxBIQxBAUxRQfyB+57rkhyCHp+uksyywuyy7c9twzzTNv2288zzzZ9tkbxxts22wJwgl33Xe67rrG8cYdxx36/vqB4IHs+ux23XZ13XWb5psWxRZL00sVxRV73nve996t6619330TxRN43nij6KNz3HNq2mqk6aQRxBE0zTTJ8sl03XTR9NE9zz1T1VNf11/z/PMyzDJo2miP448+zz6X5ZcwzDAcxxyc55xsx1JfAAAAAWJLR0QMgbNRYwAAAAd0SU1FB+gKGAksMPnnNBMAAAxaSURBVHja7d39XxTHHQfwQwX1btDTiERQVKIBDCKxJz4cGg1YTThMQDE+VAgqiSiJ+EARCRqtj4224gP4gA8tWm2rqDXVpj60Umttq9Vq20SNSWybtvkvii9b4+3d7M7szOzdsZ/3j/F293PfLPe9m5nddTgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAiS1SHjp2iYzp36ep0ughxOZ1du3SOiY7t1j0KUWVw9+j5TK84QtE7/tmefdyIKiAhsW+/JGIoqf+AgQmIakbyc4OchNng51NSEZVP2pAX0gmn9EFD3YjKrHvGMGLKsMwXEZXJ8G94iGmeEVmIathARo4igkaP8SKqjuyxwrkfGfeSF1FpsqTkfmT8BEQN6uUYIlFOLqIGfhOaGEek6v1NN6L6mzSZSPdKD7tH9T83Xs0jCvgy0uwc1V9+L6LIlNfsG9Xf60lEGddLdo3qpyCTKFWYZseo/qZOI4oVTbdfVH8vvkGUmzHTblE1P5xmEQvM/pa9ovqbE0csUVxip6j+3iwlFvHNtU9Uf/PyiGXy5tslqr8yC4MT4nnLHlH9DS0llvK9bYeompmbYmKx4gXtP6q/8lnEcgtfa+9RNT+e3iAhsGh6+47qz11BQmJaWnuOqvEOCZF323NUzYAhCZmy9hvV3+L00CV3VbbXqJpPuSWS0yxd1rEyNbWy47vLGV4cnxbKqFziBT6WX5U8Ohj7ZC2qt2qR8eujQxeVV7TpGvfxSQ3y7eSnd169wnhoYFKoovKPYkwyWeM0uRPqNZpVTl7jGaIp7tBENYE5qsZKuedxwEoyr/G5XCs1KldH4Hw1c1R/70kd+65LDjxC9SqjrZJWy4vK1xF4+wdrVI33pZ7Irwc7xHzDzdZIi8rXEbj7B2tUf2vlfncLeo1LQp3hht+RFJWvI5joH2xRNbsdJbXImcGPss5ww/XZUqLydQRT/YMlqsbbcpsvZWZ3g/GWG2VE5esI5voHS1TNH/I4uUXeFPwwlcZbvuKVEJWvI5jsH8ZRNUZK/hqZHPwwyQybpohH5esIpvuHYVSN0dYUeTPDpqOyhaPydQTT/cMwqr/vyv5B1IGyvJVl2wXCUfk6gvn+Qbgm/D6QXWSB4GSLcFS+jmC+fxhE1fyC8sguMmXyYCvLtp5NolH5OoJA/9CNqvE96eMny4M2k6g6po2/LxqVryMI9A/dqJoB8G3yR6nqgx2oE9u229yCUfk6gkj/2MY8GDdEwVDgjOog58Z2xo3HCka1rPHpRdXYoWLAdUTAB4Z3J+u2uwSj8nUEkf6hE9VfqkvJsHamdtBlGfOmrlSxqHwdQah/uBjvQjJG0eTBCr9PjM05HJuWCEbl6wgi/YMwrgwfpGqKpqHxyX2qvGXbebbcLRiVryMI9Y/dbGNDg9XNhNWt25OfnJy/YW8d33b7vIJR+TqCSP/YxzRKlEjCUJNoVL6OINA/KFE1+oZjkfcLR+XrCAL9Yz9LkfuFY5EPiEfl6wjm+8cBlp976eFYZJdbQlS+jmC2f7gYfvT1IGHpYGRH1egZnskbIzuqxqHwTP6DyI6qMT48ky+J7Kian+i9wzN5UkIkR9XoQMJUbiRH1egYrsmzIjmqycEmy9VHclSNH4Zr8uZIjqoRE67JD0VyVI0R4Zo8J5KjaiwJ1+TTIjmqxuFwTX4kkqNqNIRr8m2RHFXjR+Ga3BnJUTWSwi9z0uGjO4/V/Jg16k+sS0aZ+Es3KrIvPOq6avLRNTUTG8uGl0+N4oz60w+sSnn8RPD/7gvfIjsnt52wGY1lLYnlJ5im1SlR005aNIE2LbnAZJGTLD5hTx1rO2GrEsun8j/6gBL1tONnvawIH3/Cccbkx4XqbhK36skJmyt4WxlK1A8djuQc9TX++WaH46zJxndOyQkb39a5Jsa2fRBMzXZIQ4n6i0erXpaprnHho1bxkcmvcL+U17l2FrZ1rpbzU90ONShRH98U4YLSu/CVPp7Huxj8Xy8ZJe8i6cvNrxzKUaJuePyvTUfU1XjRxcfHaAn+z0VGyTtLyjErNlt1kSlRf/2/f76s7I7rMf+/4OEC5QwzSn5MWpT+3RUXmRL16zXcQ2eoKPGMjUbrwp8xSh4tL016q9rHX1Ki/ubrV5xcKX2utTjzqVVyB4K/pq+l009XylUWmRJ16dOv+a3kkX3/hz9R/lIMp5/kzk5eVfl0GUpUj/8FBYmdpV2U6Nky0P/KPsqe1xol7y75z2tKk7Ii06JqH+j2UYyUsYK8HO0ityzKK88arrOX/bu6tEbVA3NpUX8XeMVupvDVA9dqAi/vaw7+UpfxCEG89HZ8WNUDRilRjwZ5aUFVjsDpnFcRezLITq8Ef3UX4+TPyv/S4zl2WkmRKVGLg//prP59RZ65Cv/hw6A7rL4afIM/hmjp7PahKopMi9qNtsH1+p3pnF9DV9Rfp+3tBmUbhqWzTWp+Ja35k/wi06Lu1VtQef7CGsbJwYWnVg4v0NkV7X7N50N3OYMzVnqRaVEHFxhsmJ8yYMe4qzrfPMe9MCCl0mAnadcofS+KIXp/VT/5O78su8q0qEy3tUor3zP35rIdFeMP33I6204C563D4yt2LKudu2cx07hhCeXgp1g2HqBs8Gpho+QnP9Oi/tlhAdqd4m6zbDxQ4Tjs0Xyp75MWtfiM+hrfoT3S5CDL1gnXVM7qTZQ5hE+N+hf1Rb5JOTTbZb+O55XO24w6L/Gd0qLuS1Vd41TaV5S/sm2fonZ2rDSjQNpbpUa9oLrIf6MdeQjb9iddaqtMuk6Q9VapUesK1Na4gHbrztmXGfcwSHGRiaewWtKbpUbtpLbIH9OO+wnrHoaqX7WwqJucN0uNeu6uyhqfpv5obGHdRdR29VUma+7IeLf0qHtVFrmQdtRtUcz7yLCgyGRYlYy3S42a10ddje9Rh/Oa2XeS67GiylIWZ9CjxiubxvXepzYbjttIWnXNi4zFGfSon6oqciv9tOHZTRaxiPjiDHrU0oFqatyHPn7H9+wAyy7AF1+cQY+6/I6KGt+lP79yPd+exhDLiC7O0Im6RcFSsWydh5pwPpLd+8C6KgsuztCLWiu/yPt1lj/wjuSWEAuJLc7Qieqpl13jeTpvYw73X4Wlt0URWpyhF9U3RG6Nx+ose77P/+E0gVhKZHGGXtSkz2TWuIfeBKiZI+2wtsoiizP0os5KlFfjz/QePr7LzB7PWn2LH/OLM3Sjxn0uq8Zz9JawpZubJr5NrGZ6cYZuVN88OTX+QvcylFaTI1yjLa+y2cUZ+lE9tRK+L2fv1x3QeWB27rLJZ3mVzS7OMIi6U3gx3p0tugfw3ZM/jqiQycUZBlGXC7a/g7f0999sftfu+yGosrnFGUZRr34qsLAmodXgqsD1boH/gZsehqLKphZnGEYd38NsFf5udHGjq4PQn0kZCQkzizMMo+YdM7Ww6G6NYWsaI/iBvy40VS7NiFIQ9dw/uFcKFHxsvND2n6Jd1R2iu68XuZVEPTdxM88uUxsZrrcsEr/C60zXUNT41nRVURtqmYfyz9zcpyqq1mKn9TUeXKkwqu9U2UmGz4mWNcUKo2otKLa6xnFfKo7q/NeGZL39VN94x6k4qtbGUmtr7KuyIGppUfPaoIVOzmq+UmpBVK2ReVbWOO9Ny6IuP761cUPizNzTaWmnc2cm3riw9XidZVG15ltY5by37BJV67mrln1WfGGfqFotFg3hFw+xU1StxH1WBHdOsFfUgBGYI+qD38q3W1St6RWqg/e7br+oAZM8igfxC912jBo4nKjwmp2HY+waNWDyvUhV8CXd7Rs1YDwxWsnsqq/ZbeeoAf4t/wY65EGT3aMGnCG1kr/tJ7VGIWqA/8TIvHInZzWiBvXlemld5CKiUg2XsoB5clU2ourwpgjfOn59STaiGs72iNwH07NlAqKy9ZXWpeZyb894D1HZRwnm7OJeyzV7d0sUovK5XLKbYwS34ZPPLyOqqdbStP8Aw4jMw+O3D3oRVeSv8WDjV+vTaaFdS75qvBeFqFLOk9ys+c2Hcq5canDObvtEczZcupJzqLl+ba4XUQEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABA138BwF8HiWZpPnoAAAAldEVYdGRhdGU6Y3JlYXRlADIwMjQtMTAtMjRUMDk6NDQ6NDgrMDA6MDC8VYt5AAAAJXRFWHRkYXRlOm1vZGlmeQAyMDI0LTEwLTI0VDA5OjQ0OjQ4KzAwOjAwzQgzxQAAAABJRU5ErkJggg=='

def make_metadata(metadata_dictionary):
    metadata = Element('dcterms:dcterms',
                       {'xmlns': 'http://dublincore.org/documents/dcmi-terms/',
                        'xmlns:dcterms': 'http://dublincore.org/documents/dcmi-terms/',
                        'xsi:schemaLocation': 'http://dublincore.org/documents/dcmi-terms/ qualifiedDcSchema.xsd',
                        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                        'xmlns:tslac': 'https://www.tsl.texas.gov/'})
    title = SubElement(metadata, 'dcterms:title')
    title.text = metadata_dictionary['title']
    description = SubElement(metadata, "dcterms:description.abstract")
    description.text = metadata_dictionary['description']
    if 'agency' in metadata_dictionary.keys():
        collection_name = SubElement(metadata, 'dcterms:relation.isPartOf')
        collection_name.text = f"{metadata_dictionary['agency']} social media archive"
    if 'preferredCitation' in metadata_dictionary.keys():
        citation = SubElement(metadata, 'dcterms:identifier.bibliographicCitation')
        citation.text = metadata_dictionary['citation']
    type1 = SubElement(metadata, 'dcterms:type')
    type1.text = "Text"
    creator = SubElement(metadata, 'dcterms:creator')
    creator.text = metadata_dictionary['creator']
    date_created = SubElement(metadata, 'dcterms:date.created')
    date_created.text = metadata_dictionary['create_date']
    SubElement(metadata, 'dcterms:subject').text = "Social media"
    subject2 = SubElement(metadata, 'dcterms:subject')
    subject2.text = metadata_dictionary['platform']
    if metadata_dictionary['type'] == "Facebook Event":
        facebook_note = SubElement(metadata, 'tslac:note')
        facebook_note.text = "Facebook page events data normalized to Twitter data model for access/rending purposes. Post identifier generated based upon timestamp of event beginning and ending, and page identifier. If date event created is unknown, date of creation is defaulted to date of event. Original post json format available on request with user data incorporated for completeness."
    if metadata_dictionary['type'] == "Facebook Album":
        facebook_note = SubElement(metadata, "tslac:note")
        facebook_note.text = "Facebook Album data normalized to Twitter data model for access/rendering purposes. Post identifier generated based upon upload timestamp with each item in the album preserved as a single post and subfoldered into the Album by its date of creation if known and title. Original post json format available on request with user data incorporated for completeness."
    if metadata_dictionary['type'] == "Facebook Post":
        facebook_note = SubElement(metadata, "tslac:note")
        facebook_note.text = "Facebook post data normalized to Twitter data model for access/rendering purposes. Post identifier generated based upon timestamp of the post. Original post in json format available upon requestwith user data incorporated for completeness."
    social_type = SubElement(metadata, 'tslac:socialmedia.platform')
    social_type.text = metadata_dictionary['platform']
    username = SubElement(metadata, 'tslac:socialmedia.username')
    username.text = metadata_dictionary['username']
    post_id = SubElement(metadata, 'tslac:socialmedia.identifier')
    post_id.text = metadata_dictionary['post_id']
    for item in metadata_dictionary['hashtags']:
        SubElement(metadata, 'tslac:socialmedia.hashtag').text = item
    for item in metadata_dictionary['mentions']:
        SubElement(metadata, 'tslac:socialmedia.mentions').text = item
    return metadata

def make_metadata2(preservation_directories=list, social_type=str, collection_name=str, agency=str):
    # create metadata files based on the standardized social media format, not the native social media format
    for preservation_directory in preservation_directories:
        for dirpath, dirname, filenames in os.walk(preservation_directory):
            for filename in filenames:
                if filename.endswith(".json"):
                    metadata_file = filename.replace(".json", ".metadata")
                    metadata_file = os.path.join(dirpath, metadata_file)
                    json_file = os.path.join(dirpath, filename)
                    j = open(json_file, "r")
                    post = json.loads(j.read())
                    metadata = Element('dcterms:dcterms',
                                       {'xmlns': 'http://dublincore.org/documents/dcmi-terms/',
                                        'xmlns:dcterms': 'http://dublincore.org/documents/dcmi-terms/',
                                        'xsi:schemaLocation': 'http://dublincore.org/documents/dcmi-terms/ qualifiedDcSchema.xsd',
                                        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                                        'xmlns:tslac': 'https://www.tsl.texas.gov/'})
                    title = SubElement(metadata, 'dcterms:title')
                    title.text = f"{filename.split('_')[0]}: {post['platform']} post id {post['post_id']}"
                    description = SubElement(metadata, 'dcterms:description.abstract')
                    description.text = f"{post['platform']} post text: {post['content_text']}"
                    collectionName = SubElement(metadata, 'dcterms:relation.isPartOf')
                    collectionName.text = collection_name
                    preferredCitation = SubElement(metadata, 'dcterms:identifier.bibliographicCitation')
                    my_preferredCitation = (f"{title.text}, @{post['user']['userid']}, {post['platform']}, {collection_name}."
                                              f" Archives and Information Services Division, Texas State Library and"
                                              f" Archives Commission.")
                    my_preferredCitation = my_preferredCitation.replace("@@", "@")
                    preferredCitation.text = my_preferredCitation
                    SubElement(metadata, 'dcterms:type').text = "Text"
                    creator = SubElement(metadata, 'dcterms:creator')
                    if agency != "":
                        creator.text = agency
                    else:
                        creator.text = post['user']['username']
                    date_created = SubElement(metadata, 'dcterms:date.created')
                    date_created.text = filename.split("_")[0]
                    SubElement(metadata, 'dcterms:subject').text = 'Social media'
                    SubElement(metadata, 'dcterms:subject').text = social_type
                    SubElement(metadata, 'tslac:socialmedia.platform').text = post['platform']
                    SubElement(metadata, 'tslac:socialmedia.username').text = post['user']['username']
                    SubElement(metadata, 'tslac:socialmedia.identifier').text = post['post_id']
                    hooks = post['hooks'].keys()
                    for hook in hooks:
                        for hooky in post['hooks'][hook]:
                            SubElement(metadata, f"dcterms:{hook}").text = hooky
                    writer = open(metadata_file, 'wt', encoding='utf-8')
                    writer.write(prettify(metadata))
                    window['-OUTPUT-'].update(f"generated metadata for {filename}\n", append=True)
    window['-OUTPUT-'].update(f"generated all metadata\n", append=True)

#wall building definition
def create_wall(target_folder=str):
    output = f"{target_folder}/wall.html"
    avatar = f"{target_folder}/profile_image/"
    backlog = f"{target_folder}/backlog"
    html_head = '''<!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>twarc-based wall</title>
      <style>
        body {
          font-family: Arial, Helvetica, sans-serif;
          font-size: 12pt;
          margin-left: auto;
          margin-right: auto;
          width: 95%;
        }
        article.tweet {
          position: relative;
          float: left;
          border: thin #eeeeee solid;
          margin: 10px;
          width: 600px;
          padding: 10px;
          display: block;
          /*height: 220px;*/
        }
        .name {
          font-weight: bold;
        }
        img.avatar {
            vertical-align: middle;
            float: left;
            margin-right: 10px;
            border-radius: 5px;
            height: 45px;
        }
        .tweet footer {
          /*position: absolute;*/
          bottom: 5px;
          left: 10px;
          font-size: smaller;
        }
        .tweet a {
          text-decoration: none;
        }
        .tweet .text {
          /*height: 130px;*/
          overflow: auto;
        }
        footer#page {
          margin-top: 15px;
          clear: both;
          width: 100%;
          text-align: center;
          font-size: 20pt;
          font-weight: heavy;
        }
        header {
          text-align: center;
          margin-bottom: 20px;
        }
        .tweet-photo, .tweet-video {
            max-width: 90%;
            padding-left: 5%;
        }
        .left {
            width: 30%;
            float: left;
            height: 100%;
            display: table-cell;
            text-align: center;
        }
        div#tweets {
            display: table-cell;
            width: 40%;
        }
        .avatar-column {
            width: 50%;
        }
      </style>
    </head>
    <body>
    '''
    html_foot = '''</div>
    </div>
    <footer id="page">
    <hr>
    <br>
    Adapted from code for wall generation at <a href="https://github.com/DocNow/twarc">twarc</a>.
    <br>
    <br>
    </footer>
    </body>
    </html>
    '''
    post_text = ""
    year = ""
    year_list = set()
    for dirpath, dirnames, filenames in os.walk(backlog):
        for filename in filenames:
            if filename.endswith(".json"):
                current_year = filename.split("-")[0]
                if current_year != year:
                    post_text = (f'{post_text}<article class="tweet" style="border:2px solid orangered;border-radius:10px">'
                                 f'<h2 style="text-align:center" id="{current_year}">{current_year}</h2><br/>'
                                 f'<a href="#tweets">return to top</a></article>')
                    year_list.add(current_year)
                    year = current_year
                filename = os.path.join(dirpath, filename)
                j = open(filename, "r")
                post = json.loads(j.read())
                post_dict = {'created_at': post['timestamp'],
                             'name': post['user']['username'],
                             'username': post['user']['username'],
                             'user_url': f"{post['platform']}: {post['user']['user_id']}",
                             "text": post['content_text'],
                             "url": f"{post['platform']}: {post['user']['user_id']}, post id {post['post_id']}"}
                current_avatar = f"{avatar}{post['user']['profile_image_url'].split('/')[-1]}"
                media_string = ""
                if "media" in post:
                    for x in post['media']:
                        if x['media_type'] == "image":
                            media_file = os.path.join(dirpath, x['filename'])
                            media_string = f'{media_string}<div><img class="tweet-photo" src="{media_file}"/></div>'
                        if x['media_type'] == "video":
                            thumbnail = os.path.join(dirpath, f"{x['filename'].split('.')[0]}_thumb.jpg")
                            media_extension = x['filename'].split(".")[-1]
                            media_file = os.path.join(dirpath, x['filename'])
                            media_string = f'{media_string}<div><img class="tweet-photo" src="{thumbnail}"/>' + f'<video class="tweet-video" controls src="{media_file}"></video></div>'
                if "shares" in post['engagement']:
                    post_dict['share_count'] = post['engagement']['shares']
                else:
                    post_dict['share_count'] = 0
                if "likes" in post['engagement']:
                    post_dict['likes'] = post['engagement']['likes']
                else:
                    post_dict['likes'] = 0
                if "links" in post['hooks'] and post['hooks']['links'] is not None:
                    for url in post['hooks']['links']:
                        a = f'<a href="{url["url"]}>{url["truncated_url"]}</a>'
                        post_dict['text'] = post_dict['text'][0:].replace(url['truncated_url'], a)
                current = f'''<article class="tweet">
                  <img class="avatar" src="{current_avatar}">
                  <a href="{post_dict['user_url']}" class="name">{post_dict['name']}</a><br>
                  <span class="username">{post_dict['username']}</span><br>
                  <br>
                  <div class="text">{post_dict['text']}</div><br>
                  {media_string}
                  <footer>
                  {post_dict['retweet_count']} {post_dict['retweet_string']}, {post_dict['favorite_count']} {post_dict['favorite_string']}<br>
                  <a href="{post_dict['url']}"><time>{post_dict['created_at']}</time></a>
                  </footer>
                </article>'''
                post_text += current
    year_list = list(year_list)
    year_list.sort()
    year_block = ""
    for item in year_list:
        year_block = f'{year_block}<a href="#{item}" style="font-size:1.5em">{item}</a><br/>'
    header = f'''<header>
        <h1>{post_dict['name']} twitter wall</h1>
        <em>Tweet formatting adapted from code for wall generation at <a href="https://github.com/DocNow/twarc">twarc</a></em>
        </header>
        <div class="parent">
        <div class="left">
            <img class="avatar-column" src="{current_avatar}"/>
            <br/>
            <div>{year_block}</div>
        </div>
       <div id="tweets">'''
    html = f"{html_head}{header}{post_text}{html_foot}"
    with open(output, "w") as w:
        w.write(html)
    w.close()

# extract exact hashtag
def split_hashtag(text_block):
    tag_list = []
    text_block = text_block.replace("\n", " ")
    my_tags = text_block.split(" ")
    for item in my_tags:
        if item.startswith("#"):
            tag_list.append(item)
    tag_list.sort()
    return tag_list

# create list of urls in a text
def split_url(text_block):
    tag_list = []
    text_block = text_block.replace("\n", " ")
    text_block = text_block.split(" ")
    for item in text_block:
        if item.startswith("http://") or item.startswith("https://") or item.startswith("www."):
            tag_list.append(item)
    return tag_list
#create list of facebook-style mentions
def split_facebook_mention(text_block):
    tag_list = []
    text_block = text_block.replace("\n", " ")
    my_tags = text_block.split("@")
    if len(my_tags) > 1:
        for item in my_tags:
            if item.startswith("["):
                item = item.split("]")[0]
                tag_list.append(item)
    tag_list.sort()
    return tag_list

def prettify(elem):
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparse = minidom.parseString(rough_string)
    return reparse.toprettyxml(indent="    ")

def create_directory(fileName):
    if not os.path.exists(os.path.dirname(fileName)):
        try:
            os.makedirs(os.path.dirname(fileName), exist_ok=True)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

def create_sha256(filename):
    sha256 = hashlib.sha256()
    blocksize = 65536
    with open(filename, 'rb') as f:
        buffer = f.read(blocksize)
        while len(buffer) > 0:
            sha256.update(buffer)
            buffer = f.read(blocksize)
    fixity = sha256.hexdigest()
    return fixity

# extract tge downloaded zip file as a first step to any processing
def extract_social_archive(source_zip=str, target_dir=str):
    if not os.path.isdir(target_dir):
        window["-OUTPUT-"].update("target for extracted files doesn't exist, extracting social media zip download\n", append=True)
        crazy = zipfile.ZipFile(source_zip)
        crazy.extractall(target_dir)
        window['-OUTPUT-'].update(f"source zip extracted to {target_dir}, moving ot next step\n", append=True)
    else:
        window['-OUTPUT-'].update("target for extracted social media zip already exists, if this is a new download either delete the old extraction or choose a different target location\n", append=True)
# make preservation structure
def create_preservation(target_folder=str):
    # create set of directories for preservation action once subfoldering is completed
    preservation_directories = set()
    # get data for progress bar
    window['-OUTPUT-'].update(f"retrieving file counts for progress bar\n", append=True)
    master_count = 0
    for dirpath, dirnames, filenames in os.walk(target_folder):
        for filename in filenames:
            if not dirpath.endswith("preservation1"):
                if not dirpath.endswith("preservation2"):
                    master_count += 1
    window['-OUTPUT-'].update(f"progress bar info compiled\n", append=True)
    current_count = 0
    # go directly to posts subdirectory
    for dirpath, dirnames, filenames in os.walk(target_folder):
        for filename in filenames:
            if not dirpath.endswith("preservation1"):
                if not dirpath.endswith("preservation2"):
                    if not filename.endswith("txt"):
                        preservation_directory = os.path.join(dirpath, "preservation1")
                        normalization_directory = os.path.join(dirpath, "preservation2")
                        filename1 = os.path.join(dirpath, filename)
                        # first copy to newly minted folder where normalization will occur
                        normalization_file = os.path.join(normalization_directory, filename)
                        create_directory(normalization_file)
                        shutil.copy2(filename1, normalization_file)
                        shutil.copystat(filename1, normalization_file)
                        # now move file to newly minted preservation1 directory
                        preservation_file = os.path.join(preservation_directory, filename)
                        create_directory(preservation_file)
                        os.rename(filename1, preservation_file)
                        window['-OUTPUT-'].update(f"{filename1} moved to normalization and preservation directories\n", append=True)
                        preservation_directories.add(normalization_directory)
                        current_count += 1
                        window['-Progress-'].update_bar(current_count, master_count)
    window['-OUTPUT-'].update(f"preservation/normalization foldering completed, moving to next steps", append=True)
    preservation_directories = list(preservation_directories)
    preservation_directories.sort()
    return preservation_directories
# select YouTube best format for lowest exchange in filesize
def ytdl_formatselector(ctx):
    formats = ctx.get('formats')[::-1]
    best_video = next(f for f in formats if f['vcodec'] != 'none' and f['acodec'] == 'none')
    audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
    best_audio = next(f for f in formats if (f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))
    yield {'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
           'ext': best_video['ext'],
           'requested_formats': [best_video, best_audio],
           'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'}

# YouTube workhorse
def youtube_handler(channel_name=str, options_set=list, startdate=str, enddate=str, comments=bool, target=str):
    window['-OUTPUT-'].update("starting yt-dlt download and json aggregation process, \nyou will not see progress information until it is complete\n", append=True)
    upload_list = set()
    id_list = []
    create_directory(f"{target}/youtube.txt")
    a = open(f"{target}/youtube.txt", "a")
    a.close()
    with open(f"{target}/youtube.txt", "r") as r:
        for line in r:
            line = line[:-1]
            id_list.append(line)
    r.close()
    if startdate == "YYYY-MM-DD":
        startdate = ""
    if enddate == "YYYY-MM-DD":
        enddate = ""
    if startdate != "" and enddate != "":
        startdate = startdate.replace("-", "")
        enddate = enddate.replace("-", "")
        try:
            startdate_number = int(startdate)
            startdate_number - int(enddate)
        except:
            window['-OUTPUT-'].update("A non-numeric date was entered for date range, removing this limitation\n", append=True)
            startdate = ""
            enddate = ""
    channel_name = channel_name.replace("example: ", "")
    ydl_opts = {'writeinfojson': True,
                'writesubtitles': True,
                'subtitlesformat': 'vtt',
                'getcomments': False,
                'write-description': True,
                'format': ytdl_formatselector,
                'download_archive': f"{target}/youtube.txt",
                'ignoreerrors': True}
    if comments is True:
        ydl_opts['getcomments'] = True
    if startdate != "" and enddate != "":
        ydl_opts['daterange'] = yt_dlp.utils.DateRange(str(startdate), str(enddate))
    output_template = {'chapter': '%(title)s - %(section_number)03d %(section_title)s [%(id)s].%(ext)s'}
    for option in options_set:
        if "playlist" in option:
            option = option.replace("playlists=", "").replace("\n", "").replace(" ", "")
            urls = []
            urls.append(option)
            output_template['default'] = f'{target}/playlists/%(playlist)s/%(upload_date)s_%(id)s/%(upload_date)s_%(id)s_%(title)s.%(ext)s'
            ydl_opts['outtmpl'] = output_template
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(urls)
        else:
            urls = [f'{channel_name}/{option}']
            create_directory(f'{target}/{option}/youtube.txt')
            output_template['default'] = f'{target}/{option}/%(upload_date)s_%(id)s/%(upload_date)s_%(id)s_%(title)s.%(ext)s'
            if option == "podcasts" or option == "shorts":
                output_template['default'] = f'{target}/{option}/%(playlist)s/%(upload_date)s_%(id)s/%(upload_date)s_%(id)s_%(title)s.%(ext)s'
            ydl_opts['outtmpl'] = output_template
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(urls)
    # gather list of new videos for preservation/upload action
    id_list2 = []
    with open(f"{target}/youtube.txt", "r") as r:
        for line in r:
            line = line[:-1]
            if line not in id_list:
                line = line.split(" ")[-1]
                id_list2.append(line)
    # get directories with  applicable video ids
    filename_list = []
    for dirpath, dirnames, filenames in os.walk(target):
        for filename in filenames:
            if filename.endswith("json"):
                filename = os.path.join(dirpath, filename)
                filename_list.append(filename)

    for item in filename_list:
        if filename.endswith(".info.json"):
            os.rename(item, f"{item[:-9]}json")
    for dirpath, dirnames, filenames in os.walk(target):
        for filename in filenames:
            best_dir = dirpath.split("/")[-1].split("\\")[-1]
            for item in id_list2:
                if item in best_dir:
                    upload_list.add(dirpath)
            # harvest down a thumbnail if possible while we are here
            video_formats = ['m4a', 'mhtml', 'mp4', 'webm', 'mkv']
            if filename.endswith(".json"):
                filename = os.path.join(dirpath, filename)
                filename_list.append(filename)
                with open(filename, "r", encoding='utf-8') as r:
                    filedata = r.read()
                    json_data = json.loads(filedata)
                    if "thumbnail" in json_data.keys():
                        thumbnail_name = f"{filename[:-5]}_thumbnail.jpg"
                        if not os.path.isfile(thumbnail_name):
                            my_thumbnail = requests.get(json_data['thumbnail'], stream=True)
                            if my_thumbnail.status_code == 200:
                                with open(thumbnail_name, 'wb') as f:
                                    for chunk in my_thumbnail.iter_content(1024):
                                        f.write(chunk)
                                f.close()
                    elif "thumbnails" in json_data.keys():
                        thumbnail_name = f"{filename[:-5]}_thumbnail"
                        counter = len(json_data['thumbnails'])
                        status = 0
                        if not os.path.isfile(thumbnail_name):
                            while status != 200:
                                for thumbnail in reversed(json_data['thumbnails']):
                                    if status != 200:
                                        my_thumbnail = requests.get(thumbnail['url'], stream=True)
                                        if my_thumbnail.status_code == 200:
                                            counter = counter - 1
                                            with open(f"{thumbnail_name}{str(counter)}.jpg", 'wb') as f:
                                                for chunk in my_thumbnail.iter_content(1024):
                                                    f.write(chunk)
                                            f.close()
                                            window['-OUTPUT-'].update(f"got thumbnail for {filename}\n", append=True)
                                            status = 200
                                window['-OUTPUT-'].update(f"failed to get thumbnail for {filename}\n", append=True)
                                status = 200

    window['-OUTPUT-'].update(f"\nfinished youtube harvest step\n", append=True)
    upload_list = list(upload_list)
    upload_list.sort()
    return upload_list

def normalize_youtube(preservation_directories=list):
    for preservation_directory in preservation_directories:
        for dirpath, dirnames, filenames in os.walk(f"{preservation_directory}"):
            for filename in filenames:
                if filename.endswith(".json"):
                    filename = os.path.join(dirpath, filename)
                    # clear any existing normalized json data by switching data types and switching back
                    normalized_json = 0
                    normalized_json = dict()
                    # set basic structure of the dictionary to ensure required elements exist
                    normalized_json = {'platform': 'youtube',
                                       'post_type': "",
                                       'post_id': "",
                                       'timestamp': 0,
                                       'content_text': "",
                                       'user': {'username': "",
                                                'userid': ""},
                                       'hooks': {'hashtags': list(),
                                                 'mentions': list()},
                                       'engagement': {'likes': int(),
                                                      'favorites': int(),
                                                      'shares': int()},
                                       'relationships': list()}
                    # begin processing the existing post
                    with open(filename, "r") as r:
                        json_data = r.read()
                        json_data = json.loads(json_data)
                        normalized_json['platform'] = "youtube"
                        normalized_json['post_type'] = "video"
                        normalized_json['post_id'] = json_data['id']
                        if "timestamp" in json_data.keys():
                            normalized_json['timestamp'] = json_data['timestamp']
                        elif "epoch" in json_data.keys():
                            normalized_json['timestamp'] = json_data['epoch']
                        normalized_json['content_text'] = json_data['description']
                        normalized_json['content_title'] = json_data['title']
                        normalized_json['normalization_comment'] = "For media YouTube videos and captions do not have discernible filenames, file url input instead. Full video data placed in technical information. Only best available video and intentionally requested captions harvested, all other formats listed may still reside with YouTube. Data for automatic captions not preserved as this is system-generated without user intervention."
                        normalized_json['media'] = []
                        if "formats" in json_data.keys():
                            for item in json_data['formats']:
                                # clear the media dictionary by replacing with a string in case the json processor tries to cling to prior data
                                media_dict = "some_string"
                                media_dict = {}
                                media_dict['media_type'] = "audiovisual"
                                media_dict['mimetype'] = f"video/{item['video_ext']}"
                                if item['resolution'] == "audio only":
                                    media_dict['media_type'] = "audio"
                                    media_dict['mimetype'] = f"audio/{item['audio_ext']}"
                                media_dict['file_url'] = item['url']
                                media_dict['description'] = f"format note: {item['format']}."
                                if "filesize" in item.keys():
                                    media_dict['filesize'] = item['filesize']
                                media_dict['dates'] = {}
                                media_dict['dates']['created'] = ""
                                media_dict['dates']['uploaded'] = ""
                                media_dict['technical'] = item
                                normalized_json['media'].append(media_dict)
                        if "thumbnails" in json_data.keys():
                            for item in json_data['thumbnails']:
                                media_dict = "some_string"
                                media_dict = {}
                                media_dict['media_type'] = "thumbnail"
                                media_dict['filename'] = item['url'].split("/")[-1]
                                media_dict['mimetype'] = f"image/{media_dict['filename'].split('.')[-1]}"
                                media_dict['file_url'] = item['url']
                                media_dict['technical'] = {}
                                if "preference" in item.keys():
                                    media_dict['technical']['preference'] = item['preference']
                                if "id" in item.keys():
                                    media_dict['technical']['id'] = item['id']
                                normalized_json['media'].append(media_dict)
                        if "subtitles" in json_data.keys():
                            captions = json_data['subtitles'].keys()
                            for caption in captions:
                                caption_name = caption
                                for item in json_data['subtitles'][caption]:
                                    media_dict = "some_string"
                                    media_dict = {}
                                    media_dict['media_type'] = 'caption'
                                    media_dict['mimetype'] = f"caption/{item['ext']}"
                                    media_dict['filename'] = item['url']
                                    media_dict['file_url'] = item['url']
                                    media_dict['description'] = f"Caption in format {item['ext']} for {item['name']} language with language code {caption_name}."
                                    normalized_json['media'].append(media_dict)
                        normalized_json['user']['username'] = json_data['channel']
                        normalized_json['user']['userid'] = json_data['uploader_id']
                        hashlist = set()
                        if "#" in json_data['title']:
                            titliest = json_data['title'].split(" ")
                            for item in titliest:
                                if "#" in item:
                                    hashlist.add(item.split("#")[-1])
                        if "#" in json_data['description']:
                            titliest = json_data['description'].split(" ")
                            for item in titliest:
                                if "#" in item:
                                    hashlist.add(item.split("#")[-1])
                        hashlist = list(hashlist)
                        hashlist.sort()
                        normalized_json['hooks']['hashtags'] = hashlist
                        mentionlist = set()
                        if "@" in json_data['title']:
                            titliest = json_data['title'].split(" ")
                            for item in titliest:
                                if "@" in item:
                                    mentionlist.add(item.split("@")[-1])
                        if "@" in json_data['description']:
                            titliest = json_data['description'].split(" ")
                            for item in titliest:
                                if "@" in item:
                                    mentionlist.add(item.split("@")[-1])
                        mentionlist = list(mentionlist)
                        mentionlist.sort()
                        normalized_json['hooks']['mentions'] = mentionlist
                        normalized_json['hooks']['tags'] = json_data['tags']
                        if "like_count" in json_data.keys():
                            normalized_json['engagement']['likes'] = json_data['like_count']
                        if "view_count" in json_data.keys():
                            normalized_json['engagement']['views'] = json_data['view_count']
                        if "comment_count" in json_data.keys():
                            normalized_json['engagement']['comments'] = json_data['comment_count']
                    with open(filename, "w") as w:
                        json.dump(normalized_json, w)
                    w.close()
                    window['-OUTPUT-'].update(f"normalized json for {filename}\n", append=True)

def normalize_youtube_activityStream(preservation_directories=list):
    #create counter to help with tracking progress
    window['-OUTPUT-'].update("getting count for things to normalize for progress bar\n", append=True)
    master_count = 0
    for preservation_directory in preservation_directories:
        for dirpath, dirnames, filenames in os.walk(preservation_directory):
            for filename in filenames:
                if filename.endswith(".json"):
                    master_count += 1
    current_count = 0
    video_formats = ['m4a', 'mhtml', 'mp4', 'webm', 'mkv']
    playlist_directory = {}
    playlist_item_listing = {}
    for preservation_directory in preservation_directories:
        for dirpath, dirnames, filenames in os.walk(f"{preservation_directory}"):
            for filename in filenames:
                if filename.endswith(".json"):
                    filename1 = filename
                    filename = os.path.join(dirpath, filename)
                    window['-OUTPUT-'].update(f"Working on {filename}\n", append=True)
                    print(filename)
                    # clear any existing normalized json data by switching data types and switching back
                    normalized_json = 0
                    normalized_json = {}
                    with open(filename, 'r') as r:
                        filedata = r.read()
                        json_data = json.loads(filedata)
                        normalized_json['@context'] = ["https://www.w3.org/ns/activitystreams", {"youtube": 'https:///www.youtube.com'}]
                        normalized_json['context'] = "YouTube"
                        normalized_json['id'] = json_data['id']
                        normalized_json['name'] = json_data['title']
                        normalized_json['content'] = json_data['description']
                        text_block = f"{normalized_json['name']} {normalized_json['content']}"
                        normalized_json['actor'] = []
                        normalized_json['engagement'] = []
                        if "view_count" in json_data.keys():
                            normalized_json['engagement'].append({'type': 'Views', 'count': json_data['view_count']})
                        if "channel_follower_count" in json_data.keys():
                            normalized_json['engagement'].append({'type': 'Followers', 'count': json_data['channel_follower_count']})
                        if "comment_count" in json_data.keys():
                            normalized_json['engagement'].append({'type': 'Comments', 'count': json_data['comment_count']})
                        normalized_json['type'] = "Note"
                        normalized_json['actor'].append({'type': "YouTube Account",
                                                'id': json_data['uploader_id'],
                                                'name': json_data['uploader'],
                                                'url': json_data['channel_url']})
                        if '"_type": "playlist"' in filedata:
                            playlist_directory[json_data['title']] = filename
                            normalized_json['name'] = f"Playlist: {normalized_json['name']}"
                            normalized_json['type'] = "Collection"
                            if "modified_date" in json_data.keys():
                                normalized_json['updated'] = f"{json_data['modified_date'][:4]}-{json_data['modified_date'][4:6]}-{json_data['modified_date'][6:8]}"
                            normalized_json['url'] = json_data['webpage_url']
                            if "thumbnails" in json_data.keys():
                                root_thumbnail_name = f"{filename[:-5]}_thumbnail"
                                for item in json_data['thumbnails']:
                                    thumbnail_name = f"{root_thumbnail_name}{item['id']}.jpg"
                                    if os.path.isfile(thumbnail_name):
                                        normalized_json['preview'] = {'type': "Image", "name": "Thumbnail", "href": thumbnail_name.split('/')[-1], "mediaType": "image/jpg", "height": item['height'], "width": item['width']}
                            normalized_json['totalItems'] = json_data['playlist_count']
                        if '"_type": "video"' in filedata:
                            normalized_json['engagement'].append({'type': "Likes", 'count': json_data['like_count']})
                            if "attachments" not in normalized_json.keys():
                                normalized_json['attachments'] = []
                            mini_dict = {'type': "Video"}
                            mini_dict['mediaType'] = f"video/{json_data['ext']}"
                            base_filename = filename[:-4]
                            if os.path.isfile(f"{base_filename}{json_data['ext']}"):
                                mini_dict['url'] = f"{base_filename.split('/')[-1]}{json_data['ext']}"
                            if "url" not in mini_dict.keys():
                                mini_dict['url'] = json_data['webpage_url']
                                normalized_json['content'] = f"{normalized_json['content']}. Unable to download video for preservation."
                            if "release_timestamp" in json_data.keys():
                                normalized_json['published'] = str(datetime.datetime.fromtimestamp(json_data['release_timestamp']))
                            else:
                                normalized_json['published'] = str(datetime.datetime.fromtimestamp(json_data['timestamp']))
                            if "duration_string" in json_data.keys():
                                mini_dict["duration"] = json_data['duration_string']
                            # if the string version of video duration isn't available, try to calculate it manually
                            elif "duration" in json_data.keys():
                                duration = json_data['duration']
                                minutes = int(str(duration/60).split('.')[0])
                                seconds = duration-(minutes*60)
                                mini_dict['duration'] = f"{str(minutes)}:{str(seconds)}"
                                # in case it is longer than an hour
                                if minutes >= 60:
                                    hours = int(str(minutes/60).split('.')[0])
                                    minutes = minutes-(hours*60)
                                    mini_dict['duration'] = f"{str(hours)}:{str(minutes)}:{str(seconds)}"
                            else:
                                mini_dict['duration'] = "Unspecified"
                            if "thumbnail" in json_data.keys():
                                if os.path.isfile(f"{filename[:-5]}_thumbnail.jpg"):
                                    mini_dict['preview'] = {}
                                    my_thumbnail = json_data['thumbnail']
                                    for thumbnail in json_data['thumbnails']:
                                        if my_thumbnail == thumbnail['url']:
                                            my_thumbnail = thumbnail
                                    mini_dict['preview']['type'] = "Image"
                                    mini_dict['preview']['name'] = "Thumbnail"
                                    if "height" in my_thumbnail.keys():
                                        mini_dict['preview']['height'] = my_thumbnail['height']
                                    if "width" in my_thumbnail.keys():
                                        mini_dict['preview']['width'] = my_thumbnail['width']
                                    mini_dict['preview']['url'] = {}
                                    mini_dict['preview']['url']['href'] = f"{filename1[:-5]}_thumbnail.jpg"
                                    if len(my_thumbnail['url'].split('.')) > 1:
                                        mini_dict['preview']['url']['mediaType'] = f"image/{mini_dict['preview']['url']['href'].split('.')[-1]}"
                                    normalized_json['attachments'].append(mini_dict)
                            if "thumbnails" in json_data.keys():
                                root_thumbnail_name = f"{filename[:-5]}_thumbnail"
                                for item in json_data['thumbnails']:
                                    thumbnail_name = f"{root_thumbnail_name}{item['id']}.jpg"
                                    if os.path.isfile(thumbnail_name):
                                        normalized_json['preview'] = {'type': "Image", "name": "Thumbnail", "href": thumbnail_name.split('/')[-1], "mediaType": "image/jpg", "height": item['height'], "width": item['width']}
                            # append some playlist data to playlist_items so it can be merged into that file
                            if "playlist" in json_data.keys():
                                normalized_json['partOf'] = json_data['playlist']
                                if not json_data['playlist'] in playlist_item_listing.keys():
                                    playlist_item_listing[json_data['playlist']] = []
                                playlist_item_listing[json_data['playlist']].append({'type': "Video",
                                                                                     "name": normalized_json['name'],
                                                                                     "url": mini_dict['url'],
                                                                                     'duration': mini_dict['duration']})
                            normalized_json['youtube:live_status'] = json_data['live_status']
                            normalized_json['youtube:is_live'] = json_data['is_live']
                            normalized_json['youtube:was_live'] = json_data['was_live']
                            normalized_json['youtube:playable_in_embed'] = json_data['playable_in_embed']
                            # if subtitles not automatically generated, pull data for the subtitles that actually exist and make data an attachment
                            if json_data['subtitles'] != {}:
                                for key in json_data['subtitles'].keys():
                                    rooty = key
                                    for subtitle in json_data['subtitles'][key]:
                                        if os.path.isfile(f"{filename[:-4]}{rooty}.{subtitle['ext']}"):
                                            subtitle_dict = ""
                                            subtitle_dict = {}
                                            subtitle_dict['type'] = "subtitle"
                                            subtitle_dict['name'] = subtitle['name']
                                            subtitle_dict['url'] = f"{filename1[:-4]}{rooty}.{subtitle['ext']}"
                                            normalized_json['attachments'].append(subtitle_dict)
                        normalized_json = normalization_tags(normalized_json, text_block, 'youtube')
                        if "categories" in json_data.keys():
                            if json_data['categories'] != []:
                                if "tags" not in normalized_json.keys():
                                    normalized_json['tags'] = []
                                for category in json_data['categories']:
                                    normalized_json['tags'].append({'type': 'Category',
                                                                    'id': category,
                                                                    'name': category})
                    with open(filename, 'w') as w:
                        json.dump(normalized_json, w)
                    w.close()
                    current_count += 1
                    window['-Progress-'].update_bar(current_count, master_count)
    #loop back to add in playlist items if not already present in the normalized json data
    for item in playlist_directory.keys():
        #if both the playlist and a listing of videos are in their respective listings, proceed
        if item in playlist_item_listing.keys():
            with open(playlist_directory[item], "r") as r:
                filedata = r.read()
                json_data = json.loads(filedata)
                if "items" not in json_data.keys():
                    json_data['items'] = []
                for my_video in playlist_item_listing[item]:
                    if my_video not in json_data["items"]:
                        json_data['items'].append(my_video)
                with open(playlist_directory[item], 'w') as w:
                    json.dump(json_data, w)
                w.close()
    window['-OUTPUT-'].update(f"finished normalizing youtube content\n", append=True)


def normalize_twitter(preservation_directories=list):
    for preservation_directory in preservation_directories:
        for dirpath, dirnames, filenames in os.walk(f"{preservation_directory}/preservation2"):
            for filename in filenames:
                if filename.endswith(".json"):
                    filename = os.path.join(dirpath, filename)
                    # clear any existing normalized json data by switching data types and switching back
                    normalized_json = 0
                    normalized_json = dict()
                    # set basic structure of the dictionary to ensure required elements exist
                    normalized_json = {'platform': 'twitter',
                                       'post_id': "",
                                       'timestamp': "",
                                       'content_text': "",
                                       'user': {'username': "",
                                                'userid': ""},
                                       'hooks': {'hashtags': list(),
                                                 'mentions': list()},
                                       'engagement': {'likes': int(),
                                                      'favorites': int(),
                                                      'shares': int()},
                                       'relationships': list()}
                    # begin processing the existing post
                    with open(filename, "r") as r:
                        json_data = r.read()
                        json_data = json.loads(json_data)
                        normalized_json['platform'] = "twitter"
                        normalized_json['post_type'] = "post"
                        normalized_json['post_id'] = json_data['id_str']
                        normalized_json['timestamp'] = json_data['created_at']
                        normalized_json['content_text'] = json_data['full_text']
                        normalized_json['user']['username'] = json_data['user']['screen_name']
                        normalized_json['user']['userid'] = json_data['user']['id_str']
                        user_time = json_data['user']['created_at']
                        if "." in user_time:
                            my_time = user_time.split(".")[:-1]
                            user_time = my_time.replace(f".{my_time}", "")
                            user_time = datetime.datetime.strptime(user_time, "%Y-%m-%dT%H:%M:%S")
                            user_time = datetime.datetime.strftime(user_time, "%a %b %d $H:%M%S +0000 %Y")
                            normalized_json['user']['account_created'] = user_time
                        if "location" in json_data['user'].keys():
                            normalized_json['user']['geolocation'] = json_data['user']['location']
                        if "geo" in json_data:
                            if isinstance(json_data['geo'], dict):
                                if json_data['geo']['type'] == "Point":
                                    normalized_json['geolocation'] = {'latitude': json_data['geo']['coordinates'][0],
                                                                      'longitude': json_data['geo']['coordinates'][1]}
                        if "extended_entities" in json_data.keys():
                            if "media" in json_data['extended_entities'].keys():
                                normalized_json['media'] = list()
                                for media in json_data['extended_entities']['media']:
                                    mini_dict = 0
                                    mini_dict = {'media_type': media['type'],
                                                 'mimetype': f"{media['type']}/{media['media_url_https'].split('.')[-1]}",
                                                 'filename': media['media_url_https'].split("/")[-1],
                                                 'file_url': media['media_url'],
                                                 'description': "",
                                                 'filesize': "",
                                                 'dates': {'created': "",
                                                           'uploaded': ""},
                                                 'geolocation': {'latitude': "",
                                                                 'longitude': ""},
                                                 'technical': dict()}
                                    # populate technical data section if the data points are there
                                    if "sizes" in media:
                                        mini_dict['technical']['sizes'] = dict()
                                        for key in media['sizes'].keys():
                                            mini_dict['technical']['sizes'][key] = media['sizes'][key]
                                    if "additional_media_info" in media:
                                        mini_dict['technical']['additional_media_info'] = dict()
                                        for key in media['additional_media_info'].keys():
                                            mini_dict['technical']['additional_media_info'][key] = media['additional_media_info'][key]
                                    if "video_info" in media:
                                        mini_dict['technical']['video_info'] = dict()
                                        for key in media['video_info'].keys():
                                            mini_dict['technical']['video_info'][key] = media['video_info'][key]
                                        mini_dict['technical'] = media['sizes']
                                    normalized_json['media'].append(mini_dict)
                        if "hashtags" in json_data['entities']:
                            for hashtag in json_data['entities']['hashtags']:
                                normalized_json['hooks']['hashtags'].append(hashtag['text'])
                        if 'user_mentions' in json_data['entities']:
                            for mention in json_data['entities']['user_mentions']:
                                normalized_json['hooks']['mentions'].append(mention['screen_name'])
                        if "symbols" in json_data['entities']:
                            normalized_json['hooks']['symbols'] = list()
                            for symbol in json_data['entities']['symbols']:
                                normalized_json['hooks']['symbols'].append(symbol['text'])
                        if "urls" in json_data['entities']:
                            normalized_json['hooks']['links'] = list()
                            for url in json_data['entities']['urls']:
                                normalized_json['hooks']['links'].append(url['expanded_url'])
                        normalized_json['engagement']['favorites'] = json_data['favorite_count']
                        normalized_json['engagement']['retweet_count'] = json_data['retweet_count']
                        if "in_reply_to_screen_name" in json_data:
                            if isinstance(json_data['in_reply_to_screen_name'], str):
                                normalized_json['relationships'].append({'post_id': json_data['in_reply_to_statusId'],
                                                                         'username': json_data['in_reply_to_screen_name'],
                                                                         'relationship_type': 'reply'})
                    with open(filename, "w") as w:
                        json.dump(normalized_json, w)
                    w.close()
                    window['-OUTPUT-'].update(f"normalized json for {filename}\n", append=True)

def normalize_twitter_activitystream(preservation_directories=list):
    window['-OUTPUT-'].update("getting count for thing to normalize for progress bar\n", append=True)
    master_count = 0
    for preservation_directory in preservation_directories:
        for dirpath, dirnames, filenames in os.walk(preservation_directory):
            for filename in filenames:
                if filename.endswith("json"):
                    master_count += 1
    current_count = 0
    #now iterate over the fileset
    for preservation_directory in preservation_directories:
        for dirpath, dirnames, filenames in os.walk(f"{preservation_directory}"):
            for filename in filenames:
                if filename.endswith("json"):
                    filename1 = filename
                    filename = os.path.join(dirpath, filename)
                    window['-OUTPUT-'].update(f"Working on {filename}\n", append=True)
                    print(filename)
                    # reset/clear out anything lingering in the machine for last json being handled
                    normalized_json = 0
                    normalized_json = {}
                    with open(filename, "r") as r:
                        filedata = r.read()
                        json_data = json.loads(filedata)
                        normalized_json['@context'] = ["https://www.w3.org/ns/activitystreams",
                                                      {"twitter": 'https:///www.twitter.com'}]
                        normalized_json['context'] = "Twitter"
                        normalized_json['id'] = json_data['id_str']
                        normalized_json['content'] = json_data['full_text']
                        normalized_json['type'] = "Note"
                        normalized_json['actor'] = []
                        normalized_json['published'] = datetime.datetime.strptime(json_data['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%dT%H:%M:%SZ')
                        normalized_json['twitter:retweeted'] = json_data['retweeted']
                        normalized_json['actor'].append({'type': 'twitter',
                                                         'id': json_data['user']['id_str'],
                                                         'name': json_data['user']['name'],
                                                         'url': f"https://www.twitter.com/{json_data['user']['screen_name']}",
                                                         'twitter:created_at': json_data['user']['created_at'],
                                                         'location': json_data['user']['location'],
                                                         'twitter:profile_image_url': json_data['user']['profile_image_url'],
                                                         'twitter:profile_banner_url': json_data['user']['profile_banner_url']})
                        normalized_json['engagement'] = []
                        if "retweet_count" in json_data.keys():
                            normalized_json['engagement'].append({"type": "Share", "count": json_data['retweet_count']})
                        if "favorite_count" in json_data.keys():
                            normalized_json['engagement'].append({'type': 'Favorite', 'count': json_data['favorite_count']})
                        content_text = ""
                        content_text = f"{content_text} {normalized_json['content']}"
                        if json_data["in_reply_to_status_id"] is not None:
                            normalized_json['inReplyTo'] = {'type': 'Note',
                                                            'href': json_data['in_reply_to_status_id_str'],
                                                            'Actor': [{'type': 'twitter',
                                                                       'id': json_data['in_reply_to_user_id_str'],
                                                                       'name': json_data['in_reply_to_screen_name'],
                                                                       'url': f"https://www.twitter.com/{json_data['in_reply_to_screen_name']}"}]}
                        if "source" in json_data.keys():
                            normalized_json['origin'] = {'type': "Application", "name": json_data['source']}
                        if json_data['geo'] is not None:
                            normalized_json['location'] = {"type": json_data['geo']['type']}
                            if "coordinates" in json_data['geo'].keys():
                                normalized_json['location']['latitude'] = json_data['geo']['coordinates'][1]
                                normalized_json['location']['longitude'] = json_data['geo']['coordinates'][0]
                        if json_data['place'] is not None:
                            if "location" not in normalized_json.keys():
                                normalized_json['location'] = dict()
                            normalized_json['location']['type'] = json_data['place']['place_type']
                            normalized_json['location']['name'] = json_data['place']['full_name']
                            normalized_json['location']['twitter:country_code'] = json_data['place']['country_code']
                            normalized_json['location']['twitter:id'] = json_data['place']['id']
                        normalized_json['tags'] = []
                        if json_data['entities']['hashtags'] != []:
                            for hashtag in json_data['entities']['hashtags']:
                                normalized_json['tags'].append({'type': 'Hashtag',
                                                                'name': f"#{hashtag['text']}",
                                                                'id': f"https://www.twitter.com/hashtag/{hashtag['text']}"})
                        if json_data['entities']['symbols'] != []:
                            for symbol in json_data['entities']['symbols']:
                                normalized_json['tags'].append({'type': 'Symbol',
                                                                'name': symbol['text'],
                                                                'id': symbol['text']})
                        if json_data['entities']['user_mentions'] != []:
                            for mention in json_data['entities']['user_mentions']:
                                normalized_json['tags'].append({'type': "Mention",
                                                                'name': mention['name'],
                                                                'id': f"https//www.twitter.com/{mention['screen_name']}",
                                                                "twitter:id": mention['id_str']})
                        if json_data['entities']['urls'] != []:
                            for url in json_data['entities']['urls']:
                                normalized_json['tags'].append({'type': "Link",
                                                                "href": url['expanded_url'],
                                                                'mediaType': 'text/html'})
                        if "media" in json_data['entities'].keys():
                            # insert media handler here
                            media_set = json_data['extended_entities']['media']
                            if "Attachments" not in normalized_json.keys():
                                normalized_json['Attachments'] = []
                            for current_media in media_set:
                                # clear prior mini_dict in case something is lingering
                                mini_dict = ""
                                mini_dict = {}
                                if current_media['type'] == "photo":
                                    mini_dict['type'] = "Image"
                                    mini_dict['uri'] = f"{json_data['id_str']}-{current_media['media_url'].split('/')[-1]}"
                                    mini_dict['mediaType'] = f"image/{mini_dict['uri'].split('.')[-1]}"
                                    mini_dict['id'] = current_media['id_str']
                                    normalized_json['Attachments'].append(mini_dict)
                                if current_media['type'] == "video":
                                    preview = ""
                                    preview = {
                                        'type': "Image",
                                        'name': "Thumbnail",
                                        'url': {
                                            'href': current_media['media_url'].split('/')[-1],
                                            'mediaType': f'image/jpg'
                                        }
                                    }
                                    duration = str(current_media['video_info']['duration_millis'])
                                    hours = "00"
                                    minutes = "00"
                                    seconds = duration[:-3]
                                    miliseconds = duration[-3:]
                                    if int(seconds) >= 60:
                                        minutes = str(int(seconds)/60).split('.')[0]
                                        seconds = str(int(seconds)-(int(minutes)*60))
                                        if int(minutes) >= 60:
                                            hours = str(int(minutes)/60).split('.')[0]
                                            minutes = str(int(minutes)-(int(hours)*60))
                                    while len(seconds) < 2:
                                        seconds = f"0{seconds}"
                                    while len(minutes) < 2:
                                        minutes = f"0{minutes}"
                                    duration = f"{hours}:{minutes}:{seconds}.{miliseconds}"
                                    if hours == "00":
                                        duration = duration.replace("00:", "")
                                    for variant in current_media['video_info']['variants']:
                                        mini_dict = ""
                                        mini_dict = {}
                                        if os.path.isfile(f"{dirpath}/{json_data['id_str']}-{variant['url'].split('/')[-1]}"):
                                            if variant['content_type'].startswith("video"):
                                                mini_dict['type'] = "Video"
                                                mini_dict['id'] = current_media['id_str']
                                                mini_dict['mediaType'] = variant['content_type']
                                                mini_dict['url'] = f"{json_data['id_str']}-{variant['url'].split('/')[-1]}"
                                                if "bitrate" in variant.keys():
                                                    mini_dict['twitter:bitrate'] = variant['bitrate']
                                                if "aspect_ratio" in current_media.keys():
                                                    mini_dict['twitter:width'] = current_media['aspect_ratio'][0]
                                                    mini_dict['twitter:height'] = current_media['aspect_ratio'][1]
                                                mini_dict['preview'] = preview
                                                try:
                                                    mini_dict['width'] = int(variant['url'].split('/')[-2].split('x')[0])
                                                    mini_dict['height'] = int(variant['url'].split('/')[-2].split('x')[-1])
                                                except:
                                                    continue
                                            else:
                                                mini_dict['type'] = variant['content_type'].split('/')[0].capitalize()
                                                mini_dict['id'] = current_media['id_str']
                                                mini_dict['mediaType'] = variant['content_type']
                                                mini_dict['url'] = variant['url'].split('/')[-1]
                                        if mini_dict != {}:
                                            normalized_json['Attachments'].append(mini_dict)
                                if current_media['type'] == "animated_gif":
                                    preview = ""
                                    preview = {
                                        'type': "Image",
                                        'name': "Thumbnail",
                                        'url': {
                                            'href': current_media['media_url'].split('/')[-1],
                                            'mediaType': f'image/jpg'
                                        }
                                    }
                                    mini_dict['twitter:type'] = current_media['type']
                                    mini_dict['type'] = "Video"
                                    mini_dict['id'] = current_media['id_str']
                                    mini_dict['media_type'] = current_media['video_info']['variants'][0]['content_type']
                                    mini_dict['url'] = current_media['video_info']['variants'][0]['url'].split("/")[-1]
                                    if "bitrate" in current_media['video_info']['variants'][0].keys():
                                        mini_dict['twitter:bitrate'] = current_media['video_info']['variants'][0]['bitrate']
                                    mini_dict['preview'] = preview
                                    normalized_json['Attachments'].append(mini_dict)
                        normalized_json = normalization_tags(normalized_json, content_text, "twitter")

                        with open(filename, 'w') as w:
                            json.dump(normalized_json, w)
                        w.close()
                        current_count += 1
                        window['-OUTPUT-'].update(f"processed {filename}\n", append=True)
                        window['-Progress-'].update_bar(current_count, master_count)
    window['-OUTPUT-'].update(f"finished normalizing twitter content\n", append=True)
    print("finished twitter normalization")
                                    # twitter correspondence handler
def twitter_correspondence(source_folder=str, target_folder=str):
    direct_mesage_file = f"{source_folder}/data/direct-messages.js"
    with open(direct_mesage_file, "r") as r:
        json_data = r.read()
        json_data = json_data.replace('window.YTD.direct-messages.part0 = [\n ', '').replace('\n]', '')
        json_data = json.loads(json_data)
        for direct_message in json_data:
            key_data = direct_message['dmConversation']['messages'][-1]
            message_date = key_data['createdAt'][:10]
            conversation_id = direct_message['dmConversation']['conversationId']
            message_name = f"{message_date}_{conversation_id}"
            message_filename = f"{target_folder}/correspondence/{message_date[:4]}/{message_name}/{message_name}.json"
            create_directory(message_filename)
            with open(message_filename, "w") as w:
                json.dump(direct_message, w)
            w.close()
            window['-OUTPUT-'].update(f"processed direct message {message_name}\n", append=True)
    r.close()

# get media directly from online instead of from twitter archive
def tweet_media_handler(url, filename, profile_media_directory):
    # make sure target directory exists
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    # try to locate the file in the extracted profile media and copy over
    for dirpath, dirnames, filenames in os.walk(profile_media_directory):
        for my_filename in filenames:
            if filename.split("/")[-1].split("\\")[-1].split(".")[0] in my_filename:
                my_filename = os.path.join(dirpath, my_filename)
                shutil.copy2(my_filename, filename)
                shutil.copystat(my_filename, filename)
                window['-OUTPUT-'].update(f"pulled {filename} from {my_filename}\n", append=True)
    # do file exist check and if profile media wasn't found for some reason, try to harvest it from the website instead
    if not os.path.isfile(filename):
        tweet_media = requests.get(url, stream=True)
        if tweet_media.status_code == 200:
            filename = filename.replace('?', '')
            with open(filename, 'wb') as f:
                for chunk in tweet_media.iter_content(1024):
                    f.write(chunk)
            f.close()
            window['-OUTPUT-'].update(f"pulled {filename} from twitter servers as not in folder\n", append=True)

# workhorse to tweets
def tweet_handler(source_folder, target_folder):
    upload_list = set()
    my_precious = f'{source_folder}/data/tweet.js'
    my_data = f'{source_folder}/data'
    if os.path.isfile(my_precious):
        window['-OUTPUT-'].update("twitter archive already extracted, moving on\n", append=True)
    if not os.path.isfile(my_precious):
        window['-OUTPUT-'].update("extracting twitter archive for manipulation...go get a drink this will take some time\n", append=True)
        crazy = zipfile.ZipFile(target_file)
        crazy.extractall(source_folder)
    window['-OUTPUT-'].update("processing tweets...\n", append=True)
    window['-OUTPUT-'].update("Go get a cup of coffee, you deserve it and this may take a while\n", append=True)
    valuables = {}
    valuables['source_dir'] = my_data
    valuables['base_location'] = target_folder
    log = open(f"logger.txt", 'a')
    id_list = []
    baseline = f"{valuables['base_location']}/"
    tweet_log = f"{baseline}/log_tweetIDs.txt"
    if not os.path.isfile(tweet_log):
        create_directory(tweet_log)
        with open(tweet_log, "a") as w:
            window['-OUTPUT-'].update(f"Generated directory for {tweet_log}\n", append=True)
    with open(tweet_log, 'r') as r:
        for line in r:
            line = line[:-1]
            id_list.append(line)
    r.close()
    window['-OUTPUT-'].update("list of existing tweets compiled\n", append=True)
    id_list2 = []
    #load account information for insertion into tweet json
    with open(f"{valuables['source_dir']}/account.js", "r") as data:
        json_data = data.read()
        json_data = json_data.replace('window.YTD.account.part0 = [\n ', '').replace('\n]', '')
        user = json.loads(json_data)
        user_data = dict()
        user_data['id'] = int(user['account']['accountId'])
        user_data['id_str'] = user['account']['accountId']
        user_data['name'] = user['account']['accountDisplayName']
        user_data['screen_name'] = user['account']['username']
        user_data['created_at'] = user['account']['createdAt']
    window['-OUTPUT-'].update(f"account user data loaded, getting profile information\n", append=True)
    with open(f"{valuables['source_dir']}/profile.js", "r") as data:
        json_data = data.read()
        json_data = json_data.replace('window.YTD.profile.part0 = [\n ', '').replace('\n]', '')
        user = json.loads(json_data)
        user_data['location'] = user['profile']['description']['location']
        user_data['description'] = user['profile']['description']['bio']
        user_data['url'] = user['profile']['description']['website']
        user_data['profile_image_url'] = user['profile']['avatarMediaUrl']
        user_data['profile_image_url_https'] = user['profile']['avatarMediaUrl']
        user_data['profile_banner_url'] = user['profile']['headerMediaUrl']
    window['-OUTPUT-'].update("profile data loaded\n", append=True)
    with open(my_precious, "r", encoding="utf-8") as backlog:
        json_data = backlog.read()
        if "window.YTD.tweet.part0 = " in json_data:
            json_data = json_data.replace("window.YTD.tweet.part0 = ", "")
        twitter = json.loads(json_data)
        counter = 0
        for tweet in twitter:
            total = len(twitter)
            counter += 1
            window['-OUTPUT-'].update(f"processing {counter}/{total}\n", append=True)
            window['-Progress-'].update_bar(counter, total)
            # denesting the tweet now
            tweet = tweet['tweet']
            tweet_date = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d')
            if "+" not in tweet['created_at']:
                tweet['created_at'] = f"{tweet['created_at'][:-4]} +0000 {tweet['created_at'][-4:]}"
            if str(tweet['id']) not in id_list:
                filename = f"{str(tweet_date)}_{str(tweet['id_str'])}.txt"
                filepath1 = f"{baseline}/backlog/{str(tweet_date[:4])}/{str(tweet_date)}_{str(tweet['id_str'])}/"
                filepath = f"{filepath1}{filename}"
                upload_list.add(filepath1)
                create_directory(filepath)
                tweet['user'] = user_data
                # make changes to the json to have it comply with current individual api standards and be standalone
                # make key items integers instead of text
                tweet['id'] = int(tweet['id'])
                if 'quoted_status' in tweet:
                    tweet['quoted_status']['id'] = int(tweet['quoted_status']['id'])
                if 'hashtags' in tweet['entities']:
                    for item in tweet['entities']['hashtags']:
                        item['indices'][0] = int(item['indices'][0])
                        item['indices'][1] = int(item['indices'][1])
                if 'symbols' in tweet['entities']:
                    for item in tweet['entities']['symbols']:
                        item['indices'][0] = int(item['indices'][0])
                        item['indices'][1] = int(item['indices'][1])
                        item['id'] = int(item['id'])
                if 'user_mentions' in tweet['entities']:
                    for item in tweet['entities']['user_mentions']:
                        item['indices'][0] = int(item['indices'][0])
                        item['indices'][1] = int(item['indices'][1])
                        item['id'] = int(item['id'])
                if 'urls' in tweet['entities']:
                    for item in tweet['entities']['urls']:
                        item['indices'][0] = int(item['indices'][0])
                        item['indices'][1] = int(item['indices'][1])
                if 'quoted_status_id' in tweet:
                    tweet['quoted_status_id'] = int(tweet['quoted_status_id'])
                if 'quoted_status' in tweet:
                    tweet['quoted_status']['id'] = int(tweet['quoted_status']['id'])
                    tweet['quoted_status']['display_text_range'][0] = int(tweet['quoted_status']['display_text_range'][0])
                    tweet['quoted_status']['display_text_range'][1] = int(tweet['quoted_status']['display_text_range'][1])
            tweet['display_text_range'][0] = int(tweet['display_text_range'][0])
            tweet['display_text_range'][1] = int(tweet['display_text_range'][1])
            if 'in_reply_to_user_id' in tweet:
                tweet['in_reply_to_user_id'] = int(tweet['in_reply_to_user_id'])
            tweet['retweet_count'] = int(tweet['retweet_count'])
            tweet['favorite_count'] = int(tweet['favorite_count'])
            # reorder the json file
            dictOrder = ['created_at', 'id', 'id_str', 'full_text', 'truncated', 'display_text_range', 'entities',
                         'extended_entities', 'source', 'in_reply_to_status_id', 'in_reply_to_status_id_str',
                         'in_reply_to_user_id', 'in_reply_to_user_id_str', 'in_reply_to_screen_name', 'user', 'geo',
                         'coordinates', 'place', 'contributors', 'is_quote_status', 'retweet_count', 'favorite_count',
                         'favorited', 'retweeted', 'possibly_sensitive', 'lang']
            existingKeys = tweet.keys()
            secondlist = []
            for k in dictOrder:
                if k in existingKeys:
                    secondlist.append(k)
                else:
                    if k != 'extended_entities':
                        tweet[k] = None
                        secondlist.append(k)
            tempDict = OrderedDict(tweet)
            for k in secondlist:
                tempDict.move_to_end(k)
            tweet = json.loads(json.dumps(tempDict))
            # create the actual tweet.json file
            window['-OUTPUT-'].update(f'creating {filepath}\n', append=True)
            with open(filepath, 'w') as output:
                json.dump(tweet, output)
            output.close()
            filepath2 = f'{filepath[:-3]}json'
            os.rename(filepath, filepath2)
            # add tweet to list of tweets processed this go-around
            id_list2.append(str(tweet['id_str']))
            # get banner image for backlog depository to ensure everything is there
            profile_image = f"{tweet['user']['id_str']}-{tweet['user']['profile_image_url_https'].split('/')[-1]}"
            profile_image_filename = f"{baseline}profile_image/{profile_image}"
            profile_image_url = tweet['user']['profile_image_url_https']
            user_image_set = []
            if not os.path.isfile(profile_image_filename):
                tweet_media_handler(profile_image_url, profile_image_filename, f"{valuables['source_dir']}/profile_media")
            profile_banner_filename = f"{baseline}profile_banner/{tweet['user']['id_str']}-{tweet['user']['profile_banner_url'].split('/')[-1]}.jpg"
            profile_banner_url = tweet['user']['profile_image_url_https']
            if not os.path.isfile(profile_banner_filename):
                tweet_media_handler(profile_banner_url, profile_banner_filename, f"{valuables['source_dir']}/profile_media")
            # download the media files
            images = []
            if 'extended_entities' in tweet and tweet['extended_entities'] is not None and 'media' in tweet['extended_entities']:
                for media in tweet['extended_entities']['media']:
                    id = media['id_str']
                    # handle video first because of the structure
                    if "video_info" in media.keys():
                        bitrate = 0
                        # set variable to download only the largest video copy and overwrite anything downloaded up to then
                        for v in media['video_info']['variants']:
                            if 'bitrate' in v:
                                if int(v['bitrate']) > bitrate:
                                    bitrate = int(v['bitrate'])
                        for v in media['video_info']['variants']:
                            if 'bitrate' in v.keys():
                                if int(v['bitrate']) == bitrate:
                                    media_filename = v['url'].split('.')[-1]
                                    media_filename = media_filename.split("?")[0]
                                    media_filename = f"{filepath1}{tweet['id_str']}-{v['url'].split('/')[-1].split('?')[0]}"
                                    tweet_media_handler(v['url'], media_filename, f"{valuables['source_dir']}/tweet_media")
                                    bitrate = int(v['bitrate'])
                        # save thumbnail image with _thumb at the end to be clear what it is
                        media_filename = f"{filepath1}{media['media_url'].split('/')[-1]}"
                        tweet_media_handler(media['media_url_https'], media_filename, f"{valuables['source_dir']}/tweet_media")
                    else:
                        media_filename = f"{filepath1}{tweet['id_str']}-{media['media_url'].split('/')[-1].split('.')[0]}.{media['media_url'].split('.')[-1]}"
                        tweet_media_handler(media['media_url_https'], media_filename, f"{valuables['source_dir']}/tweet_media")
                    # add thumbnail or downloaded image to a list so it doesn't get done twice
                    images.append(id)
            # start looking at the other location of media references in the json
            if 'media' in tweet['entities']:
                for media in tweet['entities']['media']:
                    # check list of media IDs already done to see if download needed
                    if media['id_str'] not in images:
                        if media['type'] == "photo":
                            media_filename = f"{filepath1}{media['id_str']}.{media['media_url'].split('.')[-1]}"
                            window['-OUTPUT-'].update(f"{valuables['source_dir']}/tweet_media\n", append=True)
                            tweet_media_handler(media['media_url_https'], media_filename, f"{valuables['source_dir']}/tweet_media")
    with open(f"{baseline}log_tweetIDs.txt", "a") as f:
        for item in id_list2:
            f.write(f"{item}\n")
    f.close()
    upload_list = list(upload_list)
    upload_list.sort()
    return upload_list


# facebook normalization to standardized format
def normalize_facebook(preservation_directories=list):
    print("something")

# activitystreams adapted normalization method
def normalize_facebook_activityStream(preservation_directories=list):
    #create counter to help with tracking progress
    window['-OUTPUT-'].update("getting count for things to normalize for progress bar\n", append=True)
    master_count = 0
    for preservation_directory in preservation_directories:
        for dirpath, dirnames, filenames in os.walk(preservation_directory):
            for filename in filenames:
                if filename.endswith(".json"):
                    master_count += 1
    current_count = 0
    for preservation_directory in preservation_directories:
        for dirpath, dirnames, filenames in os.walk(f"{preservation_directory}"):
            for filename in filenames:
                if filename.endswith(".json"):
                    filename = os.path.join(dirpath, filename)
                    print(filename)
                    window['-OUTPUT-'].update(f"Working on {filename}\n", append=True)
                    # clear any existing normalized json data by switching data types and switching back
                    normalized_json = 0
                    normalized_json = dict()
                    with open(filename, "r") as r:
                        filedata = r.read()
                        json_data = json.loads(filedata)
                        normalized_json['@context'] = ["https://www.w3.org/ns/activitystreams"]
                        normalized_json['context'] = "Facebook"
                        normalized_json['id'] = json_data['post_id']
                        # set default type value to Post
                        normalized_json['type'] = "Note"
                        normalized_json['actor'] = []
                        normalized_json['actor'].append({"type": "Facebook page",
                                                         "id": json_data['user']['id_str'],
                                                         "name": json_data['user']['screen_name']})
                        text_block = ""
                        if "cover_photo" in json_data.keys():
                            normalized_json['preview'] = {'type': "Image",
                                                          "name": "Cover Photo",
                                                          "url": {
                                                              "href": json_data['cover_photo']['uri'].split("/")[-1],
                                                              "mediaType": f"image/{json_data['cover_photo']['uri'].split('.')[-1]}"
                                                          }}
                        if json_data['post_type'] == "facebook_album":
                            text_block = f"{json_data['description']} {json_data['name']}"
                            normalized_json = normalization_tags(normalized_json, text_block, 'facebook')
                            normalized_json['content'] = json_data['description']
                            normalized_json['@context'].append({'dcterms': 'http://purl.org/dc/terms/',
                                                            'exif': 'http://www.w3.org/2003/12/exif/ns'})
                            normalized_json['type'] = "Collection"
                            normalized_json['summary'] = f"Facebook Album: {json_data['name']}"
                            normalized_json['updated'] = str(datetime.datetime.fromtimestamp(json_data['last_modified_timestamp']))
                            normalized_json['totalitems'] = len(json_data['photos'])
                            normalized_json['items'] = []
                            for item in json_data['photos']:
                                short_dictionary = ""
                                short_dictionary = {'type': 'Image',
                                                    'title': item['title'],
                                                    'uri': item['uri'].split("/")[-1],
                                                    'dcterms:date.created': str(datetime.datetime.fromtimestamp(item['creation_timestamp']))}
                                if len(short_dictionary['uri'].split(".")[-1]) == 3:
                                    short_dictionary['mediaType'] = f"image/{short_dictionary['uri'].split('.')[-1]}"
                                if "media_metadata" in item.keys():
                                    if "photo_metadata" in item['media_metadata'].keys():
                                        if "exif_data" in item['media_metadata']['photo_metadata'].keys():
                                            short_dictionary = facebook_mediaExif_extractor(short_dictionary, item['media_metadata']['photo_metadata']['exif_data'])
                                mini_textblock = f"{item['title']}"
                                if "description" in item.keys():
                                    short_dictionary['description'] = item['description']
                                    mini_textblock = f"{mini_textblock} {item['description']}"
                                short_dictionary = normalization_tags(short_dictionary, mini_textblock, 'facebook')
                                normalized_json['items'].append(short_dictionary)
                        if json_data['post_type'] == "facebook_event":
                            normalized_json['type'] = "Event"
                            normalized_json['@context'].append({'dcterms': 'http://purl.org/dc/terms/',
                                                                'exif': 'http://www.w3.org/2003/12/exif/ns'})
                            normalized_json['summary'] = f"Facebook event: {json_data['name']}"
                            if "create_timestamp" in json_data.keys():
                                normalized_json['published'] = str(datetime.datetime.fromtimestamp(json_data['create_timestamp']))
                            normalized_json['startTime'] = str(datetime.datetime.fromtimestamp(json_data['start_timestamp']))
                            normalized_json['endTime'] = str(datetime.datetime.fromtimestamp(json_data['end_timestamp']))
                            text_block = f"{json_data['name']}"
                            if "description" in json_data.keys():
                                text_block = f"{text_block} {json_data['description']}"
                                normalized_json['content'] = json_data['description']
                            normalized_json = normalization_tags(normalized_json, text_block, 'facebook')
                            if "place" in json_data.keys():
                                normalized_json['location'] = {'name': json_data['place']['name'],
                                                               'type': 'Place'}
                                if "coordinate" in json_data['place'].keys():
                                    normalized_json['location']['latitude'] = json_data['place']['coordinate']['latitude']
                                    normalized_json['location']['longitude'] = json_data['place']['coordinate']['longitude']
                                if "address" in json_data['place'].keys():
                                    normalized_json['location']['address'] = json_data['place']['address']
                        if json_data['post_type'] == "facebook_otherPhotos":
                            if "description" in json_data.keys():
                                text_block = f"{json_data['description']}"
                                normalized_json['content'] = json_data['description']
                            normalized_json = normalization_tags(normalized_json, text_block, 'facebook')
                            normalized_json['@context'].append({'dcterms': 'http://purl.org/dc/terms/',
                                                                'exif': 'http://www.w3.org/2003/12/exif/ns'})
                            normalized_json['published'] = str(datetime.datetime.fromtimestamp(json_data['creation_timestamp']))
                            normalized_json['summary'] = f"Facebook post: Post ID {json_data['post_id']}"
                            short_dictionary = {'type': 'Image',
                                                'uri': json_data['uri'].split('/')[-1],
                                                'dcterms:date.created': str(datetime.datetime.fromtimestamp(json_data['creation_timestamp']))}
                            if len(short_dictionary['uri'].split(".")[-1]) == 3:
                                short_dictionary['mediaType'] = f"image/{short_dictionary['uri'].split('.')[-1]}"
                            if "media_metadata" in json_data.keys():
                                if "photo_metadata" in json_data['media_metadata'].keys():
                                    if "exif_data" in json_data['media_metadata']['photo_metadata'].keys():
                                        short_dictionary = facebook_mediaExif_extractor(short_dictionary, json_data['media_metadata']['photo_metadata']['exif_data'])
                            normalized_json['attachment'] = [short_dictionary]
                        if json_data['post_type'] == "facebook_video":
                            if "description" in json_data.keys():
                                normalized_json['content'] = json_data['description']
                                text_block = f"{json_data['description']}"
                            normalized_json['@context'].append({'dcterms': 'http://purl.org/dc/terms/',
                                                                'exif': 'http://www.w3.org/2003/12/exif/ns'})
                            normalized_json['published'] = str(datetime.datetime.fromtimestamp(json_data['creation_timestamp']))
                            normalized_json['summary'] = f"Facebook post: Post ID {json_data['post_id']}"
                            normalized_json = normalization_tags(normalized_json, text_block, 'facebook')
                            if "title" in json_data.keys():
                                normalized_json['name'] = json_data['title']
                            short_dictionary = {'type': "Video",
                                                'uri': json_data['uri'].split("/")[-1],
                                                'dcterms:date.created': str(datetime.datetime.fromtimestamp(json_data['creation_timestamp']))}
                            if len(short_dictionary['uri'].split(".")[-1]) == 3:
                                short_dictionary['mediaType'] = f"video/{short_dictionary['uri'].split('.')[-1]}"
                            if "media_metadata" in json_data.keys():
                                if "video_metadata" in json_data['media_metadata'].keys():
                                    if "exif_data" in json_data['media_metadata']['video_metadata'].keys():
                                        short_dictionary = facebook_mediaExif_extractor(short_dictionary, json_data['media_metadata']['video_metadata']['exif_data'])
                            normalized_json['attachment'] = [short_dictionary]
                        if json_data['post_type'] == "facebook_post":
                            if "creation_timestamp" in json_data.keys():
                                normalized_json['published'] = str(datetime.datetime.fromtimestamp(json_data['creation_timestamp']))
                            else:
                                normalized_json['published'] = str(datetime.datetime.fromtimestamp(json_data['timestamp']))
                            normalized_json['content'] = ""
                            if "data" in json_data.keys():
                                for data_chunk in json_data['data']:
                                    if "post" in data_chunk.keys():
                                        normalized_json['content'] = data_chunk['post']
                                    if "update_timestamp" in data_chunk.keys():
                                        normalized_json['updated'] = str(datetime.datetime.fromtimestamp(data_chunk['update_timestamp']))
                            text_block = normalized_json['content']
                            if "title" in json_data.keys():
                                normalized_json['summary'] = json_data['title']
                                text_block = f"{text_block} {json_data['title']}"
                            if "attachments" in json_data.keys():
                                normalized_json['attachments'] = []
                                location_list = []
                                url_list = []
                                for attachment in json_data['attachments']:
                                    attachment_data = attachment['data']
                                    for single_attachment in attachment_data:
                                        # reset the short dictionary
                                        short_dictionary = ""
                                        short_dictionary = {}
                                        if "media" in single_attachment.keys():
                                            single_attachment = single_attachment['media']
                                            short_dictionary = {'type': 'Media',
                                                                'uri': single_attachment['uri'].split('/')[-1],
                                                                'dcterms:date.created': str(
                                                                    datetime.datetime.fromtimestamp(
                                                                        single_attachment['creation_timestamp']))}
                                            if len(short_dictionary['uri'].split(".")[-1]) == 3:
                                                short_dictionary['mediaType'] = f"media/{short_dictionary['uri'].split('.')[-1]}"
                                            else:
                                                short_dictionary['mediaType'] = "media/unknown"
                                            mini_textblock = ""
                                            if "title" in single_attachment.keys():
                                                short_dictionary['name'] = single_attachment['title']
                                                mini_textblock = f"{mini_textblock} {single_attachment['title']}"
                                            if "description" in single_attachment.keys():
                                                short_dictionary['description'] = single_attachment['description']
                                                mini_textblock = f"{mini_textblock} {single_attachment['description']}"
                                            if "media_metadata" in single_attachment.keys():
                                                if "photo_metadata" in single_attachment['media_metadata']:
                                                    short_dictionary['type'] = "Image"
                                                    short_dictionary['mediaType'] = short_dictionary['mediaType'].replace("media", "image")
                                                    short_dictionary = facebook_mediaExif_extractor(short_dictionary, single_attachment['media_metadata']['photo_metadata']['exif_data'])
                                                if "video_metadata" in single_attachment['media_metadata']:
                                                    short_dictionary['type'] = "Video"
                                                    short_dictionary['mediaType'] = short_dictionary['mediaType'].replace("media", "video")
                                                    short_dictionary = facebook_mediaExif_extractor(short_dictionary, single_attachment['media_metadata']['video_metadata']['exif_data'])
                                            short_dictionary = normalization_tags(short_dictionary, mini_textblock, 'facebook')
                                            normalized_json['attachments'].append(short_dictionary)
                                            text_block = f"{text_block} {mini_textblock}"
                                        if "place" in single_attachment.keys():
                                            single_attachment = single_attachment['place']
                                            short_dictionary = {'name': single_attachment['name'],
                                                                'type': "Place"}
                                            if "url" in single_attachment.keys():
                                                short_dictionary['url'] = single_attachment['url']
                                            if "coordinate" in single_attachment.keys():
                                                short_dictionary['latitude'] = single_attachment['coordinate']['latitude']
                                                short_dictionary['longitude'] = single_attachment['coordinate']['longitude']
                                            if "address" in single_attachment.keys():
                                                short_dictionary['address'] = single_attachment['address']
                                            location_list.append(short_dictionary)
                                        if "external_context" in single_attachment.keys():
                                            single_attachment = single_attachment['external_context']
                                            if "url" in single_attachment.keys():
                                                short_dictionary = {'type': 'Link',
                                                                    'href': single_attachment['url']}
                                                url_list.append(short_dictionary)
                                        if "event" in single_attachment.keys():
                                            single_attachment = single_attachment['event']
                                            short_dictionary = {'type': "Event",
                                                                'name': single_attachment['name'],
                                                                'startTime': str(datetime.datetime.fromtimestamp(single_attachment['start_timestamp']))}
                                            if "end_timestamp" in single_attachment.keys():
                                                if single_attachment['end_timestamp'] > 0:
                                                    short_dictionary['endTime'] = single_attachment['end_timestamp']
                                            normalized_json['event'] = short_dictionary
                                if len(url_list) > 0:
                                    if len(url_list) == 1:
                                        normalized_json['url'] = url_list[0]
                                    else:
                                        normalized_json['url'] = url_list
                                if len(location_list) > 0:
                                    if len(location_list) == 1:
                                        normalized_json['location'] = location_list[0]
                                    else:
                                        normalized_json['location'] = location_list
                            text_block = text_block.replace("  ", " ")
                            normalized_json = normalization_tags(normalized_json, text_block, 'facebook')
                        # try to de-dupe tags just in case dupes got in
                        if "tags" in normalized_json:
                            my_tags = []
                            for tag in normalized_json['tags']:
                                if tag not in my_tags:
                                    my_tags.append(tag)
                            normalized_json['tags'] = my_tags
                        with open(filename, "w") as w:
                            json.dump(normalized_json, w)
                        w.close()
                        window['-OUTPUT-'].update(f"normalized {filename}\n", append=True)
                        current_count += 1
                        window['-Progress-'].update_bar(current_count, master_count)
    window['-OUTPUT-'].update(f"normalization for facebook data complete\n", append=True)


def facebook_mediaExif_extractor(short_dictionary, exifchunk):
    for exif_data in exifchunk:
        for key in exif_data.keys():
            short_dictionary[f'exif:{key}'] = exif_data[key]
    return short_dictionary

def normalization_tags(normalized_json, text_block, platform):
    text_block = text_block.replace("\n", " ")
    linklist = split_url(text_block)
    hashlist = split_hashtag(text_block)
    mentionlist = split_facebook_mention(text_block)
    if len(hashlist) > 0 or len(linklist) > 0 or len(mentionlist) > 0:
        normalized_json['tags'] = []
        if len(hashlist) > 0:
            for hashtag in hashlist:
                if platform == "facebook":
                    normalized_json['tags'].append({'type': "Hashtag",
                                                    'id': f'https://www.facebook.com/hashtag/{hashtag[1:]}',
                                                    'name': hashtag})
                if platform == "youtube":
                    normalized_json['tags'].append({'type': "Hashtag",
                                                    'id': f"https://www.youtube.com/hashtag/{hashtag[1:]}",
                                                    'name': hashtag})
        if len(mentionlist) > 0:
            for mention in mentionlist:
                normalized_json['tags'].append({'type': 'Mention',
                                                'id': mention.split(":")[0][1:],
                                                'name': mention.split(":")[-1]})
        if len(linklist) > 0:
            for linky in linklist:
                normalized_json['tags'].append({'type': 'Link',
                                                'href': linky,
                                                'mediaType': 'text/html'})
    return normalized_json



# facebook correspondence handler
def facebook_correspondence(source_folder=str, target_folder=str):
    target_folder = f"{target_folder}/correspondence"
    correspondence_source = f"{source_folder}/this_profile's_activity_across_facebook/"
    for dirpath, dirnames, filenames in os.walk(correspondence_source):
        for filename in filenames:
            if filename.endswith(".json"):
                window['-OUTPUT-'].update(f"processing {dirpath}\n", append=True)
                my_json_file = os.path.join(dirpath, filename)
                with open(my_json_file, 'r') as r:
                    json_data = r.read()
                    json_data = json.loads(json_data)
                    messages = json_data['messages']
                    latest_timestamp = messages[-1]['timestamp_ms']/1000
                    latest_timestamp = str(datetime.datetime.fromtimestamp(latest_timestamp))
                    my_dir = dirpath.split("/")[-1].split("\\")[-1]
                    my_dir = f"{target_folder}/{latest_timestamp[:4]}/{latest_timestamp[:10]}_{my_dir}"
                    new_json_file = os.path.join(my_dir, filename)
                    create_directory(new_json_file)
                    shutil.copy2(my_json_file, new_json_file)
                    shutil.copystat(my_json_file, new_json_file)
                r.close()
    window['-OUTPUT-'].update(f"done processing correspondence\n", append=True)

# Facebook workhorse
def facebook_handler(source_folder=str, target_folder=str):
    window['-OUTPUT-'].update(f"processing facebook download\n", append=True)
    my_precious = f"{source_folder}/logged_information/professional_dashboard/your_professional_dashboard_activity.json"
    window['-OUTPUT-'].update("processing facebook posts\n", append=True)
    window['-STATUS-'].update("Go get a cup of coffee, you deserve it\n", text_color="green2")
    valuables = {}
    valuables['base_location'] = target_folder
    valuables['source_dir'] = source_folder
    log = open("logger.txt", "a")
    id_list = []
    upload_list = set()
    baseline = f"{valuables['base_location']}/"
    fb_log = f"{baseline}/log_facebookIDs.txt"
    if not os.path.isfile(fb_log):
        create_directory(fb_log)
        with open(fb_log, "a") as w:
            window['-OUTPUT-'].update("facebook log file created\n", append=True)
        w.close()
    with open(fb_log, "r") as r:
        for line in r:
            id_list.append(line[:-1])
    r.close()
    window['-OUTPUT-'].update("list of existing posts compiled\n", append=True)
    window['-OUTPUT-'].update("getting user data for posts\n", append=True)
    id_list2 = []
    user_data_file = f"{valuables['source_dir']}/logged_information/professional_dashboard/your_professional_dashboard_activity.json"
    user_data = {}
    with open(user_data_file, "r") as r:
        json_data = r.read()
        user = json.loads(json_data)
        username = user['prodash_activity'][0]['page_name']
        user_data['name'] = username
        user_data['screen_name'] = username
    user_id_options = [f"{valuables['source_dir']}/this_profile's_activity_across_facebook/posts/profile_posts_1.json",
                       f"{valuables['source_dir']}/this_profile's_activity_across_facebook/events/events.json",
                       f"{valuables['source_dir']}/this_profile's_activity_across_facebook/posts/videos.json",
                       f"{valuables['source_dir']}/this_profile's_activity_across_facebook/comments_and_reactions/comments.json"]
    user_id = ""
    user_id_int = ""
    # iterate over a few things to locate the user_id that'll be embedded with the posts
    while user_id == "" and user_id_int == "":
        for option in user_id_options:
            if os.path.isfile(option):
                with open(option, "r") as r:
                    filedata = r.read()
                    filedata = filedata.split(f":274:{username}")
                    if len(filedata) > 1:
                        user_id = filedata[0].split("@[")[-1]
                        user_id_int = int(user_id)
        # if can't find the user id crash the program so can see what happened
        if user_id == "" and user_id_int == "":
            sys.exit()
    user_data['id'] = user_id_int
    user_data['id_str'] = user_id
    window['-OUTPUT-'].update("account data and profile data loaded\n", append=True)
    # aggregate the list of files needed to process a facebook account
    my_precious_posts = f"{source_folder}/this_profile's_activity_across_facebook/posts"
    my_precious_albums = f"{source_folder}/this_profile's_activity_across_facebook/posts/album"
    my_precious_events = f"{source_folder}/this_profile's_activity_across_facebook/events"
    my_precious_posts_list = [f for f in os.listdir(my_precious_posts) if os.path.isfile(f"{my_precious_posts}/{f}") and "facebook_editor" not in f]
    my_precious_album_list = [f for f in os.listdir(my_precious_albums) if os.path.isfile(f"{my_precious_albums}/{f}")]
    my_precious_event_list = 'events.json'
    blank_post = {}
    blank_metadata = {}
    with open(f"{my_precious_events}/{my_precious_event_list}", 'r') as backlog:
        json_data = backlog.read()
        facebook = json.loads(json_data)
        facebook = facebook['your_events_v2']
        counter = 0
        total = len(facebook)
        blank_post = {}
        for post in facebook:
            new_post = blank_post
            text_string = ""
            start_timestamp = post['start_timestamp']
            end_timestamp = post['end_timestamp']
            start_date = f"{str(datetime.datetime.fromtimestamp(start_timestamp))}"
            end_date = f"{str(datetime.datetime.fromtimestamp(end_timestamp))}"
            date_created = ""
            if "create_timestamp" in post.keys():
                date_created = str(post['create_timestamp'])
                post_id = f"{str(start_date)[:10]}_{date_created}"
            if date_created == "":
                post_id = f"{str(start_date)[:10]}_{str(start_timestamp)}-{str(end_timestamp)}"
                date_created = str(start_date)[:10]
            print(post_id)
            if post_id not in id_list:
                post['post_id'] = post_id
                counter = 0
                while post_id in id_list2:
                    if post_id.endswith(f"-{str(counter)}"):
                        post_id = post_id[:-2]
                    counter += 1
                    post_id = f"{post_id}-{str(counter)}"
                post['user'] = user_data
                post['post_type'] = "facebook_event"
                filepath = f"{baseline}/backlog/events/{post_id[:4]}/{post_id}/"
                upload_list.add(filepath)
                filename = f"{post_id}.txt"
                master_post = f"{filepath}/{filename}"
                create_directory(master_post)
                master_post_text = json.loads(json.dumps(post))
                with open(master_post, 'w') as w:
                    json.dump(master_post_text, w)
                w.close()
                os.rename(master_post, f"{master_post[:-3]}json")
                if 'attachments' in post.keys():
                    for attachment in post['attachments']:
                        units = attachment['data']
                        for unit in units:
                            if "media" in unit.keys():
                                mediafile = unit['media']['uri']
                                media = mediafile.split("/")[-1]
                                source_media = f"{source_folder}/{mediafile}"
                                target_media = f"{filepath}/{media}"
                                shutil.copy2(source_media, target_media)
                                shutil.copystat(source_media, target_media)
                window['-OUTPUT-'].update(f"processed {post_id}\n", append=True)
                counter +=1
                window['-Progress-'].update_bar(counter, total)
                id_list2.append(post_id)
                upload_list.add(filepath)
    total = len(my_precious_album_list)
    counter = 0
    for preciouses in my_precious_album_list:
        with open(f"{my_precious_albums}/{preciouses}", "r") as r:
            json_data = r.read()
            print(f"album {preciouses}")
            facebook = json.loads(json_data)
            timestamp = facebook['last_modified_timestamp']
            timestamp_translated = str(datetime.datetime.fromtimestamp(timestamp))
            post_id = f"{str(timestamp_translated)[:10]}_{str(facebook['name'])}"
            if post_id not in id_list:
                counter = 0
                while post_id in id_list2:
                    if post_id.endswith(f"-{str(counter)}"):
                        post_id = post_id[:-2]
                    counter += 1
                    post_id = f"{post_id}-{str(counter)}"
                facebook['post_id'] = post_id
                facebook['user'] = user_data
                facebook['post_type'] = "facebook_album"
                filepath = f"{baseline}/backlog/albums/album{preciouses[:-5]}"
                filename = f"{post_id}.txt"
                filename = filename.replace("'", "").replace('"', '').replace(':', '')
                master_post = f"{filepath}/{filename}"
                create_directory(master_post)
                master_post_text = json.loads(json.dumps(facebook))
                with open(master_post, 'w') as w:
                    json.dump(master_post_text, w)
                w.close()
                os.rename(master_post, f"{master_post[:-3]}json")
                # now deal with the media in the album
                if 'photos' in facebook.keys():
                    for photo in facebook['photos']:
                        fb_media = f"{source_folder}/{photo['uri']}"
                        target_media = f"{filepath}/{fb_media.split('/')[-1]}"
                        if not os.path.isfile(target_media):
                            shutil.copy2(fb_media, target_media)
                            shutil.copystat(fb_media, target_media)
                if "cover_photo" in facebook.keys():
                    fb_media = f"{source_folder}/{facebook['cover_photo']['uri']}"
                    target_media = f"{filepath}/{fb_media.split('/')[-1]}"
                    if not os.path.isfile(target_media):
                        shutil.copy2(fb_media, target_media)
                        shutil.copystat(fb_media, target_media)
                if "videos" in facebook.keys():
                    for video in facebook['videos']:
                        fb_media = f"{source_folder}/{video['uri']}"
                        target_media = f"{filepath}/{fb_media.split('/')[-1]}"
                        if not os.path.isfile(target_media):
                            shutil.copy2(fb_media, target_media)
                            shutil.copystat(fb_media, target_media)
                upload_list.add(filepath)
            counter += 1
            window['-Progress-'].update_bar(counter, total)
            window['-OUTPUT-'].update(f"processed {post_id}\n", append=True)
            id_list2.append(post_id)
    for preciouses in my_precious_posts_list:
        window['-OUTPUT-'].update(f"{my_precious_posts_list}\n", append=True)
        with open(f"{my_precious_posts}/{preciouses}", 'r') as r:
            json_data = r.read()
            print(f"post file {preciouses}")
            facebook = json.loads(json_data)
            # handle other photos deal, merging into saved posts
            if json_data.startswith("{"):
                if "other_photos_v2" in facebook.keys():
                    facebook = facebook['other_photos_v2']
                    total = len(facebook)
                    counter = 0
                    for post in facebook:
                        print(post)
                        timestamp = post['creation_timestamp']
                        timestamp_translated = str(datetime.datetime.fromtimestamp(timestamp))
                        post_id = f"{str(timestamp_translated)[:10]}_{str(timestamp)}"
                        if post_id not in id_list:
                            counter = 0
                            while post_id in id_list2:
                                if post_id.endswith(f"-{str(counter)}"):
                                    post_id = post_id[:-2]
                                counter += 1
                                post_id = f"{post_id}-{str(counter)}"
                            post['post_id'] = post_id
                            post['user'] = user_data
                            post['post_type'] = "facebook_otherPhotos"
                            filepath = f"{baseline}/backlog/other_photos/{post_id[:4]}/{post_id}"
                            filename = f"{post_id}.txt"
                            master_post = f"{filepath}/{filename}"
                            create_directory(master_post)
                            master_post_text = json.loads(json.dumps(post))
                            with open(master_post, 'w') as w:
                                json.dump(master_post_text, w)
                            w.close()
                            os.rename(master_post, f"{master_post[:-3]}json")
                            # now deal with the media
                            fb_media = f"{source_folder}/{post['uri']}"
                            target_media = f"{filepath}/{fb_media.split('/')[-1]}"
                            if not os.path.isfile(target_media):
                                shutil.copy2(fb_media, target_media)
                                shutil.copystat(fb_media, target_media)
                            counter += 1
                            window['-Progress-'].update_bar(counter, total)
                            window['-OUTPUT-'].update(f"processed {post_id}\n", append=True)
                            id_list2.append(post_id)
                            upload_list.add(filepath)
                # work on the videos post files
                if "videos.json" in preciouses:
                    facebook = facebook['videos_v2']
                    counter = 0
                    total = len(facebook)
                    for post in facebook:
                        print(post)
                        timestamp = post['creation_timestamp']
                        timestamp_translated = str(datetime.datetime.fromtimestamp(timestamp))
                        post_id = f"{str(timestamp_translated[:10])}_{str(timestamp)}"
                        if post_id not in id_list:
                            counter = 0
                            while post_id in id_list2:
                                if post_id.endswith(f"-{str(counter)}"):
                                    post_id = post_id[:-2]
                                counter += 1
                                post_id = f"{post_id}-{str(counter)}"
                            post['post_id'] = post_id
                            post['user'] = user_data
                            post['post_type'] = "facebook_video"
                            filepath = f"{baseline}/backlog/videos/{post_id[:4]}/{post_id}"
                            filename = f"{post_id}.txt"
                            master_post = f"{filepath}/{filename}"
                            create_directory(master_post)
                            master_post_text = json.loads(json.dumps(post))
                            with open(master_post, 'w') as w:
                                json.dump(master_post_text, w)
                            w.close()
                            os.rename(master_post, f"{master_post[:-3]}json")
                            # deal with the media files
                            fb_media = f"{source_folder}/{post['uri']}"
                            target_media = f"{filepath}/{fb_media.split('/')[-1]}"
                            if not os.path.isfile(target_media):
                                shutil.copy2(fb_media, target_media)
                                shutil.copystat(fb_media, target_media)
                            counter += 1
                            window['-Progress-'].update_bar(counter, total)
                            window['-OUTPUT-'].update(f"Processed {post_id}\n", append=True)
                            id_list2.append(post_id)
                            upload_list.add(filepath)
            # for handling proper posts since those are a list
            if json_data.startswith('['):
                total = len(facebook)
                counter = 0
                for post in facebook:
                    print(post)
                    timestamp = post['timestamp']
                    timestamp_translated = str(datetime.datetime.fromtimestamp(timestamp))
                    post_id = f"{str(timestamp_translated[:10])}_{str(timestamp)}"
                    if post_id not in id_list:
                        counter = 0
                        while post_id in id_list2:
                            if post_id.endswith(f"-{str(counter)}"):
                                post_id = post_id[:-2]
                            counter += 1
                            post_id = f"{post_id}-{str(counter)}"
                        post['post_id'] = post_id
                        post['user'] = user_data
                        post['post_type'] = "facebook_post"
                        filepath = f"{baseline}/backlog/posts/{post_id[:4]}/{post_id}"
                        filename = f"{post_id}.txt"
                        master_post = f"{filepath}/{filename}"
                        create_directory(master_post)
                        master_post_text = json.loads(json.dumps(post))
                        with open(master_post, 'w') as w:
                            json.dump(master_post_text, w)
                        w.close()
                        os.rename(master_post, f"{master_post[:-3]}json")
                        # deal with any media
                        if "attachments" in post.keys():
                            attachment_list = post['attachments']
                            for attachment in attachment_list:
                                attachment = attachment['data']
                                for x in attachment:
                                    if "media" in x.keys():
                                        fb_media = f"{source_folder}/{x['media']['uri']}"
                                        target_media = f"{filepath}/{fb_media.split('/')[-1]}"
                                        if not os.path.isfile(target_media):
                                            shutil.copy2(fb_media, target_media)
                                            shutil.copystat(fb_media, target_media)
                        counter += 1
                        window['-Progress-'].update_bar(counter, total)
                        window['-OUTPUT-'].update(f"processed {post_id}\n", append=True)
                        id_list2.append(post_id)
                        upload_list.add(filepath)
    id_list2.sort()
    with open(fb_log, "a") as w:
        for item in id_list2:
            w.write(f"{item}\n")
    w.close()
    print("something")
    upload_list = list(upload_list)
    upload_list.sort()
    print(upload_list)
    return upload_list

def instagram_handler(source_folder=str, target_folder=str):
    print("something")

def normalize_instagram(preservation_directories=list):
    print("something else")

layout = [
    # [sg.Push(),sg.Titlebar("My Twitter Breaker tool"),sg.Push()],
    [
        sg.Radio("Twitter", group_id="media_type", key='-TYPE_twitter-'),
        sg.Radio("Facebook page", group_id="media_type", key="-TYPE_facebook_page-"),
        sg.Radio("Instagram account", group_id="media_type", key="-TYPE_instagram-"),
        sg.Radio("YouTube", group_id="media_type", key="-TYPE_youtube-"),
        sg.Button("Load options")
    ],
    [
        sg.Push(),
        sg.Text("social media zip file", key="-File_Label-", visible=True),
        sg.In("", key="-File-", visible=True), #sg.In(size=(50, 1), enable_events=True, key="-File-"),
        sg.FileBrowse(file_types=(("zip files only", "*.zip"),), key="-File_Browse-", visible=True)
    ],
    [
        sg.Push(),
        sg.Text("temporary staging location for unprocessed social media archive", key="-SourceFolder_label-", visible=True),
        sg.In("", key="-SourceFolder-", visible=True),
        sg.FolderBrowse(key="-SourceFolder_browse-", visible=True)
    ],
    [
        sg.Push(),
        sg.Text("target location for processed social media archive"),
        sg.In("", key="-TargetFolder-"), #sg.In(size=(50, 1), enable_events=True, key="-TargetFolder-"),
        sg.FolderBrowse()
    ],
    [
        sg.Checkbox("TDA upload", tooltip="Texas State Archives use only", visible=True, key="-UPLOAD-"),
        sg.Push(),
        sg.Text("upload staging location"),
        sg.In("", key="-UploadStaging-", tooltip="Where the previously uningested files will be staged for the upload process"), #sg.In(size=(50, 1), enable_events=True, key="-UploadStaging-"),
        sg.FolderBrowse()
    ],
    [
        sg.Push(),
        sg.Text("channel url", key="-youtube_channel_label-", visible=False),
        sg.In(default_text="example: https://www.youtube.com/@TSLAC", visible=False, key="-youtube_channel-"),

    ],
    [
        sg.Push(),
        sg.Text("Choose types to download: ", visible=False, key="-youtube_type_label-"),
        sg.Radio("all videos", visible=False, key='-youtube_type_video-', default=False, group_id="youtube_selector"),
        sg.Radio("selected videos", visible=False, key="-youtube_type_selected-", default=True, group_id="youtube_selector")
    ],
    [
        sg.Push(),
        sg.Checkbox("shorts", visible=False, key="-youtube_type_shorts-"),
        sg.Checkbox("lives", visible=False, key="-youtube_type_streams-"),
        sg.Checkbox("podcasts", visible=False, key="-youtube_type_podcasts-"),
        sg.Checkbox("playlists", visible=False, key="-youtube_type_playlists-", tooltip="Can only download one at a time"),
        sg.Push()
    ],
    [
        sg.Push(),
        sg.Text("Single playlist url, like https://www.youtube.com/watch?v=K1uWw6PCIPc&list=PLLvdMHqukWBLCAOM9ANi71JKPAkcjDnIM", visible=False, key="-youtube_playlists_text-"),
    ],
    [
        sg.Push(),
        sg.Multiline(default_text="", visible=False, key="-youtube_playlists_list-", size=(60, 3))
    ],
    [
        sg.Push(),
        sg.Text("If date range applies", visible=False, key="-youtube_date_label-")
    ],
    [
        sg.Push(),
        sg.Text("Begin date (yyyy-mm-dd):", visible=False, key="-youtube_date_begin_label-"),
        sg.In(default_text="YYYY-MM-DD", visible=False, key="-youtube_date_begin-", size=(15, 1)),
        sg.Text("End date (yyyy-mm-dd):", visible=False, key="-youtube_date_end_label-"),
        sg.In(default_text="YYYY-MM-DD", visible=False, key="-youtube_date_end-", size=(15, 1))
    ],
    [
        sg.Push(),
        sg.Checkbox("Get Comments?", visible=False, key='-youtube_GetComments-', tooltip="include YouTube comments in harvested YouTube data"),
    ],
    [
        sg.Push(),
        sg.Checkbox('Get correspondence?', tooltip="extract correspondence from social media data archive", key='-GET_correspondence-', enable_events=True, visible=False)
    ],
    [
        sg.Checkbox("Normalize JSON?", tooltip="Checking this will convert native JSON to universal format and create duplicate presentation files",
                    key="-NORMALIZE-", enable_events=True, visible=True),
        sg.Checkbox("Export Metadata?", checkbox_color="dark green",
                    tooltip="Checking this box will create sidecar metadata for each post compatible with TSLAC standards",
                    key='-METADATA-', enable_events=True, visible=False),
        sg.Checkbox("Generate wall too?", checkbox_color="dark green", tooltip="Checking this box will generate a html page emulating a twitter wall which can be used to review or validate content",
                            key="-WALL-", enable_events=True, visible=False)
    ],
    [
        sg.Text("Fill in additional metadata elements if you wish:", key='-MOREMETADATA-', visible=False)
    ],
    [
        sg.Push(),
        sg.Text("Agency Name/Abbreviation:", key="-CREATOR_TEXT-", visible=False),
        sg.Input("tslac", size=(50, 1), key="-CREATOR-", visible=False)
    ],
    [
        sg.Push(),
        sg.Text("Official collection name:", key="-CITATION_TEXT-", visible=False),
        sg.Input("Social Media Test", size=(50, 1), key="-CITATION-", visible=False)
    ],
    [

    ],
    [
        sg.Text("")
    ],
    [
        sg.Text("Select execute to start processing")
    ],
    [
        sg.Push(),
        sg.Button("Execute", tooltip="This will start the program running."),
        sg.Push()
    ],
    [
        sg.Text("Select Close to close the window.")
    ],
    [sg.Button("Close",
               tooltip="Close this window. Other processes you started must be finished before this button will do anything.",
               bind_return_key=True)],
    [
        sg.ProgressBar(1, orientation="h", size=(50, 20), bar_color="dark green", key="-Progress-", border_width=5,
                       relief="RELIEF_SUNKEN")
    ],
    [
        sg.Text("", key="-STATUS-")
    ],
    [
        sg.Multiline(default_text="Click execute to show progress\n------------------------------\n", size=(100, 6),
                     auto_refresh=True, reroute_stdout=False, key="-OUTPUT-", autoscroll=True, border_width=5),
    ],
]

window = sg.Window(
    "Social Media Harvest and Preservation tool",
    layout,
    icon=my_icon, #"Twitter_icon.png",
    button_color="dark green",

)

event, values = window.read()

while True:
    event, values = window.read()
    if values['-TYPE_youtube-'] is True:
        window['-File-'].update(visible=False)
        window['-File_Label-'].update(visible=False)
        window['-File_Browse-'].update(visible=False)
        window["-SourceFolder_label-"].update(visible=False)
        window['-SourceFolder-'].update(visible=False)
        window['-SourceFolder_browse-'].update(visible=False)
        window['-youtube_channel_label-'].update(visible=True)
        window['-youtube_channel-'].update(visible=True)
        window['-youtube_type_label-'].update(visible=True)
        window['-youtube_type_video-'].update(visible=True)
        window['-youtube_type_selected-'].update(visible=True)
        window['-youtube_type_shorts-'].update(visible=True)
        window['-youtube_type_streams-'].update(visible=True)
        window['-youtube_type_podcasts-'].update(visible=True)
        window['-youtube_type_playlists-'].update(visible=True)
        window['-youtube_playlists_text-'].update(visible=True)
        window['-youtube_playlists_list-'].update(visible=True)
        window['-youtube_date_label-'].update(visible=True)
        window['-youtube_date_begin_label-'].update(visible=True)
        window['-youtube_date_begin-'].update(visible=True)
        window['-youtube_date_end_label-'].update(visible=True)
        window['-youtube_date_end-'].update(visible=True)
        window['-youtube_GetComments-'].update(visible=True)
        window['-GET_correspondence-'].update(visible=False)
    if values['-TYPE_twitter-'] is True or values['-TYPE_facebook_page-'] is True:
        window['-File-'].update(visible=True)
        window['-File_Label-'].update(visible=True)
        window['-File_Browse-'].update(visible=True)
        window["-SourceFolder_label-"].update(visible=True)
        window['-SourceFolder-'].update(visible=True)
        window['-SourceFolder_browse-'].update(visible=True)
        window['-youtube_channel_label-'].update(visible=False)
        window['-youtube_channel-'].update(visible=False)
        window['-youtube_type_video-'].update(visible=False)
        window['-youtube_type_selected-'].update(visible=False)
        window['-youtube_type_shorts-'].update(visible=False)
        window['-youtube_type_streams-'].update(visible=False)
        window['-youtube_type_podcasts-'].update(visible=False)
        window['-youtube_type_playlists-'].update(visible=False)
        window['-youtube_playlists_text-'].update(visible=False)
        window['-youtube_playlists_list-'].update(visible=False)
        window['-youtube_type_label-'].update(visible=False)
        window['-youtube_date_label-'].update(visible=False)
        window['-youtube_date_begin_label-'].update(visible=False)
        window['-youtube_date_begin-'].update(visible=False)
        window['-youtube_date_end_label-'].update(visible=False)
        window['-youtube_date_end-'].update(visible=False)
        window['-GET_correspondence-'].update(visible=True)
        window['-youtube_GetComments-'].update(visible=False)
    if values['-NORMALIZE-'] is True:
        window['-METADATA-'].update(visible=True)
        window['-WALL-'].update(visible=True)
        window['-MOREMETADATA-'].update(visible=True)
        window['-CREATOR_TEXT-'].update(visible=True)
        window['-CREATOR-'].update(visible=True)
        window['-CITATION_TEXT-'].update(visible=True)
        window['-CITATION-'].update(visible=True)
    if values['-NORMALIZE-'] is False:
        window['-METADATA-'].update(visible=False)
        window['-WALL-'].update(visible=False)
        window['-MOREMETADATA-'].update(visible=False)
        window['-CREATOR_TEXT-'].update(visible=False)
        window['-CREATOR-'].update(visible=False)
        window['-CITATION_TEXT-'].update(visible=False)
        window['-CITATION-'].update(visible=False)
    target_file = values['-File-'] #"/media/sf_Z_DRIVE/Working/research/socialMedia/facebook/facebook-tslac-2024-04-08-Hn2tG4Jj.zip" #
    source_folder = values['-SourceFolder-'] #"/media/sf_Z_DRIVE/Working/research/socialMedia/facebook/facebook-tslac-2024-04-08-Hn2tG4Jj" #
    target_folder = values['-TargetFolder-']
    upload_folder = f"{target_folder}_upload"
    metadata_generator = values['-METADATA-']
    metadata_creator = values['-CREATOR-']
    metadata_citation = values['-CITATION-']
    collectionName = values['-CITATION-']
    wall = values['-WALL-']
    if event == "Execute":
        if values['-TYPE_youtube-'] is True:
            # get the variables
            startdate = values['-youtube_date_begin-']
            enddate = values['-youtube_date_end-']
            channel = values['-youtube_channel-']
            options_set = []
            if values['-youtube_type_video-'] is True:
                options_set.append("videos")
            if values['-youtube_type_selected-'] is True:
                if values['-youtube_type_shorts-'] is True:
                    options_set.append("shorts")
                if values['-youtube_type_streams-'] is True:
                    options_set.append("streams")
                if values['-youtube_type_podcasts-'] is True:
                    options_set.append("podcasts")
                if values['-youtube_type_playlists-'] is True:
                    options_set.append(f"playlists={values['-youtube_playlists_list-']}")
            # do a direct harvest of the data, will print out as it goes
            youtube_handler(channel_name=channel, options_set=options_set, startdate=startdate, enddate=enddate, comments=values['-youtube_GetComments-'], target=values['-TargetFolder-'])
            if values['-NORMALIZE-'] is True:
                # tap into foldering rules and assume that anything not put into standard structure needs normalization
                preservation_directories = create_preservation(target_folder)
                # end list of folders to be normalized to normalization handler
                normalize_youtube_activityStream(preservation_directories)
                if values['-METADATA-'] is True:
                    window['-OUTPUT-'].update(f"started metadata generation\n", append=True)
                    make_metadata2(preservation_directories, social_type="YouTube", collection_name=collectionName, agency=metadata_creator)
                    window['-OUTPUT-'].update("metadata generation completed\n", append=True)
                if values['-WALL-'] is True:
                    window['-OUTPUT-'].update(f"creating wall\n", append=True)
                    create_wall(target_folder)
                    window['-OUTPUT-'].update(f"wall generated\n", append=True)
            if values['-UPLOAD-'] is True:
                window['-OUTPUT-'].update(f"beginning to create upload directories and files\n", append=True)
                if values['-UploadStaging-'] != "":
                    upload_folder = values['-UploadStaging-']
                else:
                    upload_folder = f"{target_folder}_upload"
                for post in preservation_directories:
                    post = post.replace("/preservation2", "")
                    for dirpath, dirnames, filenames in os.walk(post):
                        for filename in filenames:
                            filename1 = os.path.join(dirpath, filename)
                            filename2 = filename1.replace(target_folder, upload_folder)
                            create_directory(filename2)
                            shutil.copy2(filename1, filename2)
                            shutil.copystat(filename1, filename2)
                            window['-OUTPUT-'].update(f"copied {filename} to upload staging area\n", append=True)
                window['-OUTPUT-'].update(f"done creating upload directories and files\n", append=True)

        upload_list = set()
        year_list = set()
        if target_file != "" and target_folder != "" and source_folder != "":
            window['-OUTPUT-'].update(f"your zip file is {target_file}\n", append=True)
            window['-OUTPUT-'].update(f"your temp folder is located at {source_folder}\n", append=True)
            window['-OUTPUT-'].update(f"your final processed archive will be at {target_folder}\n", append=True)
            window['-OUTPUT-'].update(f"executing...\n")
            if values['-TYPE_twitter-'] is True:
                extract_social_archive(target_file, source_folder)
                window['-OUTPUT-'].update(f"Starting processing twitter account data\n", append=True)
                # send the whole deal to the twitter handler and get back a list of twitter data to deal with
                my_source = f"{source_folder}/{target_file.split('/')[-1][:-4]}"
                upload_list = tweet_handler(my_source, target_folder)
                if values['-GET_correspondence-'] is True:
                    twitter_correspondence(source_folder, target_folder)
                if values['-NORMALIZE-'] is True:
                    # tap into foldering rules and assume that anything not put into standard structure needs normalization
                    preservation_directories = create_preservation(target_folder)
                    # send list of folders to be normalized to normalization handler
                    normalize_twitter_activitystream(preservation_directories)
                    if values['-METADATA-'] is True:
                        window['-OUTPUT-'].update(f"starting metadata generation\n", append=True)
                        make_metadata2(preservation_directories, "Twitter", collectionName, metadata_creator)
                        window['-OUTPUT-'].update(f"metadata generation completed\n", append=True)
                    if values['-WALL-'] is True:
                        window['-OUTPUT-'].update(f"creating wall\n", append=True)
                        create_wall(target_folder)
                        window['-OUTPUT-'].update(f"wall generated\n", append=True)
                if values['-UPLOAD-'] is True:
                    window['-OUTPUT-'].update(f"beginning to create upload directories and files\n", append=True)
                    if values['-UploadStaging-'] != "":
                        upload_folder = values['-UploadStaging-']
                    else:
                        upload_folder = f"{target_folder}_upload"
                    for post in preservation_directories:
                        for dirpath, dirnames, filenames in os.walk(post):
                            filename1 = os.path.join(dirpath, filename)
                            filename2 = filename1.replace(target_folder, upload_folder)
                            create_directory(filename2)
                            shutil.copy2(filename1, filename2)
                            shutil.copystat(filename1, filename2)
                            window['-OUTPUT-'].update(f"copied {filename} to upload staging area\n", append=True)
                    window['-OUTPUT-'].update(f"done creating upload directories and files\n", append=True)

            if values['-TYPE_facebook_page-'] is True:
                extract_social_archive(target_file, source_folder)
                window['-OUTPUT-'].update(f"Starting processing facebook page account data\n", append=True)
                # send the whole deal to the twitter handler and get back a list of twitter data to deal with
                upload_list = facebook_handler(source_folder, target_folder)
                if values['-NORMALIZE-'] is True:
                    # tap into foldering rules and assume that anything not put into standard structure needs normalization
                    preservation_directories = create_preservation(target_folder)
                    # send list of folders to be normalized to normalization handler
                    normalize_facebook_activityStream(preservation_directories)
                    if values['-METADATA-'] is True:
                        window['-OUTPUT-'].update(f"starting metadata generation\n", append=True)
                        make_metadata2(preservation_directories, "Facebook", collectionName, metadata_creator)
                        window['-OUTPUT-'].update(f"metadata generation completed\n", append=True)
                    if values['-WALL-'] is True:
                        window['-OUTPUT-'].update(f"creating wall\n", append=True)
                        create_wall(target_folder)
                        window['-OUTPUT-'].update(f"wall generated\n", append=True)
                if values['-UPLOAD-'] is True:
                    window['-OUTPUT-'].update(f"beginning to create upload directories and files\n",
                                              append=True)
                    if values['-UploadStaging-'] != "":
                        upload_folder = values['-UploadStaging-']
                    else:
                        upload_folder = f"{target_folder}_upload"
                    for post in preservation_directories:
                        for dirpath, dirnames, filenames in os.walk(post):
                            for filename in filenames:
                                filename1 = os.path.join(dirpath, filename)
                                filename2 = filename1.replace(target_folder, upload_folder)
                                create_directory(filename2)
                                shutil.copy2(filename1, filename2)
                                shutil.copystat(filename1, filename2)
                                window['-OUTPUT-'].update(f"copied {filename} to upload staging area\n",
                                                          append=True)
                    window['-OUTPUT-'].update(f"done creating upload directories and files\n", append=True)
            if values['-TYPE_instagram-'] is True:
                window['-OUTPUT-'].update(f"Starting processing instagram account data\n", append=True)
                # send the whole deal to the twitter handler and get back a list of twitter data to deal with
                upload_list = instagram_handler(source_folder, target_folder)
                if values['-NORMALIZE-'] is True:
                    extract_social_archive(target_file, source_folder)
                    # tap into foldering rules and assume that anything not put into standard structure needs normalization
                    preservation_directories = create_preservation(target_folder)
                    # send list of folders to be normalized to normalization handler
                    normalize_instagram(preservation_directories)
                    if values['-METADATA-'] is True:
                        window['-OUTPUT-'].update(f"starting metadata generation\n", append=True)
                        make_metadata2(preservation_directories, "Instagram", collectionName, metadata_creator)
                        window['-OUTPUT-'].update(f"metadata generation completed\n", append=True)
                    if values['-WALL-'] is True:
                        window['-OUTPUT-'].update(f"creating wall\n", append=True)
                        create_wall(target_folder)
                        window['-OUTPUT-'].update(f"wall generated\n", append=True)
                if values['-UPLOAD-'] is True:
                    window['-OUTPUT-'].update(f"beginning to create upload directories and files\n",
                                              append=True)
                    if values['-UploadStaging-'] != "":
                        upload_folder = values['-UploadStaging-']
                    else:
                        upload_folder = f"{target_folder}_upload"
                    for post in preservation_directories:
                        for dirpath, dirnames, filenames in os.walk(post):
                            filename1 = os.path.join(dirpath, filename)
                            filename2 = filename1.replace(target_folder, upload_folder)
                            create_directory(filename2)
                            shutil.copy2(filename1, filename2)
                            shutil.copystat(filename1, filename2)
                            window['-OUTPUT-'].update(f"copied {filename} to upload staging area\n",
                                                      append=True)
                    window['-OUTPUT-'].update(f"done creating upload directories and files\n", append=True)
                '''
                my_precious = source_folder + "/data/tweet.js"
                my_data = source_folder + "/data"
                if os.path.isfile(my_precious):
                    window['-OUTPUT-'].update("twitter archive already extracted, moving on\n", append=True)
                if not os.path.isfile(my_precious):
                    window['-OUTPUT-'].update("extracting twitter archive for manipulation...\n", append=True)
                    crazy = zipfile.ZipFile(target_file)
                    crazy.extractall(source_folder)
                window['-OUTPUT-'].update("processing tweets...\n", append=True)
                window['-STATUS-'].update(
                    "Go get a cup of coffee, you deserve it. Press ctrl+c in the terminal window to stop processing.\n",
                    text_color="green2")
                valuables = {}
                valuables['source_dir'] = my_data
                valuables['base_location'] = target_folder
                if metadata_citation != "":
                    valuables[
                        'preferredCitation'] = metadata_citation + ". Archives and Information Services Division, Texas State Library and Archives Commission."
                if metadata_creator != "":
                    valuables['agency'] = metadata_creator
                print("starting the process")
                log = open("logger.txt", "a")
                id_list = []
                baseline = valuables[
                               'base_location'] + "/"  # + "/" + valuables['agency'] + "/" + valuables['harvestType'] + "/"
                if not os.path.isfile(baseline + "log_tweetIDs.txt"):
                    create_directory(baseline + "log_tweetIDs.txt")
                    with open(baseline + "log_tweetIDs.txt", "a") as w:
                        print("tweet log file created")
                    w.close()
                with open(baseline + "log_tweetIDs.txt", "r") as r:
                    for line in r:
                        line = line[:-1]
                        id_list.append(line)
                r.close()
                print("list of existing tweets compiled")
                id_list2 = []
                # start creating the user structure
                user_data = {}
                with open(valuables['source_dir'] + "/account.js", "r") as data:
                    json_data = data.read()
                    json_data = json_data.replace('window.YTD.account.part0 = [\n  ', '')
                    json_data = json_data.replace('\n]', '')
                    user = json.loads(json_data)
                    user_data['id'] = int(user['account']['accountId'])
                    user_data['id_str'] = user['account']['accountId']
                    user_data['name'] = user['account']['accountDisplayName']
                    user_data['screen_name'] = user['account']['username']
                    user_data['created_at'] = user['account']['createdAt']
                print("account data loaded")
                with open(valuables['source_dir'] + "/profile.js", "r") as data:
                    json_data = data.read()
                    json_data = json_data.replace('window.YTD.profile.part0 = [\n  ', '')
                    json_data = json_data.replace('\n]', '')
                    user = json.loads(json_data)
                    user_data['location'] = user['profile']['description']['location']
                    user_data['description'] = user['profile']['description']['bio']
                    user_data['url'] = user['profile']['description']['website']
                    user_data['profile_image_url'] = user['profile']['avatarMediaUrl']
                    user_data['profile_image_url_https'] = user['profile']['avatarMediaUrl']
                    user_data['profile_banner_url'] = user['profile']['headerMediaUrl']
                print("profile data loaded")
                with open(valuables['source_dir'] + "/tweet.js", "r") as backlog:
                    json_data = backlog.read()
                    if "window.YTD.tweet.part0 = " in json_data:
                        json_data = json_data.replace("window.YTD.tweet.part0 = ", "")
                    twitter = json.loads(json_data)
                    print(twitter)
                    counter = 0
                    for tweet in twitter:
                        total = len(twitter)
                        counter += 1
                        window['-OUTPUT-'].update(f" processing {counter}/{total}")
                        window['-Progress-'].update_bar(counter, total)
                        # sg.one_line_progress_meter("Progress",counter,total,orientation="h")
                        # denest the tweet
                        tweet = tweet['tweet']
                        tweet_date = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime(
                            '%Y-%m-%d')
                        print(tweet_date)
                        tweet['created_at'] = datetime.datetime.strptime(tweet['created_at'],
                                                                         '%a %b %d %H:%M:%S %z %Y').ctime()
                        if "+" not in tweet['created_at']:
                            tweet['created_at'] = tweet['created_at'][:-4] + "+0000 " + tweet['created_at'][-4:]
                            print(tweet['created_at'])
                        if str(tweet['id']) not in id_list:
                            filename = str(tweet_date) + "_" + str(tweet['id_str']) + '.txt'
                            file_path1 = baseline + "backlog/" + str(tweet_date[:4]) + "/" + str(tweet_date) + "_" + str(
                                tweet['id_str']) + "/"
                            file_path = file_path1 + filename
                            upload_list.add(file_path1)
                            year_list.add(tweet_date[:4])
                            if not os.path.exists(os.path.dirname(file_path)):
                                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                            tweet['user'] = user_data
                            # make changes to json to have it match up with current data standard
                            tweet['id'] = int(tweet['id'])
                            if 'quoted_status' in tweet:
                                tweet['quoted_status']['id'] = int(tweet['quoted_status']['id'])
                            if 'hashtags' in tweet['entities']:
                                for item in tweet['entities']['hashtags']:
                                    item['indices'][0] = int(item['indices'][0])
                                    item['indices'][1] = int(item['indices'][1])
                            if 'symbols' in tweet['entities']:
                                for item in tweet['entities']['symbols']:
                                    item['indices'][0] = int(item['indices'][0])
                                    item['indices'][1] = int(item['indices'][1])
                                    item['id'] = int(item['id'])
                            if 'user_mentions' in tweet['entities']:
                                for item in tweet['entities']['user_mentions']:
                                    item['indices'][0] = int(item['indices'][0])
                                    item['indices'][1] = int(item['indices'][1])
                                    item['id'] = int(item['id'])
                            if 'urls' in tweet['entities']:
                                for item in tweet['entities']['urls']:
                                    item['indices'][0] = int(item['indices'][0])
                                    item['indices'][1] = int(item['indices'][1])
                            if 'quoted_status_id' in tweet:
                                tweet['quoted_status_id'] = int(tweet['quoted_status_id'])
                            if 'quoted_status' in tweet:
                                tweet['quoted_status']['id'] = int(tweet['quoted_status']['id'])
                                tweet['quoted_status']['display_text_range'][0] = int(
                                    tweet['quoted_status']['display_text_range'][0])
                                tweet['quoted_status']['display_text_range'][1] = int(
                                    tweet['quoted_status']['display_text_range'][1])
                            tweet['display_text_range'][0] = int(tweet['display_text_range'][0])
                            tweet['display_text_range'][1] = int(tweet['display_text_range'][1])
                            if 'in_reply_to_user_id' in tweet:
                                tweet['in_reply_to_user_id'] = int(tweet['in_reply_to_user_id'])
                            tweet['retweet_count'] = int(tweet['retweet_count'])
                            tweet['favorite_count'] = int(tweet['favorite_count'])
                            # reorder the json file
                            dictOrder = ['created_at', 'id', 'id_str', 'full_text', 'truncated', 'display_text_range',
                                         'entities',
                                         'extended_entities', 'source', 'in_reply_to_status_id',
                                         'in_reply_to_status_id_str',
                                         'in_reply_to_user_id', 'in_reply_to_user_id_str', 'in_reply_to_screen_name',
                                         'user',
                                         'geo', 'coordinates', 'place', 'contributors', 'is_quote_status', 'retweet_count',
                                         'favorite_count', 'favorited', 'retweeted', 'possibly_sensitive', 'lang']
                            existingKeys = tweet.keys()
                            secondlist = []
                            for k in dictOrder:
                                if k in existingKeys:
                                    secondlist.append(k)
                                else:
                                    if k != "extended_entities":
                                        tweet[k] = None
                                        secondlist.append(k)
                            tempDict = OrderedDict(tweet)
                            for k in secondlist:
                                tempDict.move_to_end(k)
                            tempDict = dict(tempDict)
                            tweet = json.loads(json.dumps(tempDict))
                            # create the tweet file
                            print(file_path)
                            with open(file_path, "w") as output:
                                json.dump(tweet, output)
                            output.close()
                            file_path2 = file_path[:-3] + "json"
                            os.rename(file_path, file_path2)
                            # create the sidecar metadata file
                            hashtags = []
                            if len(tweet['entities']['hashtags']) > 0:
                                for item in tweet['entities']['hashtags']:
                                    hashtags.append(item['text'])
                            mentions = []
                            if len(tweet['entities']['user_mentions']) > 0:
                                for item in tweet['entities']['user_mentions']:
                                    mentions.append(item['screen_name'])
                            # generate metadata file
                            if metadata_generator is True:
                                metadata = Element('dcterms:dcterms',
                                                   {'xmlns': 'http://dublincore.org/documents/dcmi-terms/',
                                                    'xmlns:dcterms': 'http://dublincore.org/documents/dcmi-terms/',
                                                    'xsi:schemaLocation': 'http://dublincore.org/documents/dcmi-terms/ qualifiedDcSchema.xsd',
                                                    'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                                                    'xmlns:tslac': 'https://www.tsl.texas.gov/'})
                                title = SubElement(metadata, 'dcterms:title')
                                title.text = tweet_date + ": tweet id " + str(tweet['id_str'])
                                description = SubElement(metadata, "dcterms:description.abstract")
                                description.text = "Tweet text: " + tweet['full_text']
                                if 'agency' in valuables:
                                    SubElement(metadata, 'dcterms:relation.isPartOf').text = valuables[
                                                                                                 'agency'] + ' social media archive'
                                if 'preferredCitation' in valuables:
                                    SubElement(metadata,
                                               'dcterms:bibliographicCitation').text = f"({title.text}), {valuables['preferredCitation']}"
                                SubElement(metadata, 'dcterms:type').text = "Text"
                                creator = SubElement(metadata, "dcterms:creator")
                                creator.text = tweet['user']['name']
                                date_created = SubElement(metadata, 'dcterms:date.created')
                                date_created.text = tweet_date
                                SubElement(metadata, "dcterms:subject").text = "Social media"
                                SubElement(metadata, "dcterms:subject").text = "Twitter"
                                SubElement(metadata, 'tslac:socialmedia.platform').text = "Twitter"
                                SubElement(metadata, 'tslac:socialmedia.username').text = tweet['user']['screen_name']
                                SubElement(metadata, 'tslac:socialmedia.identifier').text = str(tweet['id_str'])
                                for item in hashtags:
                                    SubElement(metadata, 'tslac:socialmedia.hashtag').text = item
                                for item in mentions:
                                    SubElement(metadata, 'tslac:socialmedia.mentions').text = item
                                metadata_file = file_path2 + ".metadata"
                                writer = open(metadata_file, 'wt', encoding='utf-8')
                                writer.write(prettify(metadata))
                            # continue processing
                            id_list2.append(str(tweet['id_str']))
                            # redownload the banner file and profile image just to be sure you h the current version
                            profile_image_filename = baseline + "profile_image/" + \
                                                     tweet['user']['profile_image_url_https'].split("/")[-1]
                            profile_image_url = tweet['user']['profile_image_url_https']
                            if not os.path.isfile(profile_image_filename):
                                tweet_media_handler(profile_image_url, profile_image_filename)
                            profile_banner_filename = baseline + "profile_banner/" + \
                                                      tweet['user']['profile_banner_url'].split("/")[-1]
                            profile_banner_url = tweet['user']['profile_banner_url']
                            if not os.path.isfile(profile_banner_filename):
                                tweet_media_handler(profile_banner_url, profile_banner_filename)
                            # download the media files
                            images = []
                            if 'extended_entities' in tweet and tweet['extended_entities'] is not None and 'media' in tweet[
                                'extended_entities']:
                                for media in tweet['extended_entities']['media']:
                                    id = media['id_str']
                                    # downloading videos
                                    if 'video_info' in media:
                                        bitrate = 0
                                        # set variable to download only the largest video copy and overwrite anything download to then
                                        for v in media['video_info']['variants']:
                                            if 'bitrate' in v:
                                                if int(v['bitrate']) > bitrate:
                                                    media_filename = v['url'].split(".")[-1]
                                                    media_filename = media_filename.split("?")[0]
                                                    media_filename = file_path1 + id + "." + media_filename
                                                    tweet_media_handler(v['url'], media_filename)
                                                    bitrate = int(v['bitrate'])
                                        # save thumbnail image with _thumb at the end to be clear what it is
                                        media_filename = file_path1 + media['id_str'] + "_thumb." + \
                                                         media['media_url'].split(".")[-1]
                                        tweet_media_handler(media['media_url_https'], media_filename)
                                    # downloading everything else
                                    else:
                                        media_filename = file_path1 + media['id_str'] + "." + media['media_url'].split(".")[
                                            -1]
                                        tweet_media_handler(media['media_url_https'], media_filename)
                                    images.append(id)
                                    # add thumbnail or downloaded image to a list so it doesn't get done twice
                            if 'media' in tweet['entities']:
                                for media in tweet['entities']['media']:
                                    # check list of media IDs to see if download is needed
                                    if media['id_str'] not in images:
                                        if media['type'] == 'photo':
                                            media_filename = file_path1 + media['id_str'] + "." + \
                                                             media['media_url'].split(".")[-1]
                                            tweet_media_handler(media['media_url_https'], media_filename)
                    with open(baseline + "log_tweetIDs.txt", "a") as f:
                        for item in id_list2:
                            f.write(item + "\n")
                    f.close()
                # start processing the upload
                window['-OUTPUT-'].update('\nstarting upload prep\n', append=True)
                window['-OUTPUT-'].update('resetting status bar\n', append=True)
                counter = 0
                total = len(upload_list)
                window['-Progress-'].update_bar(counter,total)
                upload_list = list(upload_list)
                upload_list.sort()
                print(upload_list)
                year_list = list(year_list)
                year_list.sort()
                create_structure_template = {'dirTitle':'',
                                             'prefix':values['-PREFIX-'],
                                             'tempDir':target_folder}
                year_dict = {}
                for item in year_list:
                    structure_dict = create_structure_template
                    structure_dict['dirTitle'] = item
                print(year_dict)
                valuables = ""
                valuables = {'agency':values['-CREATOR-'],
                             'harvestType': 'twitter',
                             'harvest_type': 'timeline',
                             'collectionName': collectionName,
                             'preferredCitation': metadata_citation + ". Archives and Information Services Division, Texas State Library and Archives Commission.",
                             'source_dir': target_folder}
                upload_dict_template = {'preservation_directory':"",
                                        'asset_title':"",
                                        'parent_uuid':valuables['parentFolder'],
                                        'asset_tag':'open',
                                        'export_directory':values['-UploadStaging-'],
                                        'asset_description':'',
                                        'username': values['-USERNAME-'],
                                        'password':values['-PASSWORD-'],
                                        'tenant':values['-TENANCY-'],
                                        'prefix':values['-PREFIX-'],
                                        'custom_type':'Tweet',
                                        'ignore':['.metadata','.db'],
                                        'timeframe':'',
                                        'metadata_file':''}
                for item in upload_list:
                    counter += 1
                    window['-Progress-'].update_bar(counter,total)
                    window['-OUTPUT-'].update(f"processing {counter}/{total}, {item}")
                    upload_dict = upload_dict_template
                    upload_dict['parent_uuid'] = year_dict[item.split("/")[-3]]
                    upload_dict['preservation_directory'] = item
                    upload_dict['asset_title'] = item.split("/")[-2]
                    upload_dict['timeframe'] = "staging/" + item.split("/")[-3]
                    upload_dict['metadata_file'] = item + item.split("/")[-2] + ".json.metadata"
                    pax_prep_withXIP(upload_dict)
                for year in year_list:
                    directory = values['-UploadStaging-'] + "/staging/" + year
                    zippy = str(uuid.uuid4())
                    zippy_name = values['-UploadStaging-'] + "/staging/" + zippy
                    shutil.make_archive(zippy_name,"zip",directory)
                #clean-up
                directory_list = set()
                file_list = set()
                for dirpath, dirnames, filenames in os.walk(values['-UploadStaging-']):
                    for filename in filenames:
                        filename = os.path.join(dirpath,filename)
                        file_list.add(filename)
                        directory_list.add(dirpath)
                file_list = list(file_list)
                file_list.sort()
                total = len(file_list)
                counter = 0
                for item in file_list:
                    os.remove(item)
                    counter += 1
                    window['-Progress-'].update_bar(counter, total)
                    window['-OUTPUT-'].update(f"processing {counter}/{total}, {item}")
                time.sleep(5)
                directory_list = list(directory_list)
                directory_list.sort()
                total = len(file_list)
                counter = 0
                for item in directory_list:
                    try:
                        os.removedirs(item)
                        window['-Progress-'].update_bar(counter, total)
                        window['-OUTPUT-'].update(f"processing {counter}/{total}, {item}")
                    except:
                        continue
                if wall is True:
                    window['-OUTPUT-'].update("\ngenerating twitter wall html page", append=True)
                    twitter_wall_tool.wall_tool(target_folder)
                # twitter_backlog(valuables)
                window['-OUTPUT-'].update("\nall done, click on Close to exit", append=True)'''
        else:
            window['-STATUS-'].update("Need more data, fill in the proper elements\n", text_color="orchid1",
                                      font=("Calibri", "12", "bold"))
            # print("\need more data, fill in the proper elements")
    if event == "Close" or event == sg.WIN_CLOSED:
        break
window.close()

#TODO make each section a definition so it is object-oriented
#TODO pass type of social media to handler for normalization
#TODO pass type of social media and if normalization has occured to handler for wall
#TODO make a spreadsheet output for summary data for the end-user
#TODO fix issue with youtube harvest/normalization stripping too much of the filename