# a simplified version of the opexCompiler to facilitate uploading social media without having to
# reference external packages
import datetime
import hashlib
import os
import shutil
import sys
import threading
import uuid
from os import listdir
from os.path import isfile, join
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

import boto3
import requests
from boto3.s3.transfer import TransferConfig
from botocore.config import Config
import configparser
'''
configuration = configparser.ConfigParser()
# update this to the filepath for your passwords file
configuration.read("/media/sf_G_DRIVE/working_electronicRecords/research_3a.001b/socialMedia/social_monster/credentials/secrets.txt")
passcodes = {'tenancy': configuration.get("preservica_tenancy"),
             'domain': configuration.get("preservica_domain_prefix"),
             'username': configuration.get("preserca_username"),
             'password': configuration.get("preservica_password")}
'''
#basic definitions for upload
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

def pax_prep_withXIP(valuables):
    #a simpler version of the multi-upload to handle cases where a pax is simply preservation files
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
    xip.set('xmlns', 'http://preservica.com/XIP/v6.3')
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
                if filename.split(".")[-1] == "srt":
                    filename2 = os.path.join(preservation_representation, "English", filename)
                elif filename.endswith(tuple(["mp4", "m4v", "mov"])):
                    filename2 = os.path.join(preservation_representation, "Movie", filename)
                else:
                    filename2 = os.path.join(preservation_representation, filename.split(".")[0], filename)
                if not os.path.exists(os.path.dirname(filename2)):
                    os.makedirs(os.path.dirname(filename2), exist_ok=True)
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
    export_file = valuables['export_directory'] + "/" + valuables['timeframe'] + "/" + valuables['asset_title'] + ".pax.zip.opex"
    opex_output = open(export_file, "w", encoding='utf-8')
    opex_output.write(prettify(opex))
    opex_output.close()
    if 'metadata_file' in valuables.keys():
        with open(valuables['metadata_file'], 'r') as f:
            filedata = f.read()
            filedata = filedata.replace('<?xml version="1.0" encoding="UTF-8"?>', "")
            filedata = filedata.replace('<?xml version="1.0" ?>','')
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
    compiled_opex = valuables['export_directory']+ "/" + valuables['timeframe']
    shutil.make_archive(compiled_opex, "zip", compiled_opex)
    compiled_opex = compiled_opex + ".zip"
    valuables['compiled_opex'] = compiled_opex
    print("uploading", valuables['timeframe'])
    valuables['asset_id'] = valuables['timeframe']
    uploader(valuables)


def uploader(valuables):
    token = new_token(valuables['username'], valuables['password'], valuables['tenent'], valuables['prefix'])
    print(token)
    user_tenant = valuables['tenent']
    user_domain = valuables['prefix']
    bucket = f'{user_tenant.lower()}.package.upload'
    endpoint = f'https://{user_domain}.preservica.com/api/s3/buckets'
    print(f'Uploading to Preservica: using s3 bucket {bucket}')
    client = boto3.client('s3', endpoint_url=endpoint, aws_access_key_id=token, aws_secret_access_key="NOT USED",
                          config=Config(s3={'addressing_style': 'path'}))
    sip_name = valuables['compiled_opex']
    metadata = {'Metadata': {'structuralObjectreference': valuables['parent_uuid']}}
    switch = 0
    while switch != 3:
        try:
            response = client.upload_file(sip_name, bucket, valuables['asset_id'] + ".zip", ExtraArgs=metadata,
                                          Callback=ProgressPercentage(sip_name), Config=transfer_config)
            switch = 3
            print("\n", "upload successful")
        except:
            print("upload failure, trying again")
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
                    filename = filename.replace(item,"{" + item + "}")
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
        if filename.split(".")[-1] == "srt":
            bitstream.text = "Representation_" + generation_label[:-1] + "/English/" + filename
        elif filename.endswith(tuple(["mp4", "m4v", "mov"])):
            bitstream.text = "Representation_" + generation_label[:-1] + "/Movie/" + filename
        else:
            bitstream.text = "Representation_" + generation_label[:-1] + "/" + filename.split(".")[
                0] + "/" + filename
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
        if filename.split(".")[-1] == "srt":
            physloc.text = "Representation_" + generation_label[:-1] + "/English"
        elif filename.endswith(tuple(["mp4", "m4v", "mov"])):
            physloc.text = "Representation_" + generation_label[:-1] + "/Movie"
        else:
            physloc.text = "Representation_" + generation_label[:-1] + "/" + filename.split(".")[0]
        if content_type == "Tweet":
            placeholder = filename.split("_")
            for item in placeholder:
                if len(item) > 11:
                    item = item.split(".")[0]
                    turtle = filename.replace(item,"{" + item + "}[tslac]")
            SubElement(bitstream, 'OriginalFilename').text = turtle
        fixities = SubElement(bitstream, "Fixities")
        fixity = SubElement(fixities, "Fixity")
        fixityAlgorithmRef = SubElement(fixity, "FixityAlgorithmRef")
        fixityAlgorithmRef.text = "SHA256"
        fixityValue = SubElement(fixity, "FixityValue")
        fixityValue.text = create_sha256(fullPath)

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