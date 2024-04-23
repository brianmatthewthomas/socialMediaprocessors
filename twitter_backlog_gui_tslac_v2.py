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

def split_hashtag(text_block):
    tag_list = []
    my_tags = text_block.split(" #")
    if len(my_tags) > 1:
        for item in my_tags[1:]:
            item = item.split(" ")
            if len(item[0]) > 1:
                tag_list.append(item[0])
    my_tags = text_block.split("\n#")
    if len(my_tags) > 1:
        for item in my_tags[1:]:
            item = item.split(" ")[0]
            if item not in tag_list:
                tag_list.append(item)
    tag_list.sort()
    return tag_list

def split_mention(text_block):
    tag_list = []
    my_tags = text_block.split(" @")
    if len(my_tags) > 1:
        for item in my_tags:
            if item.startswith("["):
                item = item.split("]")[0]
                item = item.split(":")[-1]
                tag_list.append(item)
    my_tags = text_block.split("\n@")
    if len(my_tags) > 1:
        for item in my_tags[1:]:
            if item.startswith("["):
                item = item.split("]")[0]
                item = item.split(":")[-1]
                if item not in tag_list:
                    tag_list.append(item)
    tag_list.sort()
    return tag_list

def prettify(elem):
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparse = minidom.parseString(rough_string)
    return reparse.toprettyxml(indent="    ")

def pax_prep_withXIP(valuables):
    # a simpler version of the multi-upload to handle cases where a pax is simply preservation files
    # unpack the dictionary to individual variables
    preservation_directory = valuables['preservation_directory']
    asset_title = valuables['asset_title']
    parent_uuid = valuables['parent_uuid']
    asset_tag = valuables['asset_tag']
    export_dir = valuables['export_directory']
    # set description, fallback to title if missing from dictionary
    if valuables['asset_description']:
        if valuables['asset_description'] != None and valuables['asset_description'] != "":
            asset_description = valuables['asset_description']
        else:
            asset_description = valuables['asset_title']
    else:
        asset_description = valuables['asset_title']
    # initiate creating xml file
    xip = Element('XIP')
    xip.set('xmlns', f'http://preservica.com/XIP/v{valuables["version"]}')
    io = SubElement(xip, 'InformationObject')
    ref = SubElement(io, 'Ref')
    ref.text = str(uuid.uuid4())
    valuables['asset_id'] = ref.text
    asset_id = valuables['asset_id']
    title = SubElement(io, 'Title')
    title.text = asset_title
    description = SubElement(io, 'Description')
    description.text = asset_description
    security = SubElement(io, 'SecurityTag')
    security.text = asset_tag
    custom_type = SubElement(io, 'CustomType')
    if valuables['custom_type']:
        custom_type.text = valuables['custom_type']
    else:
        custom_type.text = ""
    parent = SubElement(io, 'Parent')
    parent.text = parent_uuid
    # copy the files to the export area for processing
    preservation_representation = os.path.join(export_dir, asset_title, "Representation_Preservation")
    for dirpath, dirnames, filenames in os.walk(preservation_directory):
        for filename in filenames:
            if not filename.endswith(tuple(valuables['ignore'])):
                filename1 = os.path.join(dirpath, filename)
                checksum1 = create_sha256(filename1)
                filename2 = os.path.join(preservation_representation, filename.split(".")[0], filename)
                create_directory(filename2)
                shutil.copyfile(filename1, filename2)
                checksum2 = create_sha256(filename2)
                if checksum1 == checksum2:
                    print("copy of", filename, "verified, continuing")
                else:
                    print("error in copying of", filename, "... exiting, try again")
                    sys.exit()
    # start creating the representations, content objects and bitstreams
    preservation_refs_dict = {}
    if preservation_representation:
        preservation_refs_dict = make_representation(xip, "Preservation", "Preservation", preservation_directory,
                                                     asset_id, valuables)
    if preservation_refs_dict:
        make_content_objects(xip, preservation_refs_dict, asset_id, asset_tag, "", custom_type.text)
    if preservation_refs_dict:
        make_generation(xip, preservation_refs_dict, "Preservation1")
    if preservation_representation:
        make_bitstream(xip, preservation_refs_dict, preservation_directory, "Preservation1",
                       preservation_representation, custom_type.text)
    pax_folder = export_dir + "/" + asset_title
    # currently unable to get xip to work with preservica ingest, uncomment the 4 lines below if/when it starts working
    pax_file = pax_folder + "/" + asset_title + ".xip"
    metadata = open(pax_file, "wt", encoding='utf-8')
    metadata.write(prettify(xip))
    metadata.close()
    tempy = export_dir + "/" + valuables['timeframe']
    os.makedirs(tempy, exist_ok=True)
    archive_name = export_dir + "/" + asset_title + ".pax"
    shutil.make_archive(archive_name, "zip", pax_folder)
    archive_name = archive_name + ".zip"
    archive_name2 = archive_name.replace(export_dir, tempy)
    shutil.move(archive_name, archive_name2)
    make_opex(valuables, archive_name2)

def make_opex(valuables, filename2):
    opex = Element('opex:OPEXMetadata', {'xmlns:opex': 'http://www.openpreservationexchange.org/opex/v1.0'})
    opexTransfer = SubElement(opex, "opex:Transfer")
    opexSource = SubElement(opexTransfer, "opex:SourceID")
    opexSource.text = valuables["asset_id"]
    opexFixities = SubElement(opexTransfer, "opex:Fixities")
    opexSHA256 = create_sha256(filename2)
    opexFixity = SubElement(opexFixities, "opex:Fixity", {'type': 'SHA-256', 'value': opexSHA256})
    opex_properties = SubElement(opex, 'opex:Properties')
    opex_title = SubElement(opex_properties, 'opex:Title')
    opex_title.text = valuables['asset_title']
    opex_description = SubElement(opex_properties, 'opex:Description')
    if valuables['asset_description'] not in valuables.keys():
        valuables['asset_description'] = valuables['asset_title']
    opex_description.text = valuables['asset_description']
    opex_security = SubElement(opex_properties, 'opex:SecurityDescriptor')
    opex_security.text = valuables['asset_tag']
    if 'metadata_file' in valuables.keys():
        opex_metadata = SubElement(opex, 'opex:DescriptiveMetadata')
        opex_metadata.text = "This is where the metadata goes"
    export_file = valuables['export_directory'] + "/" + valuables['timeframe'] + "/" + valuables[
        'asset_title'] + ".pax.zip.opex"
    opex_output = open(export_file, "w", encoding='utf-8')
    opex_output.write(prettify(opex))
    opex_output.close()
    if 'metadata_file' in valuables.keys():
        with open(valuables['metadata_file'], 'r') as f:
            filedata = f.read()
            filedata = filedata.replace('<?xml version="1.0" encoding="UTF-8"?>', "")
            filedata = filedata.replace('<?xml version="1.0" ?>', '')
            with open(export_file, "r") as r:
                fileinfo = r.read()
                fileinfo = fileinfo.replace("This is where the metadata goes", filedata)
                with open(export_file, "w") as w:
                    w.write(fileinfo)
                    w.close()

def make_opex_directory(valuables):
    export_directory = valuables['export_directory'] + "/" + valuables['timeframe']
    filelist = []
    for dirpath, dirnames, filenames in os.walk(export_directory):
        for filename in filenames:
            if not filename.endswith(".opex"):
                filelist.append(filename)
    opex = Element('opex:OPEXMetadata', {'xmlns:opex': 'http://www.openpreservationexchange.org/opex/v1.0'})
    opexTransfer = SubElement(opex, "opex:Transfer")
    opexSource = SubElement(opexTransfer, "opex:SourceID")
    opexSource.text = str(uuid.uuid4())
    '''opexManifest = SubElement(opexTransfer, "opex:Manifest")
    opexFiles = SubElement(opexManifest, "opex:Files")
    for item in filelist:
        opexFile = SubElement(opexFiles, "opex:File")
        opexFile.text = item'''
    export_file = valuables['export_directory'] + "/" + valuables['timeframe'] + "/" + valuables['timeframe'] + ".opex"
    opex_output = open(export_file, "w", encoding='utf-8')
    opex_output.write(prettify(opex))
    opex_output.close()
    compiled_opex = valuables['export_directory'] + "/" + valuables['timeframe']
    shutil.make_archive(compiled_opex, "zip", compiled_opex)
    compiled_opex = compiled_opex + ".zip"
    valuables['compiled_opex'] = compiled_opex
    print("uploading", valuables['timeframe'])
    valuables['asset_id'] = valuables['timeframe']

def make_representation(xip, rep_name, rep_type, path, io_ref, valuables):
    representation = SubElement(xip, 'Representation')
    io_link = SubElement(representation, "InformationObject")
    io_link.text = io_ref
    access_name = SubElement(representation, 'Name')
    access_name.text = rep_name
    access_type = SubElement(representation, 'Type')
    access_type.text = rep_type
    content_objects = SubElement(representation, 'ContentObjects')
    rep_files = [f for f in listdir(path) if isfile(join(path, f))]
    rep_files.sort(key=len, reverse=True)
    refs_dict = {}
    counter = 0
    for f in rep_files:
        if not f.endswith(tuple(valuables['ignore'])):
            content_object = SubElement(content_objects, 'ContentObject')
            content_object_ref = str(uuid.uuid4())
            content_object.text = content_object_ref
            refs_dict[f] = content_object_ref
            counter += 1
    return refs_dict

def make_content_objects(xip, refs_dict, io_ref, tag, content_description, content_type):
    for filename, ref in refs_dict.items():
        content_object = SubElement(xip, 'ContentObject')
        ref_element = SubElement(content_object, 'Ref')
        ref_element.text = ref
        title = SubElement(content_object, 'Title')
        if filename.split(".")[-1] == "srt":
            title.text = "English"
        elif filename.endswith(tuple(["mp4", "m4v", "mov"])):
            title.text = "Movie"
        elif content_type == "Tweet":
            placeholder = filename.split("_")
            for item in placeholder:
                if len(item) > 11:
                    item = item.split(".")[0]
                    filename = filename.replace(item, "{" + item + "}")
            title.text = filename
        else:
            title.text = os.path.splitext(filename)[0]
        description = SubElement(content_object, "Description")
        description.text = content_description
        security_tag = SubElement(content_object, "SecurityTag")
        security_tag.text = tag
        custom_type = SubElement(content_object, "CustomType")
        custom_type.text = content_type
        parent = SubElement(content_object, "Parent")
        parent.text = io_ref

def make_generation(xip, refs_dict, generation_label):
    for filename, ref in refs_dict.items():
        generation = SubElement(xip, 'Generation', {"original": "true", "active": "true"})
        content_object = SubElement(generation, "ContentObject")
        content_object.text = ref
        label = SubElement(generation, "Label")
        if generation_label:
            label.text = generation_label
        else:
            label.text = os.path.splitext(filename)[1]
        effective_date = SubElement(generation, "EffectiveDate")
        effective_date.text = datetime.datetime.now().isoformat()[:-7] + "Z"
        bitstreams = SubElement(generation, "Bitstreams")
        bitstream = SubElement(bitstreams, "Bitstream")
        bitstream.text = "Representation_" + generation_label[:-1] + "/" + filename.split(".")[0] + "/" + filename
        SubElement(generation, "Formats")
        SubElement(generation, "Properties")

def make_bitstream(xip, refs_dict, root_path, generation_label, representation_location, content_type):
    for filename, ref in refs_dict.items():
        bitstream = SubElement(xip, "Bitstream")
        filenameElement = SubElement(bitstream, "Filename")
        filenameElement.text = filename
        filesize = SubElement(bitstream, "FileSize")
        fullPath = os.path.join(root_path, filename)
        file_stats = os.stat(fullPath)
        filesize.text = str(file_stats.st_size)
        physloc = SubElement(bitstream, "PhysicalLocation")
        physloc.text = "Representation_" + generation_label[:-1] + "/" + filename.split(".")[0]
        if content_type == "Tweet":
            placeholder = filename.split("_")
            for item in placeholder:
                if len(item) > 11:
                    item = item.split(".")[0]
                    turtle = filename.replace(item, "{" + item + "}[tslac]")
            SubElement(bitstream, 'OriginalFilename').text = turtle
        fixities = SubElement(bitstream, "Fixities")
        fixity = SubElement(fixities, "Fixity")
        fixityAlgorithmRef = SubElement(fixity, "FixityAlgorithmRef")
        fixityAlgorithmRef.text = "SHA256"
        fixityValue = SubElement(fixity, "FixityValue")
        fixityValue.text = create_sha256(fullPath)

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

def tweet_handler():
    print("something")

layout = [
    # [sg.Push(),sg.Titlebar("My Twitter Breaker tool"),sg.Push()],
    [
        sg.Radio("Twitter", group_id="media_type", key='-TYPE_twitter-'),
        sg.Radio("Facebook page", group_id="media_type", key="-TYPE_facebook_page-")
    ],
    [
        sg.Push(),
        sg.Text("social media zip file"),
        sg.In("", key="-File-"), #sg.In(size=(50, 1), enable_events=True, key="-File-"),
        sg.FileBrowse(file_types=(("zip files only", "*.zip"),))
    ],
    [
        sg.Push(),
        sg.Text("temporary staging location for unprocessed social media archive"),
        sg.In("", key="-SourceFolder-"), #sg.In(size=(50, 1), enable_events=True, key="-SourceFolder-"),
        sg.FolderBrowse()
    ],
    [
        sg.Push(),
        sg.Text("target location for processed social media archive"),
        sg.In("", key="-TargetFolder-"), #sg.In(size=(50, 1), enable_events=True, key="-TargetFolder-"),
        sg.FolderBrowse()
    ],
    [
        sg.Push(),
        sg.Text("upload staging location"),
        sg.In("", key="-UploadStaging-"), #sg.In(size=(50, 1), enable_events=True, key="-UploadStaging-"),
        sg.FolderBrowse()
    ],
    [
        sg.Checkbox("Export Metadata?", checkbox_color="dark green",
                    tooltip="Checking this box will create sidecar metadata for each post compatible with TSLAC standards",
                    key='-METADATA-', enable_events=True)
    ],
    [
        sg.Text("Fill in additional metadata elements if you wish:", key='-MOREMETADATA-')
    ],
    [
        sg.Push(),
        sg.Text("Agency Name/Abbreviation:", key="-CREATOR_TEXT-"),
        sg.Input("tslac", size=(50, 1), key="-CREATOR-")
    ],
    [
        sg.Push(),
        sg.Text("Official collection name:", key="-CITATION_TEXT-"),
        sg.Input("Social Media Test", size=(50, 1), key="-CITATION-")
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
        sg.Multiline(default_text="Click execute to show progress\n------------------------------\n", size=(100, 6),
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
    target_file = "/media/sf_Z_DRIVE/Working/research/socialMedia/facebook/facebook-tslac-2024-04-08-Hn2tG4Jj.zip" #values['-File-']
    source_folder = "/media/sf_Z_DRIVE/Working/research/socialMedia/facebook/facebook-tslac-2024-04-08-Hn2tG4Jj" #values['-SourceFolder-']
    target_folder = "/media/sf_Z_DRIVE/Working/research/socialMedia/facebook/tslac_test" #values['-TargetFolder-']
    upload_folder = f"{target_folder}_upload"
    metadata_generator = values['-METADATA-']
    metadata_creator = values['-CREATOR-']
    metadata_citation = values['-CITATION-']
    collectionName = values['-CITATION-']
    wall = values['-WALL-']
    if event == "Execute":
        upload_list = set()
        year_list = set()
        if target_file != "" and target_folder != "" and source_folder != "":
            window['-OUTPUT-'].update(f"your zip file is {target_file}\n", append=True)
            window['-OUTPUT-'].update(f"your temp folder is located at {source_folder}\n", append=True)
            window['-OUTPUT-'].update(f"your final processed archive will be at {target_folder}\n", append=True)
            window['-OUTPUT-'].update(f"executing...\n")
            if values['-TYPE_twitter-'] is True:
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
                window['-OUTPUT-'].update("\nall done, click on Close to exit", append=True)
            if values['-TYPE_facebook_page-'] is True:
                my_precious = f"{source_folder}/logged_information/professional_dashboard/your_professional_dashboard_activity.json"
                if os.path.isfile(my_precious):
                    window['-OUTPUT-'].update("facebook archive already extracted, moving on\n", append=True)
                if not os.path.isfile(my_precious):
                    window['-OUTPUT-'].update("extracting facebook archive for manipulation\n", append=True)
                    crazy = zipfile.ZipFile(target_file)
                    crazy.extractall(source_folder)
                window['-OUTPUT-'].update("processing facebook posts\n", append=True)
                window['-STATUS-'].update(
                    "Go get a cup of coffee, you deserve it. Press ctrl+c in the terminal window to stop processing.\n",
                    text_color="green2")
                valuables = {}
                if metadata_citation != "":
                    valuables['preferredCitation'] = f"{metadata_citation}. Archives and Information Services Division, Texas State Library and Archives Commission."
                if metadata_creator != "":
                    valuables['agency'] = metadata_creator
                valuables['base_location'] = target_folder
                valuables['source_dir'] = source_folder
                print("starting the process")
                log = open("logger.txt", "a")
                id_list = []
                baseline = f"{valuables['base_location']}/"
                fb_log = f"{baseline}/log_facebooksIDs.txt"
                if not os.path.isfile(fb_log):
                    create_directory(fb_log)
                    with open(fb_log, "a") as w:
                        print("facebook log file created")
                    w.close()
                with open(fb_log, "r") as r:
                    for line in r:
                        id_list.append(line[:-1])
                r.close()
                print("list of existing posts compiled")
                id_list2 = []
                # begin creation of user info for json output
                user_data_file = f"{valuables['source_dir']}/logged_information/professional_dashboard/your_professional_dashboard_activity.json"
                user_data = {}
                with open(user_data_file, "r") as data:
                    json_data = data.read()
                    user = json.loads(json_data)
                    print(user)
                    # get username for getting userid
                    username = user['prodash_activity'][0]['page_name']
                    user_data['name'] = username
                    user_data['screen_name'] = username
                user_id_options = [f"{valuables['source_dir']}/this_profile's_activity_across_facebook/posts/profile_posts_1.json",
                                   f"{valuables['source_dir']}/this_profile's_activity_across_facebook/events/events.json",
                                   f"{valuables['source_dir']}/this_profile's_activity_across_facebook/posts/videos.json",
                                   f"{valuables['source_dir']}/this_profile's_activity_across_facebook/comments_and_reactions/comments.json"
                                   ]
                user_id = ""
                user_id_int = ""
                while user_id == "" and user_id_int == "":
                    for option in user_id_options:
                        if os.path.isfile(option):
                            with open(option, "r") as r:
                                filedata = r.read()
                                filedata = filedata.split(f":274:{username}]")
                                if len(filedata) > 1:
                                    user_id = filedata[0].split("@[")[-1]
                                    user_id_int = int(user_id)
                    if user_id == "" and user_id_int == "":
                        sys.exit()
                user_data['id'] = user_id_int
                user_data['id_str'] = user_id
                print(user_data)
                print("account data and profile data loaded")
                my_precious_posts = f"{source_folder}/this_profile's_activity_across_facebook/posts"
                my_precious_albums = f"{source_folder}/this_profile's_activity_across_facebook/posts/album"
                my_precious_events = f"{source_folder}/this_profile's_activity_across_facebook/events"
                my_precious_posts_list = [f for f in os.listdir(my_precious_posts) if os.path.isfile(f"{my_precious_posts}/{f}") and "facebook_editor" not in f]
                my_precious_album_list = [f for f in os.listdir(my_precious_albums) if os.path.isfile(f'{my_precious_albums}/{f}')]
                my_precious_event_list = ["events.json"]
                blank_post = {}
                blank_metadata = {}
                '''
                for preciouses in my_precious_event_list:
                    with (open(f"{my_precious_events}/{preciouses}", "r") as backlog):
                        json_data = backlog.read()
                        facebook = json.loads(json_data)
                        facebook = facebook['your_events_v2']
                        counter = 0
                        total = len(facebook)
                        blank_post = {}
                        blank_metadata = {}
                        for post in facebook:
                            counter += 1
                            new_post = blank_post
                            metadata_dictionary = blank_metadata
                            window['-Progress-'].update_bar(counter, total)
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
                                metadata_dictionary['post_id'] = str(post_id)
                                metadata_dictionary['create_date'] = date_created
                                start_date_date = start_date.split(" ")
                                end_date_date = end_date.split(" ")
                                if start_date_date[0] == end_date_date[0]:
                                    date_in_title = f"{start_date_date[0]} {start_date_date[1][:-3]} thru {end_date_date[1][:-3]}"
                                else:
                                    date_in_title = f"{start_date[:-3]} thru {end_date}"
                                title = f"{date_in_title}: {post['name']}"
                                metadata_dictionary['title'] = title
                                place_name = "unspecified location"
                                if "place" in post.keys():
                                    place_name = post['place']['name']
                                description = "no additional information provided."
                                if "description" in post.keys():
                                    description = post['description']
                                description = f"{post['name']} event at {place_name}: {description}"
                                metadata_dictionary['description'] = description
                                metadata_dictionary['type'] = "Facebook events"
                                metadata_dictionary['platform'] = "Facebook"
                                metadata_dictionary['agency'] = valuables['agency']
                                metadata_dictionary['username'] = username
                                metadata_dictionary['citation'] = f"{title}, {username} page, Facebook, {valuables['preferredCitation']}"
                                metadata_dictionary['creator'] = username
                                metadata_dictionary['hashtags'] = []
                                metadata_dictionary['mentions'] = []
                                if "#" in description:
                                    metadata_dictionary['hashtags'] = split_hashtag(description)
                                if "@" in description:
                                    metadata_dictionary['mentions'] = split_mention(description)
                                filepath1 = f"{baseline}/backlog/events/{post_id[:4]}/{post_id}/"
                                upload_list.add(filepath1)
                                year_list.add(post_id[:4])
                                filename = f"{post_id}.txt"
                                master_post = f"{filepath1}/preservation1/{filename}"
                                normalized_post = f"{filepath1}/preservation2/{filename}"
                                if not os.path.exists(os.path.dirname(master_post)):
                                    create_directory(master_post)
                                if not os.path.exists(os.path.dirname(normalized_post)):
                                    create_directory(normalized_post)
                                post['user'] = user_data
                                # save the post file for now
                                master_post_text = json.loads(json.dumps(post))
                                with open(master_post, "w") as w:
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
                                                target_media = f"{filepath1}/preservation1/{media}"
                                                shutil.copy2(source_media, target_media)
                                                shutil.copystat(source_media, target_media)
                                if metadata_generator is True:
                                    metadata_dictionary = make_metadata(metadata_dictionary)
                                    metadata_file = f"{master_post[:-3]}json.metadata"
                                    with open(metadata_file, "wt", encoding='utf-8') as w:
                                        w.write(prettify(metadata_dictionary))
                                    w.close()

                for preciouses in my_precious_album_list:
                    with open(f"{my_precious_albums}/{preciouses}", "r") as backlog:
                        json_data = backlog.read()
                        print(f"album {preciouses}")
                        facebook = json.loads(json_data)
                        counter = 0
                        total = len(facebook['photos'])
                        blank_post = {}
                        blank_metadata = {}
                        # process album post data
                        new_post = blank_post
                        metadata_dictionary = blank_metadata
                        text_string = ""
                        timestamp = facebook['last_modified_timestamp']
                        timestamp_translated = f"{str(datetime.datetime.fromtimestamp(timestamp))}"
                        post_id = f"{str(timestamp_translated)[:10]}_{str(timestamp)}"
                        date_created = str(timestamp_translated)[:10]
                        print(post_id)
                        metadata_dictionary['post_id'] = str(post_id)
                        metadata_dictionary['create_date'] = date_created
                        title = f"{date_created}, {facebook['name']} Album cover"
                        metadata_dictionary['title'] = title
                        if "description" in facebook.keys():
                            description = facebook['description']
                        if description == "":
                            description = "No description available"
                        description = f"{title}: {description}"
                        metadata_dictionary['description'] = description
                        metadata_dictionary['type'] = "Facebook albums"
                        metadata_dictionary['platform'] = "Facebook"
                        metadata_dictionary['agency'] = valuables['agency']
                        metadata_dictionary['username'] = username
                        metadata_dictionary['citation'] = f"{title}, {username} page, {valuables['preferredCitation']}"
                        metadata_dictionary['creator'] = username
                        metadata_dictionary['hashtags'] = []
                        metadata_dictionary['mentions'] = []
                        if "#" in description:
                            metadata_dictionary['hashtags'] = split_hashtag(description)
                        if "@" in description:
                            metadata_dictionary['mentions'] = split_mention(description)
                        master_filepath = f"{baseline}/backlog/albums/album{preciouses[:-5]}"
                        master_filepath_metadata = f"{master_filepath}/{master_filepath.split('/')[-1]}.metadata"
                        if not os.path.exists(os.path.dirname(master_filepath_metadata)):
                            create_directory(master_filepath_metadata)
                        master_metadata = metadata_dictionary
                        master_metadata['title'] = title[:-6]
                        master_metadata = make_metadata(master_metadata)
                        with open(master_filepath_metadata, 'wt', encoding='utf-8') as w:
                            w.write(prettify(master_metadata))
                        w.close()
                        album_root_filepath = f"{master_filepath}/{post_id}"
                        filename = f"{post_id}.txt"
                        master_post = f"{album_root_filepath}/preservation1/{filename}"
                        normalized_post = f"{album_root_filepath}/preservation2/{filename}"
                        if not os.path.exists(os.path.dirname(master_post)):
                            create_directory(master_post)
                        if not os.path.exists(os.path.dirname(normalized_post)):
                            create_directory(normalized_post)
                        facebook['user'] = user_data
                        master_post_text = json.loads(json.dumps(facebook))
                        with open(master_post, "w") as w:
                            json.dump(master_post_text, w)
                        w.close()
                        os.rename(master_post, f"{master_post[:-3]}json")
                        metadata_dictionary['title'] = title
                        metadata_dictionary = make_metadata(metadata_dictionary)
                        metadata_file = f"{master_post[:-3]}json.metadata"
                        with open(metadata_file, 'wt', encoding='utf-8') as w:
                            w.write(prettify(metadata_dictionary))
                        w.close()
                        if "cover_photo" in facebook.keys():
                            cover_photo = f"{valuables['source_dir']}/{facebook['cover_photo']['uri']}"
                            cover_photo_target = f"{album_root_filepath}/preservation1/{facebook['cover_photo']['uri'].split('/')[-1]}"
                            shutil.copy2(cover_photo, cover_photo_target)
                            shutil.copystat(cover_photo, cover_photo_target)
                        posts = facebook['photos']
                        counter = 0
                        total = len(posts)
                        root_post_id = post_id
                        for post in posts:
                            counter += 1
                            new_post = blank_post
                            metadata_dictionary = blank_metadata
                            window['-Progress-'].update_bar(counter, total)
                            post['user'] = user_data
                            text_string = ""
                            timestamp = post['creation_timestamp']
                            date_created = str(datetime.datetime.fromtimestamp(timestamp))[:10]
                            post_id = f"{date_created}_{str(timestamp)}"
                            filename = f"{post_id}.txt"
                            if post_id not in id_list:
                                master_post = f"{master_filepath}/{post_id}/preservation1/{filename}"
                                normalized_post = f"{master_filepath}/{post_id}/preservation2/{filename}"
                                if not os.path.exists(os.path.dirname(master_post)):
                                    create_directory(master_post)
                                if not os.path.exists(os.path.dirname(normalized_post)):
                                    create_directory(normalized_post)
                                post['user'] = user_data
                                master_post_text = json.loads(json.dumps(post))
                                with open(master_post, "w") as w:
                                    json.dump(master_post_text, w)
                                w.close()
                                os.rename(master_post, f"{master_post[:-3]}json")
                                photo = f"{valuables['source_dir']}/{post['uri']}"
                                photo_target = f"{master_filepath}/{post_id}/preservation1/{post['uri'].split('/')[-1]}"
                                shutil.copy2(photo, photo_target)
                                shutil.copystat(photo, photo_target)
                                metadata_dictionary['post_id'] = str(post_id)
                                metadata_dictionary['create_date'] = date_created
                                title = f"{date_created}, {post['title']} photograph"
                                metadata_dictionary['title'] = title
                                description = ""
                                if "description" in post.keys():
                                    description = post['description']
                                if description == "":
                                    description = "No description available"
                                description = f"{title}: {description}"
                                metadata_dictionary['description'] = description
                                metadata_dictionary['type'] = "Facebook albums"
                                metadata_dictionary['platform'] = 'Facebook'
                                metadata_dictionary['agency'] = valuables['agency']
                                metadata_dictionary['username'] = username
                                metadata_dictionary['citation'] = f"{title}, {username} page, {valuables['preferredCitation']}"
                                metadata_dictionary['creator'] = username
                                metadata_dictionary['hashtags'] = []
                                metadata_dictionary['mentions'] = []
                                if "#" in description:
                                    metadata_dictionary['hashtags'] = split_hashtag(description)
                                if "@" in description:
                                    metadata_dictionary['mentions'] = split_mention(description)
                                master_metadata = f"{master_post[:-3]}json.metadata"
                                metadata_dictionary = make_metadata(metadata_dictionary)
                                with open(master_metadata, 'wt', encoding='utf-8') as w:
                                    w.write(prettify(metadata_dictionary))
                                w.close()
                '''
                # start plain old posts
                print(my_precious_posts_list)
                image_list = []
                for preciouses in my_precious_posts_list:
                    with open(f"{my_precious_posts}/{preciouses}", "r") as backlog:
                        json_data = backlog.read()
                        facebook = json.loads(json_data)
                        print(type(facebook))
                        if isinstance(facebook, dict) is True:
                            print(preciouses)
                            if "videos_v2" in facebook.keys():
                                facebook = facebook['videos_v2']
                                print(facebook[:50])

                            elif "other_photos_v2" in facebook.keys():
                                facebook = facebook['other_photos_v2']
                                print(facebook[:50])
                            for post in facebook:
                                new_post = blank_post
                                metadata_dictionary = blank_metadata
                                text_string = ""
                                timestamp = post['creation_timestamp']
                                date_created = str(datetime.datetime.fromtimestamp(timestamp))[:10]
                                post_id = f"{date_created}_{str(timestamp)}"
                                if post_id not in id_list:
                                    filename = f"{post_id}.txt"
                                    year = date_created[:4]
                                    master_post = f"{baseline}/backlog/posts/{year}/{post_id}/preservation1/{filename}"
                                    normalized_post = f"{baseline}/backlog/posts/{year}/{post_id}/presentation2/{filename}"
                                    if not os.path.exists(os.path.dirname(master_post)):
                                        create_directory(master_post)
                                    if not os.path.exists(os.path.dirname(normalized_post)):
                                        create_directory(normalized_post)
                                    post['user'] = user_data
                                    master_post_text = json.loads(json.dumps(post))
                                    with open(master_post, "w") as w:
                                        json.dump(master_post_text, w)
                                    w.close()
                                    os.rename(master_post, f"{master_post[:-3]}json")
                                    media = f"{valuables['source_dir']}/{post['uri']}"
                                    media_filename = post['uri'].split("/")[-1]
                                    image_list.append(media_filename)
                                    media_target = f"{baseline}/backlog/posts/{year}/{post_id}/preservation1/{media_filename}"
                                    shutil.copy2(media, media_target)
                                    shutil.copystat(media, media_target)
                                    metadata_dictionary['post_id'] = str(post_id)
                                    metadata_dictionary['create_date'] = date_created
                                    title = ""
                                    if "title" in post.keys():
                                        if post['title'] != "":
                                            title = f", {post['title']}"
                                    title = f"{date_created}: {post_id}{title}"
                                    metadata_dictionary['title'] = title
                                    description = ""
                                    if "description" in post.keys():
                                        description = post['description']
                                    if description == "":
                                        description = "No description available"
                                    description = f"{title}: {description}"
                                    metadata_dictionary['description'] = description
                                    metadata_dictionary['type'] = 'Facebook post'
                                    metadata_dictionary['platform'] = "Facebook"
                                    metadata_dictionary['agency'] = valuables['agency']
                                    metadata_dictionary['username'] = username
                                    metadata_dictionary['citation'] = f"{title} page, {valuables['preferredCitation']}"
                                    metadata_dictionary['creator'] = username
                                    metadata_dictionary['hashtags'] = []
                                    metadata_dictionary['mentions'] = []
                                    if "#" in description:
                                        metadata_dictionary['hashtags'] = split_hashtag(description)
                                    if "@" in description:
                                        metadata_dictionary['mentions'] = split_mention(description)
                                    master_metadata = f"{master_post[:-3]}json.metadata"
                                    metadata_dictionary = make_metadata(metadata_dictionary)
                                    with open(master_metadata, 'wt', encoding='utf-8') as w:
                                        w.write(prettify(metadata_dictionary))
                                    w.close()
                        else:
                            for post in facebook:
                                new_post = blank_post
                                metadata_dictionary = blank_metadata
                                text_string = ""
                                timestamp = post['timestamp']
                                date_created = str(datetime.datetime.fromtimestamp(timestamp))[:10]
                                post_id = f"{date_created}_{str(timestamp)}"
                                if post_id not in id_list:
                                    filename = f"{post_id}.txt"
                                    year = date_created[:4]
                                    master_post = f"{baseline}/backlog/posts/{year}/{post_id}/preservation1/{filename}"
                                    normalized_post = f"{baseline}/backlog/posts/{year}/{post_id}/presentation2/{filename}"
                                    if not os.path.exists(os.path.dirname(master_post)):
                                        create_directory(master_post)
                                    if not os.path.exists(os.path.dirname(normalized_post)):
                                        create_directory(normalized_post)
                                    post['user'] = user_data
                                    master_post_text = json.loads(json.dumps(post))
                                    counters = 0
                                    description = "No description available"
                                    if "post" in post['data'][0]:
                                        description = post['data'][0]['post']
                                    if "attachments" in post.keys():
                                        for attachments in post['attachments']:
                                            attachment = attachments['data']
                                            for x in attachment:
                                                if "media" in x.keys():
                                                    if "description" in x['media'].keys():
                                                        if x['media']['description'] == "" or x['media']['description'] == description:
                                                            print(f"{post_id} is awesome")








                sys.exit()
                '''
                        counter = 0
                        total = len(facebook)
                        blank_post = {}
                        for post in facebook:
                            #print(post)
                            text_string = ""
                            master_date = f"{str(datetime.datetime.fromtimestamp(post['timestamp']))}"
                            #print(master_date)
                            post_id = f"{str(master_date)[:10]}_{str(post['timestamp'])}"
                            if post_id not in id_list:
                                file_path1 = f"{baseline}/backlog/{str(master_date)[:4]}/{str(master_date)[:10]}_{str(post['timestamp'])}/"
                                upload_list.add(file_path1)
                                year_list.add(str(master_date)[:4])
                                filename = f"{str(master_date)[:10]}_{str(post['timestamp'])}.txt"
                                master_post = f"{file_path1}/preservation1/{filename}"
                                normalized_post = f"{file_path1}/presentation2/{filename}"
                                if not os.path.exists(os.path.dirname(master_post)):
                                    os.makedirs(os.path.dirname(master_post), exist_ok=True)
                                if not os.path.exists(os.path.dirname(normalized_post)):
                                    os.makedirs(os.path.dirname(normalized_post), exist_ok=True)
                                my_datas = post['data']
                                for a_data in my_datas:
                                    keys = a_data.keys()
                                    for key in keys:
                                        text_string = f"{text_string}{a_data[key]} "
                                text_string = text_string[:-1]
                                #print(text_string)
                                #new_post['created_at'] = str(datetime.datetime.fromtimestamp(post['timestamp']))
                                new_post['created_at'] = str(datetime.datetime.fromtimestamp(post['timestamp']).ctime())
                                if "+" not in new_post['created_at']:
                                    new_post['created_at'] = new_post['created_at'][:-4] + "+0000 " + new_post['created_at'][-4:]
                                new_post['id_str'] = f"{user_data['id']}.{str(post['timestamp'])}"
                                new_post['id'] = float(new_post['id_str'])
                                new_post['full_text'] = ""
                                url_list = []
                                media_list = []
                                media_filepaths = []
                                source = ""
                                if 'title' in post.keys():
                                    new_post['full_text'] = f"Title:{post['title']} \n"
                                    if "via" in post['title']:
                                        source = f"{post['title'].split('via ')[-1]}"
                                if 'attachments' in post.keys():
                                    for attachment in post['attachments']:
                                        if 'data' in attachment.keys():
                                            for data in attachment['data']:
                                                if "text" in data.keys():
                                                    new_post['full_text'] = f"{new_post['full_text']}Summary: {data['text']} \n"
                                                if "external_context" in data.keys():
                                                    if "name" in data['external_context'].keys():
                                                        new_post['full_text'] = f"{new_post['full_text']}Summary: {data['external_context']['name']}"
                                                    if "url" in data['external_context'].keys():
                                                        new_post['full_text'] = f"{new_post['full_text']} ({data['external_context']['url']})"
                                                        url_list.append(data['external_context']['url'])
                                                if "media" in data.keys():
                                                    media_list.append(data['media'])
                                                    media_filepaths.append(data['media']['uri'])
                                if "data" in post.keys():
                                    for data in post['data']:
                                        if "post" in data.keys():
                                            new_post['full_text'] = f"{new_post['full_text']}Post:{data['post']} \n"
                                while new_post['full_text'].endswith( "\n"):
                                    new_post['full_text'] = new_post['full_text'][:-2]
                                #print(new_post['full_text'])
                                mentions = re.findall(r"@\w*", new_post['full_text'])
                                if len(mentions) > 0:
                                    for item in mentions:
                                        mentions.remove(item)
                                        item = item[1:]
                                        mentions.append(item)
                                hashtags = re.findall(f"#\w*", new_post['full_text'])
                                if len(hashtags) > 0:
                                    for item in hashtags:
                                        hashtags.remove(item)
                                        item = item[1:]
                                        hashtags.append(item)
                                new_post['truncated'] = False
                                new_post['display_text_range'] = [0, len(new_post['full_text'])]
                                #print(new_post['display_text_range'])
                                new_post['entities'] = {}
                                print(hashtags, mentions)
                                new_post['entities']['user_mentions'] = mentions
                                new_post['entities']['urls'] = url_list
                                new_post['entities']['symbols'] = []
                                new_post['entities']['media'] = []
                                if len(media_list) > 0:
                                    for item in media_list:
                                        new_dict = {}
                                        print(item['uri'])
                                        new_dict['expanded_url'] = item['uri']
                                        new_dict['indices'] = ["144", "167"]
                                        new_dict['url'] = item['uri']
                                        new_dict['media_url'] = item['uri']
                                        new_dict['id_str'] = str(item['creation_timestamp'])
                                        new_dict['id'] = str(item['creation_timestamp'])
                                        new_dict['media_url_https'] = item['uri']
                                        if "photo_metadata" in item['media_metadata'].keys():
                                            height = "320"
                                            width = "320"
                                            if "original_height" in item['media_metadata']['photo_metadata']['exif_data'][0].keys():
                                                height = item['media_metadata']['photo_metadata']['exif_data'][0]['original_height']
                                            if "original_width" in item['media_metadata']['photo_metadata']['exif_data'][0].keys():
                                                width = item['media_metadata']['photo_metadata']['exif_data'][0]['original_width']
                                            new_dict['sizes'] = {}
                                            new_dict['sizes']['small'] = {}
                                            new_dict['sizes']['small']['w'] = str(width)
                                            new_dict['sizes']['small']['h'] = str(height)
                                            new_dict['sizes']['small']['resize'] = "fit"
                                            new_dict['sizes']['large'] = new_dict['sizes']['small']
                                            new_dict['sizes']['thumb'] = {}
                                            new_dict['sizes']['thumb']['w'] = "150"
                                            new_dict['sizes']['thumb']['h'] = "150"
                                            new_dict['sizes']['thumb']['resize'] = "crop"
                                            new_dict['sizes']['medium'] = new_dict['sizes']['small']
                                            new_dict['type'] = "photo"
                                        new_dict['display_url'] = item['uri']
                                        new_post['entities']['media'].append(new_dict)
                                        new_dict = ""
                                    new_post['extended_entities'] = {}
                                    new_post['extended_entities']['media'] = new_post['entities']['media']
                                new_post['entities']['hashtags'] = hashtags
                                new_post['source'] = source
                                # hold a sec
                                new_post['in_reply_to_status_id'] = ""
                                new_post['in_reply_to_status_id_str'] = ""
                                new_post['in_reply_to_user_id'] = ""
                                new_post['in_reply_to_user_id_str'] = ""
                                new_post['user'] = user_data
                                new_post['geo'] = ""
                                new_post['coordinates'] = ""
                                new_post['place'] = ""
                                new_post['contributors'] = ""
                                new_post['is_quote_status'] = ""
                                new_post['retweet_count'] = 0
                                new_post['favorite_count'] = 0
                                new_post['favorited'] = False
                                new_post['retweeted'] = False
                                new_post['possibly_sensitive'] = False
                                new_post['lang'] = "en"
                                master_post_text = json.loads(json.dumps(post))
                                with open(master_post, "w") as output:
                                    json.dump(master_post_text, output)
                                output.close()
                                master_post2 = f"{master_post[:-3]}json"
                                os.rename(master_post, master_post2)
                                print(f"saved {master_post2}")
                                normalized_post_text = json.loads(json.dumps(new_post))
                                with open(normalized_post, "w") as output:
                                    json.dump(normalized_post_text, output)
                                output.close()
                                normalized_post2 = f"{normalized_post[:-3]}json"
                                os.rename(normalized_post, normalized_post2)
                                print(f"save {normalized_post2}")
                                if len(media_filepaths) > 0:
                                    for item in media_filepaths:
                                        item1 = f"{source_folder}/{item}"
                                        item_root = item.split("/")[-1]
                                        item2 = f"{file_path1}/preservation1/{item_root}"
                                        item3 = f"{file_path1}/presentation2/{item_root}"
                                        shutil.copy2(item1, item2)
                                        shutil.copystat(item1, item2)
                                        shutil.copy2(item1, item3)
                                        shutil.copystat(item1, item3)
                                if metadata_generator is True:
                                    metadata = Element('dcterms:dcterms',
                                                       {'xmlns': 'http://dublincore.org/documents/dcmi-terms/',
                                                        'xmlns:dcterms': 'http://dublincore.org/documents/dcmi-terms/',
                                                        'xsi:schemaLocation': 'http://dublincore.org/documents/dcmi-terms/ qualifiedDcSchema.xsd',
                                                        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                                                        'xmlns:tslac': 'https://www.tsl.texas.gov/'})
                                    title = SubElement(metadata, 'dcterms:title')
                                    title.text = f"{str(master_date[:10])}: {new_post['id_str']}"
                                    description = SubElement(metadata, 'dcterms:description.abstract')
                                    description.text = f"Post text: {new_post['full_text']}"
                                    if 'agency' in valuables:
                                        SubElement(metadata, 'dcterms:relation.isPartOf').text = f"{valuables['agency']} social media archive"
                                    if "preferredCitation" in valuables:
                                        SubElement(metadata, 'dcterms:identifier.bibliographicCitation').text = f"{title.text}, {new_post['user']['name']}, Facebook, {valuables['preferredCitation']}"
                                    SubElement(metadata, 'dcterms:type').text = "Text"
                                    creator = SubElement(metadata, 'dcterms:creator')
                                    creator.text = metadata_creator
                                    date_created = SubElement(metadata, 'dcterms:date.created')
                                    date_created.text = str(master_date[:10])
                                    SubElement(metadata, "dcterms:subject").text = "Social media"
                                    SubElement(metadata, "dcterms:subject").text = "Facebook"
                                    SubElement(metadata,  "tslac:note").text = "Facebook data normalized to Twitter data model for access/rending purposes. Post identifier generated based upon user identifier and timestamp of post. Original post json format available on request."
                                    SubElement(metadata, "tslac:socialmedia.platrform").text = "Facebook"
                                    SubElement(metadata, "tslac:socialmedia.username").text = new_post['user']['name']
                                    SubElement(metadata, "tslac:socialmedia.identifier").text = new_post['id_str']
                                    for item in hashtags:
                                        SubElement(metadata, "tslac:socialmedia.hashtag").text = item
                                    for item in mentions:
                                        SubElement(metadata, "tslac:socialmedia.mentions").text = item
                                    metadata_file = f"{master_post2}.metadata"
                                    writer = open(metadata_file, 'wt', encoding='utf-8')
                                    writer.write(prettify(metadata))
                                id_list2.append(post_id)
                with open(fb_log, "a") as w:
                    for item in id_list2:
                        w.write(f"{item}\n")
                w.close()
            window['-OUTPUT-'].update('\nstarting upload prep\n', append=True)
            window['-OUTPUT-'].update('resetting status bar\n', append=True)
            counter = 0
            total = len(upload_list)
            upload_list = list(upload_list)
            upload_list.sort()
            year_list = list(year_list)
            year_list.sort()
            for item in upload_list:
                for dirpath, dirnames, filenames in os.walk(item):
                    for filename in filenames:
                        filename1 = os.path.join(dirpath, filename)
                        filename2 = filename1.replace(target_folder, upload_folder)
                        create_directory(filename2)
                        shutil.copy2(filename1, filename2)
                        shutil.copystat(filename1, filename2)
                        window['-OUTPUT-'].update(f"{filename1} copied to upload folder\n", append=True)
            print("test works")
'''
        else:
            window['-STATUS-'].update("Need more data, fill in the proper elements\n", text_color="orchid1",
                                      font=("Calibri", "12", "bold"))
            # print("\need more data, fill in the proper elements")
    if event == "Close" or event == sg.WIN_CLOSED:
        break
window.close()
