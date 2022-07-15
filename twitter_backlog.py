import requests
from twarc import Twarc
import os
import datetime
import json
# for creating the metadata file
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
import upload_backlog as upload
import configparser
from collections import OrderedDict
import errno

def create_directory(fileName):
    if not os.path.exists(os.path.dirname(fileName)):
        try:
            os.makedirs(os.path.dirname(fileName), exist_ok=True)
        except OSError as exc:
            if exc.errno != errno.EExist:
                raise

def prettify(elem):
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparse = minidom.parseString(rough_string)
    return reparse.toprettyxml(indent="    ")

def tweet_media_handler(url, filename):
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
    tweet_media = requests.get(url, stream=True)
    if tweet_media.status_code == 200:
        filename = filename.replace('?','')
        with open(filename, 'wb') as f:
            for chunk in tweet_media.iter_content(1024):
                f.write(chunk)
        f.close()


def twitter_backlog(credentials: dict, valuables: dict, passcodes: dict):
    log = open("logger.txt", "a")
    t = Twarc(consumer_key=credentials['twitter_consumer_key'],
              consumer_secret=credentials['twitter_consumer_secret'],
              access_token=credentials['twitter_access_token'],
              access_token_secret=credentials['twitter_access_token_secret'])
    id_list = []
    baseline = valuables['base_location'] + "/" + valuables['agency'] + "/" \
               + valuables['harvestType'] + "/"
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
        json_data = json_data.replace('window.YTD.account.part0 = [\n  ','')
        json_data = json_data.replace('\n]','')
        user = json.loads(json_data)
        user_data['id'] = int(user['account']['accountId'])
        user_data['id_str'] = user['account']['accountId']
        user_data['name'] = user['account']['accountDisplayName']
        user_data['screen_name'] = user['account']['username']
        user_data['created_at'] = user['account']['createdAt']
    with open(valuables['source_dir'] + "/profile.js", "r") as data:
        json_data = data.read()
        json_data = json_data.replace('window.YTD.profile.part0 = [\n  ','')
        json_data = json_data.replace('\n]','')
        user = json.loads(json_data)
        user_data['location'] = user['profile']['description']['location']
        user_data['description'] = user['profile']['description']['bio']
        user_data['url'] = user['profile']['description']['website']
        user_data['profile_image_url'] = user['profile']['avatarMediaUrl']
        user_data['profile_image_url_https'] = user['profile']['avatarMediaUrl']
        user_data['profile_banner_url'] = user['profile']['headerMediaUrl']
    with open(valuables['source_dir'] + "/tweet.js", "r") as backlog:
        json_data = backlog.read()
        if "window.YTD.tweet.part0 = " in json_data:
            json_data = json_data.replace("window.YTD.tweet.part0 = ","")
        twitter = json.loads(json_data)
        print(twitter)
        for tweet in twitter:
            #denest the tweet
            tweet = tweet['tweet']
            tweet_date = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d')
            print(tweet_date)
            tweet['created_at'] = datetime.datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y').ctime()
            if "+" not in tweet['created_at']:
                tweet['created_at'] = tweet['created_at'][:-4] + "+0000 " + tweet['created_at'][-4:]
                print(tweet['created_at'])
            if str(tweet['id']) not in id_list:
                filename = str(tweet_date) + "_" + str(tweet['id_str']) + '.txt'
                file_path1 = baseline + "backlog/" + str(tweet_date[:4]) + "/" + str(tweet_date) + "_" + str(tweet['id_str']) + "/"
                file_path = file_path1 + filename
                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                tweet['user'] = user_data
                #make changes to json to have it match up with current data standard
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
                #reorder the json file
                dictOrder = ['created_at','id','id_str','full_text','truncated','display_text_range','entities',
                             'extended_entities','source','in_reply_to_status_id','in_reply_to_status_id_str',
                             'in_reply_to_user_id','in_reply_to_user_id_str','in_reply_to_screen_name','user',
                             'geo','coordinates','place','contributors','is_quote_status','retweet_count',
                             'favorite_count','favorited','retweeted','possibly_sensitive','lang']
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
                #create the tweet file
                print(file_path)
                with open(file_path, "w") as output:
                    json.dump(tweet, output)
                output.close()
                file_path2 = file_path[:-3] + "json"
                os.rename(file_path,file_path2)
                # create the sidecar metadata file
                hashtags = []
                if len(tweet['entities']['hashtags']) > 0:
                    for item in tweet['entities']['hashtags']:
                        hashtags.append(item['text'])
                mentions = []
                if len(tweet['entities']['user_mentions']) > 0:
                    for item in tweet['entities']['user_mentions']:
                        mentions.append(item['screen_name'])
                metadata = Element('dcterms:dcterms', {'xmlns': 'http://dublincore.org/documents/dcmi-terms/','xmlns:dcterms': 'http://dublincore.org/documents/dcmi-terms/','xsi:schemaLocation': 'http://dublincore.org/documents/dcmi-terms/ qualifiedDcSchema.xsd','xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance','xmlns:tslac': 'https://www.tsl.texas.gov/'})
                title = SubElement(metadata, 'dcterms:title')
                title.text = tweet_date + ": tweet id " + str(tweet['id_str'])
                description = SubElement(metadata, "dcterms:description.abstract")
                description.text = "Tweet text: " + tweet['full_text']
                SubElement(metadata, 'dcterms:relation.isPartOf').text = valuables['agency'] + ' social media archive'
                SubElement(metadata, 'dcterms:bibliographicCitation').text = f"({title.text}), {valuables['preferredCitation']}"
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
                writer.close()
                id_list2.append(str(tweet['id_str']))
                #redownload the banner file and profile image just to be sure you h the current version
                profile_image_filename = baseline + "profile_image/" + tweet['user']['profile_image_url_https'].split("/")[-1]
                profile_image_url = tweet['user']['profile_image_url_https']
                if not os.path.isfile(profile_image_filename):
                    tweet_media_handler(profile_image_url, profile_image_filename)
                profile_banner_filename = baseline + "profile_banner/" + tweet['user']['profile_banner_url'].split("/")[-1]
                profile_banner_url = tweet['user']['profile_banner_url']
                if not os.path.isfile(profile_banner_filename):
                    tweet_media_handler(profile_banner_url, profile_banner_filename)
                #download the media files
                images = []
                if 'extended_entities' in tweet and tweet['extended_entities'] is not None and 'media' in tweet['extended_entities']:
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
                            media_filename = file_path1 + media['id_str'] + "_thumb." + media['media_url'].split(".")[-1]
                            tweet_media_handler(media['media_url_https'], media_filename)
                        # downloading everything else
                        else:
                            media_filename = file_path1 + media['id_str'] + "." + media['media_url'].split(".")[-1]
                            tweet_media_handler(media['media_url_https'], media_filename)
                        images.append(id)
                        # add thumbnail or downloaded image to a list so it doesn't get done twice
                if 'media' in tweet['entities']:
                    for media in tweet['entities']['media']:
                        #check list of media IDs to see if download is needed
                        if media['id_str'] not in images:
                            if media['type'] == 'photo':
                                media_filename = file_path1 + media['id_str'] + "." + media['media_url'].split(".")[-1]
                                tweet_media_handler(media['media_url_https'], media_filename)
                upload_dict = {'preservation_directory': file_path1, 'asset_title': filename[:-4], 'parent_uuid': valuables['parentFolder'],
                               'asset_tag': 'open', 'export_directory': valuables['base_location'] + "/export",
                               'asset_description': description.text, 'username': passcodes['username'], 'password': passcodes['password'],
                               'tenent': passcodes['tenancy'], 'prefix': passcodes['domain'], 'custom_type': 'Tweet',
                               'ignore': ['.metadata','.db'], 'timeframe': "2009-04"}
                if os.path.isfile(metadata_file):
                    upload_dict['metadata_file'] = metadata_file
                upload.pax_prep_withXIP(upload_dict)
            else:
                print(str(tweet['id']),"already harvested, moving on")
        upload.make_opex_directory(upload_dict)
        #document that tweet harvest/upload is finished so it won't dupe effort later
        with open(baseline + "log_tweetIDs.txt", "a") as f:
            for item in id_list2:
                f.write(item + "\n")
        f.close()

config = configparser.ConfigParser()
config.read("/media/sf_Z_DRIVE/Working/social/social_monster/credentials/secrets.txt")
passcodes = {'tenancy': config.get('social_monster_keys',"preservica_tenancy"),
             'domain': config.get('social_monster_keys',"preservica_domain_prefix"),
             'username': config.get('social_monster_keys',"preservica_username"),
             'password': config.get('social_monster_keys',"preservica_password")}
tDictionary = {'twitter_consumer_key': config.get('social_monster_keys','twitter_consumer_key'),
               'twitter_consumer_secret': config.get('social_monster_keys','twitter_consumer_secret'),
               'twitter_access_token': config.get('social_monster_keys','twitter_access_token'),
               'twitter_access_token_secret': config.get('social_monster_keys','twitter_access_token_secret')}
#agency = input("agency abreviation: ")
agency = "TSLAC"
#agency_full = input("agency full name: ")
agency_full = "Texast State Library and Archives Commission"
#collectionName = input("name of the collection going to: ")
collectionName = "tslac social media archive"
#preferredCitation = input("root citation: ")
preferredCitation = "Texas State Library and Archives Commission Social Media, Archives and Information Services Division, Texas State Library and Archives Commission."
#timeline = input("year or year-month of the backlog upload: ")
timeline = "2019"
#source_file = input("full filepath to the backlog data, not the .js file: ")
source_file = "//media/sf_Z_DRIVE/Working/social/twitter/twitter_tslac/data"
#parentFolder = input("parentFolder UUID: ")
parentFolder = "0497cb11-bc80-42b9-bc25-790cb7d2557f"
valuables = {'agency': agency, 'agency_full_name': agency_full, 'harvestType': 'twitter', 'harvest_type': 'timeline', 'lastHarvestDate': '2021-01-01',
             'Frequency': 'Daily', 'mostRecentPostId': "", "youtube_channel_id": "", "collectionName": collectionName,
             "preferredCitation": preferredCitation, "parentFolder": parentFolder, "timeline": timeline, 'source_dir': source_file}

baselocation = '/media/sf_Z_DRIVE/Working/social/harvested/twitter'
valuables['base_location'] = baselocation
twitter_backlog(tDictionary, valuables, passcodes)
