import PySimpleGUI as sg
import zipfile
import requests
import os
import datetime
import json
# for creating the metadata file
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from collections import OrderedDict
import errno
import twitter_wall_tool


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
        filename = filename.replace('?', '')
        with open(filename, 'wb') as f:
            for chunk in tweet_media.iter_content(1024):
                f.write(chunk)
        f.close()


layout = [
    # [sg.Push(),sg.Titlebar("My Twitter Breaker tool"),sg.Push()],
    [
        sg.Push(),
        sg.Text("twitter zip file"),
        sg.In(size=(50, 1), enable_events=True, key="-File-"),
        sg.FileBrowse(file_types=(("zip files only", "*.zip"),))
    ],
    [
        sg.Push(),
        sg.Text("temporary staging location for unprocessed twitter archive"),
        sg.In(size=(50, 1), enable_events=True, key="-SourceFolder-"),
        sg.FolderBrowse()
    ],
    [
        sg.Push(),
        sg.Text("target location for processed twitter archive"),
        sg.In(size=(50, 1), enable_events=True, key="-TargetFolder-"),
        sg.FolderBrowse()
    ],
    [
        sg.Checkbox("Export Metadata?", checkbox_color="dark green",
                    tooltip="Checking this box will create sidecar metadata for each tweet compatible with TSLAC standards",
                    key='-METADATA-', enable_events=True)
    ],
    [
        sg.Text("Fill in additional metadata elements if you wish:", visible=False, key='-MOREMETADATA-')
    ],
    [
        sg.Push(),
        sg.Text("Agency Name/Abbreviation:", visible=False, key="-CREATOR_TEXT-"),
        sg.Input("", size=(50, 1), visible=False, key="-CREATOR-")
    ],
    [
        sg.Push(),
        sg.Text("Official collection name:", visible=False, key="-CITATION_TEXT-"),
        sg.Input("", size=(50, 1), visible=False, key="-CITATION-")
    ],
    [
        sg.Checkbox("Generate wall too?", checkbox_color="dark green", tooltip="Checking this box will generate a html page emulating a twitter wall which can be used to review or validate content",
                    key="-WALL-", enable_events=True)
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
        sg.Multiline(default_text="Click execute to show progress\n------------------------------\n", size=(70, 3),
                     auto_refresh=True, reroute_stdout=False, key="-OUTPUT-", autoscroll=True, border_width=5),
    ],
]

window = sg.Window(
    "Twitter breaker tool",
    layout,
    icon="Twitter_icon.png",
    button_color="dark green",

)

event, values = window.read()

while True:
    event, values = window.read()
    target_file = values['-File-']
    source_folder = values['-SourceFolder-']
    target_folder = values['-TargetFolder-']
    metadata_generator = values['-METADATA-']
    metadata_creator = values['-CREATOR-']
    metadata_citation = values['-CITATION-']
    wall = values['-WALL-']
    if metadata_generator is True:
        window['-MOREMETADATA-'].update(visible=True)
        window['-CREATOR_TEXT-'].update(visible=True)
        window['-CREATOR-'].update(visible=True)
        window['-CITATION_TEXT-'].update(visible=True)
        window['-CITATION-'].update(visible=True)
    if metadata_generator is False:
        window['-MOREMETADATA-'].update(visible=False)
        window['-CREATOR_TEXT-'].update(visible=False)
        window['-CREATOR-'].update(visible=False)
        window['-CITATION_TEXT-'].update(visible=False)
        window['-CITATION-'].update(visible=False)
    if event == "Execute":
        if target_file != "" and target_folder != "" and source_folder != "":
            window['-OUTPUT-'].update(f"your zip file is {target_file}\n", append=True)
            window['-OUTPUT-'].update(f"your temp folder is located at {source_folder}\n", append=True)
            window['-OUTPUT-'].update(f"your final processed archive will be at {target_folder}\n", append=True)
            window['-OUTPUT-'].update(f"executing...\n")
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
            # twitter_backlog(valuables)
            if wall is True:
                window['-OUTPUT-'].update("\ngenerating twitter wall html page", append=True)
                twitter_wall_tool.wall_tool(target_folder)
            window['-OUTPUT-'].update("\nall done, click on Close to exit", append=True)
        else:
            window['-STATUS-'].update("Need more data, fill in the proper elements\n", text_color="orchid1",
                                      font=("Calibri", "12", "bold"))
            # print("\nneed more data, fill in the proper elements")
    if event == "Close" or event == sg.WIN_CLOSED:
        break
window.close()
