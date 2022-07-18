# a python script to create a wall based on harvested twitter data
import sys, os
import json
import re

source = "../extraction3"  # input("root folder for processed twitter archive: ")
output = source + "/wall.html"
avatar = "./profile_image/"
backlog = source + "/backlog"

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
tweet_text = ""
year = ""
year_list = set()
for dirpath, dirnames, filenames in os.walk(backlog):
    for filename in filenames:
        if filename.endswith(".json"):
            current_year = filename.split("-")[0]
            if current_year != year:
                tweet_text = tweet_text + f'''<article class="tweet"><h2 style="text-align:center" id="{current_year}">{current_year}</h2><br/>
                <a href="#tweets">return to top</a></article>'''
                year_list.add(current_year)
                year = current_year
            filename = os.path.join(dirpath, filename)
            j = open(filename, "r")
            tweet = json.loads(j.read())
            tweet_dict = {"created_at": tweet["created_at"],
                          "name": tweet["user"]["name"],
                          "username": tweet["user"]["screen_name"],
                          "user_url": "https://twitter.com/" + tweet["user"]["screen_name"],
                          "text": tweet['full_text'],
                          "url": "https://twitter.com/" + tweet["user"]["screen_name"] + "/status/" + tweet["id_str"],
                          }
            current_avatar = avatar + tweet['user']['profile_image_url'].split("/")[-1]
            media_string = ""
            if "extended_entities" in tweet:
                for x in tweet['extended_entities']['media']:
                    if x['type'] == "photo":
                        extension = x['media_url_https'].split(".")[-1]
                        media_file = os.path.join(dirpath, x['id'] + "." + extension)
                        media_file = media_file.replace(source + "/", "")
                        media_string = media_string + f'<div><img class="tweet-photo" src="{media_file}"/></div>'
                    if x['type'] == "video":
                        extension = x['media_url_https'].split(".")[-1]
                        thumbnail = os.path.join(dirpath, x['id'] + "_thumb." + extension)
                        thumbnail = thumbnail.replace(source + "/", "")
                        media_extension = x['video_info']['variants'][0]['url'].split(".")[-1]
                        media_file = os.path.join(dirpath, x['id'] + "." + media_extension)
                        media_file = media_file.replace(source + "/", "")
                        media_string = media_string + f'<div><img class="tweet-photo" src="{thumbnail}"/>' + f'<video class="tweet-video" controls src="{media_file}"></video></div>'
            if "retweet_status" in tweet:
                tweet_dict["retweet_count"] = tweet["retweet_status"].get("retweet_count", 0)
            else:
                tweet_dict["retweet_count"] = tweet.get("retweet_count", 0)

            tweet_dict["favorite_count"] = tweet.get("favorite_count", 0)
            tweet_dict["retweet_string"] = "retweet" if tweet_dict["retweet_count"] == 1 else "retweets"
            tweet_dict["favorite_string"] = "like" if tweet_dict["favorite_count"] == 1 else "likes"

            for url in tweet["entities"]["urls"]:
                a = '<a href="%(expanded_url)s">%(url)s</a>' % url
                start, end = url["indices"]
                tweet_dict["text"] = tweet_dict["text"][0:start] + a + tweet_dict["text"][end:]

            current = f'''<article class="tweet">
              <img class="avatar" src="{current_avatar}">
              <a href="{tweet_dict['user_url']}" class="name">{tweet_dict['name']}</a><br>
              <span class="username">{tweet_dict['username']}</span><br>
              <br>
              <div class="text">{tweet_dict['text']}</div><br>
              {media_string}
              <footer>
              {tweet_dict['retweet_count']} {tweet_dict['retweet_string']}, {tweet_dict['favorite_count']} {tweet_dict['favorite_string']}<br>
              <a href="{tweet_dict['url']}"><time>{tweet_dict['created_at']}</time></a>
              </footer>
            </article>'''
            tweet_text = tweet_text + current
year_list = list(year_list)
year_list.sort()
year_block = ""
for item in year_list:
    year_block = year_block + f'''<a href="#{item}" style="font-size:1.5em">{item}</a><br/>'''
header = f'''<header>
    <h1>{tweet_dict['name']} twitter wall</h1>
    <em>Tweet formatting adapted from code for wall generation at <a href="https://github.com/DocNow/twarc">twarc</a></em>
    </header>
    <div class="parent">
    <div class="left">
        <img class="avatar-column" src="{current_avatar}"/>
        <br/>
        <div>{year_block}</div>
    </div>
   <div id="tweets">'''

html = html_head + header + tweet_text + html_foot
with open(output, "w") as w:
    w.write(html)
w.close()