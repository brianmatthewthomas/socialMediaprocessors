import PySimpleGUI as sg
import zipfile
import requests
import os
import time
from os import listdir
from os.path import isfile, join
import datetime
import json
import hashlib
import shutil
import sys
import threading
import uuid
import boto3
from boto3.s3.transfer import TransferConfig
from botocore.config import Config
import lxml.etree as ET
# for creating the metadata file
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from collections import OrderedDict
import errno
import twitter_wall_tool
GB = 1024 ** 3
transfer_config = TransferConfig(multipart_threshold=1 * GB)


class ProgressPercentage(object):

    def __init__(self, filename):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write("\r%s %s / %s (%.2f%%)" % (self._filename, self._seen_so_far, self._size, percentage))
            sys.stdout.flush()

def prettify(elem):
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparse = minidom.parseString(rough_string)
    return reparse.toprettyxml(indent="    ")

def new_token(username, password, tenent, prefix):
    switch = 0
    while switch != 3:
        paydirt = {'username': username, 'password': password, 'tenant': tenent}
        resp = requests.post(f'https://{prefix}.preservica.com/api/accesstoken/login', data=paydirt).json()
        print(resp)
        if resp['success'] == True:
            return resp['token']
            switch = 3
            success = True
        else:
            print(f"new_token failed with error code: {resp['status']}")
            print("retrying...")
            success = False
            switch += 1
    if success is False:
        print("max retries reached, stopping program. Wait a bit and try again")
        print(resp.request.url)
        print(resp)
        raise SystemExit

def create_structure(structure_dict):
    headers = login(structure_dict['url'],structure_dict['payload'])
    version = structure_dict['version']
    dirTitle = structure_dict['dirTitle']
    standardDir = structure_dict['standardDir']
    base_url = f"https://{structure_dict['prefix']}.preservica.com/api/entity/structural-objects/"
    namespaces = {'xip': f'http://preservica.com/XIP/v{version}',
                  'EntityResponse': f'http://preservica.com/EntityAPI/v{version}',
                  'ChildrenResponse': f'http://preservica.com/EntityAPI/v{version}',
                  'MetadataResponse': f'http://preservica.com/EntityAPI/v{version}',
                  'dcterms': 'http://dublincore.org/documents/dcmi-terms',
                  'tslac': 'https://www.tsl.texas.gov/'}
    data = f'<StructuralObject xmlns="http://preservica.com/XIP/v{version}"><Title>' + dirTitle + '</Title><Description>' + dirTitle + '</Description><SecurityTag>open</SecurityTag><Parent>' + standardDir + '</Parent></StructuralObject>'
    response = requests.post(base_url, headers=headers, data=data)
    status = response.status_code
    print(response)
    tempfile = structure_dict['tempDir'] + "/temp.xml"
    with open(tempfile, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=128):
            fd.write(chunk)
    fd.close()
    dom = ET.parse(tempfile)
    purl = dom.find(".//xip:Ref", namespaces=namespaces).text
    os.remove(tempfile)
    return purl


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
    uploader(valuables)

def uploader(valuables):
    token = new_token(valuables['username'], valuables['password'], valuables['tenant'], valuables['prefix'])
    print(token)
    user_tenant = valuables['tenant']
    user_domain = valuables['prefix']
    bucket = f'{user_tenant.lower()}.package.upload'
    endpoint = f'https://{user_domain}.preservica.com/api/s3/buckets'
    print(endpoint)
    print(f'Uploading to Preservica: using s3 bucket {bucket}')
    client = boto3.client('s3', endpoint_url=endpoint, aws_access_key_id=token, aws_secret_access_key="NOT USED",
                          config=Config(s3={'addressing_style': 'path'}))
    sip_name = valuables['compiled_opex']
    print(valuables['parent_uuid'])
    print(sip_name)
    print(valuables['asset_id'])
    technical = input("press enter to continue")
    metadata = {'Metadata': {'structuralObjectreference': valuables['parent_uuid']}}
    switch = 0
    while switch != 3:
        try:
            response = client.upload_file(sip_name, bucket, valuables['asset_id'] + ".zip", ExtraArgs=metadata,
                                          Callback=ProgressPercentage(sip_name), Config=transfer_config)
            switch = 3
            print("\n", "upload successful")
        except:
            print("\nupload failure, trying again")
            switch += 1

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
            if exc.errno != errno.EExist:
                raise

def login(url, payload):
    auth = requests.post(url, data=payload).json()
    sessionToken = auth['token']
    headers = {'Preservica-Access-Token': sessionToken}
    headers['Content-Type'] = 'application/xml'
    headers['Accept-Charset'] = 'UTF-8'
    return headers

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

layout = [
    # [sg.Push(),sg.Titlebar("My Twitter Breaker tool"),sg.Push()],
    [
        sg.Push(),
        sg.Text("twitter zip file"),
        sg.In("", key="-File-"), #sg.In(size=(50, 1), enable_events=True, key="-File-"),
        sg.FileBrowse(file_types=(("zip files only", "*.zip"),))
    ],
    [
        sg.Push(),
        sg.Text("temporary staging location for unprocessed twitter archive"),
        sg.In("", key="-SourceFolder-"), #sg.In(size=(50, 1), enable_events=True, key="-SourceFolder-"),
        sg.FolderBrowse()
    ],
    [
        sg.Push(),
        sg.Text("target location for processed twitter archive"),
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
      sg.Text("Upload variables",text_color="orchid1",font=("Calibri", "12", "underline"))
    ],
    [
        sg.Push(),
        sg.Text("Preservica Version:", key="-PreservicaVersion_TEXT-"),
        sg.Input("", size=(50, 1), key="-PreservicaVersion-")
    ],
    [
        sg.Push(),
        sg.Text("Username:", key="-USERNAME_TEXT-"),
        sg.Input("", size=(50, 1), key="-USERNAME-")
    ],
    [
        sg.Push(),
        sg.Text("Password:", key="-PASSWORD_TEXT-"),
        sg.Input("", size=(50, 1), password_char="#", key="-PASSWORD-")
    ],
    [
        sg.Push(),
        sg.Text("Domain Prefix:", key="-PREFIX_TEXT-"),
        sg.Input("", size=(50, 1), key="-PREFIX-")
    ],
    [
        sg.Push(),
        sg.Text("Tenancy abbreviation:", key="-TENANCY_TEXT-"),
        sg.Input("", size=(50, 1), key="-TENANCY-")
    ],
    [
        sg.Push(),
        sg.Text("Parent folder UUID", key="-PARENT_TEXT-"),
        sg.Input("", size=(50,0), key="-PARENT-")
    ],
    [
        sg.Checkbox("Export Metadata?", checkbox_color="dark green",
                    tooltip="Checking this box will create sidecar metadata for each tweet compatible with TSLAC standards",
                    key='-METADATA-', enable_events=True)
    ],
    [
        sg.Text("Fill in additional metadata elements if you wish:", key='-MOREMETADATA-')
    ],
    [
        sg.Push(),
        sg.Text("Agency Name/Abbreviation:", key="-CREATOR_TEXT-"),
        sg.Input("", size=(50, 1), key="-CREATOR-")
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
    target_file = values['-File-']
    source_folder = values['-SourceFolder-']
    target_folder = values['-TargetFolder-']
    metadata_generator = values['-METADATA-']
    metadata_creator = values['-CREATOR-']
    metadata_citation = values['-CITATION-']
    parentFolder = values['-PARENT-']
    collectionName = values['-CITATION-']
    version = values['-PreservicaVersion-']
    wall = values['-WALL-']
    if event == "Execute":
        upload_list = set()
        year_list = set()
        window['-OUTPUT-'].update(f"testing login\n", append=True)
        payload = {'username': values['-USERNAME-'],
                   'password': values['-PASSWORD-'],
                   'tenant': values['-TENANCY-']}
        url = f"https://{values['-PREFIX-']}.preservica.com/api/accesstoken/login"
        headers = login(url, payload)
        window['-OUTPUT-'].update(headers, append=True)
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
            create_structure_template = {'version': version,
                                'dirTitle':'',
                                'standardDir':parentFolder,
                                'url':url,
                                'payload':payload,
                                'prefix':values['-PREFIX-'],
                                'tempDir':target_folder}
            year_dict = {}
            for item in year_list:
                structure_dict = create_structure_template
                structure_dict['dirTitle'] = item
                year_dict[item] = create_structure(structure_dict)
            print(year_dict)
            valuables = ""
            valuables = {'agency':values['-CREATOR-'],
                         'harvestType': 'twitter',
                         'harvest_type': 'timeline',
                         'collectionName': collectionName,
                         'preferredCitation': metadata_citation + ". Archives and Information Services Division, Texas State Library and Archives Commission.",
                         'parentFolder': parentFolder,
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
                                    'version':version,
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
                upload_dict = upload_dict_template
                upload_dict['parent_uuid'] = year_dict[year]
                upload_dict['compiled_opex'] = zippy_name + ".zip"
                upload_dict['asset_id'] = zippy
                uploader(upload_dict)
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
        else:
            window['-STATUS-'].update("Need more data, fill in the proper elements\n", text_color="orchid1",
                                      font=("Calibri", "12", "bold"))
            # print("\need more data, fill in the proper elements")
    if event == "Close" or event == sg.WIN_CLOSED:
        break
window.close()
