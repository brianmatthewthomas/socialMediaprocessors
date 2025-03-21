# Documentation under construction
# Social Media Processors at TSLAC
This repository has paradigms specific to the Texas State Library and Archives Commission and this should be taken into account when considering usage. twitter_backlog_gui_tslac, twitter_backlog_gui_agencies, twitter_wall_tool, upload_backlog and twitter_backlog are all deprecated and superseded by twitter_backlog_gui_tslac_v2. These other scripts are left in historical reference but are not intended for current use.

**Note**: These tools require installation of python3.9 and all dependencies. If you receive an error message about needing to install a specific library, it probably isn't in your distribution by default.

**Another note**: While this was developed in a Linux environment it is intended for generating a Windows OS executable file. In Linux this was accomplished using `Wine`, which must be installed separately. If compiling natively in Windows OS It is possible the difference between the two factors can come into conflict, no tests have been run to rule this out. There may also be some difference in the underlying libraries, although this seems unlikely.

**Yet another note:** The graphical interface for this was written in pysimplegui using a prior iteration, which was free to use. If compiling this executable from scratch with the most modern version of the library there may be a licensing fee.

## Instructions for compiling the executable
1. Install all dependencies. These are PySimpleGUI, zipfile, os, datetime, json, hashlib, shutil, sys, requests, xml, errno, yt_dlp. Ensure you are installing yt_dlp and not yt_dl; yt_dl had a couple of issues that could not be resolved for the purpose of this project.
2. Ensure ffmpeg is installed on your computer and is on the system path. This is specifically for YouTube handling. If it isn't and you can't get it to work, then you should be able to run this tool so long as it is n the same folder as the ffmpeg executable that can be downloaded for command line use. To get ffmpeg as an executable goto `https://www.gyan.dev/ffmpeg/builds/` and download the latest full release. Unzip the folder and drop the twitter_backlog_gui executable into the `/bin` subfolder of ffmpeg.
3. Run pyinstaller (should have come bundled with PySimpleGUI but if it didn't go install it) using a command like `pyinstaller -wF [filepath to the backlog_gui script]`. It'll take a little bit of time to compile. If something goes wrong and you need to retry, make sure to delete the contents of the `/build` subfolder or else you'll just carry the problem to the next attempt.
4. Get the compiled executable from the `/dist` directory and drop it wherever.

### Alternative to running as an executable
This tool may work directly from the script. It will generate the executable window and from there operate as you otherwise would have. Note that an     executable method was targeted for speed compared to a GUI tool script in a Linux virtual machine, running as a script directly in Windows OS may or may not be slower.
## `twitter_backlog_gui_tslac_v2.py`
## Usage notes
### Usage for non-archives
Ignore and do not check the `Export Metadata?` checkbox

Get correspondence checkbox is for you to download correspondence type records. As this is how it is being considered, it is not processed into the same directory as posts. 
### Usage notes for archives that aren't TSLAC
You will need a good text editor to bulk update the exported metadata to whatever standard you choose to use. Metadata is exported using tslac-specific schema details and tslac-specific metadata. This is not configurable within the tool, you will have to modify the script to make changes to how that is done. Or identify what you do not care for and use the text editor to make batch changes.
### Normal usage notes (for everyone)
This tool works on the premise of downloading account data from a social media company and directly processing the zip file. It is highly dependent on tracking the structure of the platform-provided zip file so it is important.


# old documentation below, will be deleted shortly

## `twitter_backlog_gui_agencies.py`
A graphical interface tool intended for state agencies or other non-archive users. It is standalone with a graphical interface. There is no command-line or graphical interface.
### Usage
This is intended for use and re-use. When you download a twitter archive it will break open the archive file into a directory you choose and then start processing the Tweets (tweets only at this time) contents into one folder per tweet with any associated media you wish. There is an option to also generate metadata files based on the data in the tweets into the metadata structure used by TSLAC. Content is structured in the JSON format you would get if you harvested it from the twitter backend.

**Note**: If you use this tool over a period of time it is set to only process tweets not previously processed. To reprocess the entire archive you should delete the `log_tweetIDs.txt` file.

**Note**: The icon was sourced from wikicommons under an open usage license given its shape is general

**Note**: If you start the tool and need to stop it for some reason you will need to press ctrl+c in the background terminal window. Pressing the close button won't do anything during execution.
### Why not use the API or harvest the webpage???
Good question. The API as of 2022 only allows harvesting of the most recent 3600 or so tweets, if that (the number seems to vary a bit). If you try to harvest the webpage for the look and feel you will get no more, and most likely a lesser number of tweets; plus, if you get adds in the feed or user comments there are potential concerns about copyright and privacy. Most of us haven't been thinking about tackling this problem until long after we have posted more than that number of tweets. When you download your twitter archive it includes data for all of your posts, not just the most recent ones.
### First steps
Before invoking this tool you need to download your twitter account data. You need to log in **directly on twitter**, not through a social media manager program. It will usually take several days to obtain this data. Download as a ZIP. Your can rename the ZIP file but don't extract it.
### Notes on metadata
If you choose to extract metadata, you will be presented with the option to writer in your agencies name/abbreviation as well as a collection name. This is part of TSLAC's processes but is available here since it may be useful, especially if used by multiple departments.
### Last steps
The tool is not set to delete the files extract from the twitter ZIP archive. It isn't necessary to keep it. If you intend to re-use the tool later you will either need to delete the extracted files (not the processed ones) or on next extraction target a different directory. If the tool senses an already extracted twitter archive it will skip the extraction step and move directly to processing.
### How it works
`log_tweetIDs.txt`: a log file generated after the archive is processed that includes an itemized list of tweet IDs. This log is re-used in later extractions to prevent the re-processing of tweets already in existence. The version of this tool meant for the Archives also uses this dedupe functionality to only upload new tweets to the preservation/access system.

`profile_banner/`: The banner in place at the time of the processing. Interesting if you want to keep a running example of banner changes over time.

`profile_image/`: The profile image at the time of the processing. Interesting if you want to keep a running example of profile image changes over time.

`backlog/`: The processed tweets subfoldered by year, then by tweet. Naming convention for the tweets and their folders is YYYY-MM-DD_tweet_id.

`*.json`: The javascript object notation formatted version of the tweet data. This is compliant with the formatting for TSLAC's preservation system.

`*.json.metadata`: If metadata creation is selected, this the metadata file generated. Agencies are not required to generate metadata but still may find it useful. It is an XML format.

`*[image of video format] extention`: The media associated with a specific tweet based on what was added to twitter at the time of upload. Media file is named based on the twitter ID for the file, which is how they store the files, rather than the original file name.
## twitter_wall_tool.py
This script is meant to be run on the command line and will output a twitter wall feed using the data extracted from the twitter archive. It works by crawling the data extracted so if something is missing from this wall that means it is missing from the data extraction process. Note that some older images are no longer available on the twitter website for unknown reasons.

## `twitter_backlog.py`
The original twitter backlog processor and uploader tool developed for TSLAC use. Depends upon some credentials files for twitter's API as well as for logging into TSLAC's preservation system for uploading tweets. Agencies do not use. 
## `upload_backlog.py`
Used for uploading backlog social media under the auspices of the twitter_backlog.py tool. This is a workhorse customized to TSLAC.  It does not contain anything restricted but should not be used outside of TSLAC without adaptation. Presumes Preservica as the preservation system.

## `twitter_backlog_gui_tslac.py`
The more complicated tool used by TSLAC for both processing a twitter download file and uploading it to the Texas Digital Archive. Set up based on the assumption of using the Preservica digital preservation system. Improves upload the `twitter_backlog` and `upload_backlog` processes.