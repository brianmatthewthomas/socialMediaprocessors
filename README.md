# Social Media Processors at TSLAC
This repository is specific to the Texas State Library and Archives Commission and includes the processors intended to use in order to harvest/process social media files. Some of these tools may be re-usable by state agencies in which case they will be marked with a suffix `_agencies`

**Note**: These tools require installation of python3.9 and all dependencies. If you receive an error message about needing to install a specific library, it probably isn't in your distribution by default.

**Another note**: This was developed using Anaconda on a Linux operating system. It should work in a Windows environment without Anaconda so long as all the requirements are installed but we cannot guarantee that.

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