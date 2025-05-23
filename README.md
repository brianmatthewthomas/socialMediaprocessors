# Documentation under construction
# Social Media Processing at TSLAC
This repository has paradigms specific to the Texas State Library and Archives Commission and this should be taken into account when considering usage. twitter_backlog_gui_tslac, twitter_backlog_gui_agencies, twitter_wall_tool, upload_backlog and twitter_backlog are all deprecated and superseded by `social_media_processor`. These other scripts are left in for historical reference but are not intended for current use.

**Note**: These tools require installation of python3.9 and all dependencies. If you receive an error message about needing to install a specific library, it probably isn't in your distribution by default.

**Another note**: While this was developed in a Linux environment it is intended for generating a Windows OS executable file. In Linux this was accomplished using `Wine`, which must be installed separately. If compiling natively in Windows OS It is possible the difference between the two factors can come into conflict, no tests have been run to rule this out. There may also be some difference in the underlying libraries, although this seems unlikely.

**Yet another note:** The graphical interface for this was written in pysimplegui using a prior iteration, which was free to use. If compiling this executable from scratch with the most modern version of the library there may be a licensing fee.

## Instructions for compiling the executable
1.	Install all dependencies. These are PySimpleGUI, zipfile, os, datetime, json, hashlib, shutil, sys, requests, xml, errno, yt_dlp. Ensure you are installing yt_dlp and not yt_dl; yt_dl had a couple of issues that could not be resolved for the purpose of this project.
2.	Ensure ffmpeg is installed on your computer and is on the system path. This is specifically for YouTube handling. If it isn't and you can't get it installed or get it installed but can't get it to work with this tool, then you should be able to run this tool using the following method: Get FFmpeg as an executable for command-line use by going to `https://www.gyan.dev/ffmpeg/builds/` and downloading the latest full release. Unzip the folder and drop the twitter_backlog_gui executable into the `/bin` subfolder of ffmpeg. Navigate to that `/bin` folder and double-click on the social media processor to get it running.

   * **Note:** FFmpeg is used by yt_dlp to merge an audio-only file and a video-only file from YouTube and merge them. The two files are deleted after the merger takes place. If you do not run this executable with FFmpeg the step will not complete and you will be left with the audio-only and the video-only files.

3.	Run pyinstaller (should have come bundled with PySimpleGUI but if it didn't go install it) using a command like `pyinstaller -wF [filepath to the backlog_gui script]`. It'll take a little bit of time to compile. If something goes wrong and you need to retry, make sure to delete the contents of the `/build` subfolder or else you'll just carry the problem to the next attempt.
4.	Get the compiled executable from the `/dist` directory and drop it wherever. Remember the question of FFmpeg in step 2.

### Alternative to running as an executable
This tool may work directly from the script. It will generate the executable window and from there operate as you otherwise would have. Note that an     executable method was targeted for speed compared to a GUI tool script in a Linux virtual machine, running as a script directly in Windows OS may or may not be slower.
# Archival/Records Management theory behind this tool
This tool is based on basic archival/records management practice and should be understood in that context as it explains why it does what it does in the way it does. Specifically, the principle of "a record is a records regardless of format" and record types.

Records can be divided into several types, but here are attributed to two categories: (1) Posts/Public Engagement and (2) Correspondence.

The primary purpose of this tool is to preserve and manage the record of how the account-holder (agency) engaged with the public using common social media platforms. This engagement is through posts (events, albums, and videos are a type of post), which is often classified as a form of outreach for records management/archival purposes. Although comments on posts brings much of the "social" part of social media, the question of whether an individual commenter intended their comment to be preserved in-perpetuity even though it is in a public space is fraught and getting permissions from every commenter for preservation of their comments is not scalable and so will not be extracted for preservation. 

'Correspondence' means an interaction from the public which the account-holder then engages with. This is post comments with account-holder replies and direct messages with replies. The retention period for correspondence for most agencies will be very different from that of their posts, as is the long-term value as evidence of the public engagement of the agency. Thus, while it may be possible to process correspondence with this tool (most platforms but not all are guaranteed), it is not processed by default and if processed it is processed into a separate folder from the posts.

While a social media wall will show posts as a seamless listing, each post is its own distinct record. A complete preservation copy of a given post will include both the text and any media that accompanies it. Thus, a processed social media account will have each post in its own folder with accompanying media. Posts are foldered using the date (YYYY-MM-DD or YYYYMMDD format) and a post identifier (name of video for YouTube). A major organization unit is applied on top of that to reflect associations. For most platforms this will be the year of the post, bot for others this may be 'Albums', 'Events', or a playlist name. For ease of post-processing review, if you check the box, the tool will generate a genericized wall to view the output in one place.

Social media records are inherently electronic records and long-term preservation of electronic records involves format normalization. Normalization, in short, is the converting one set of formats into a standardized version of the same format or an independent format with the aim of long-term sustainability. The standard format for a post is json, but each platform uses its own data standard for its json output. Further, some will include account-holder data while others will not. Long-term this variability will become problematic as platforms themselves may change how it structures the data. While still close in time to the standard for each platform, normalization to common 3rd standard within the json file format is important so that social media can be managed and viewed in its entirety rather than trying to make bespoke renderers and documentation for each version of each platform's json output. Current supported platforms are listed below.
## Why not use a harvester tool or api method?
There are a few reasons to opt for this method over other methods.
1.	Completeness: API harvesting is typically point-forward. For those that are not point-forward, historic data that can be harvested via API is most often limited to a certain timeframe or number of historic posts (most recent 1500, for example). Thus, what is received if you have long-standing accounts or an active social media presence if unlikely to be the whole of the account data.
2.	Ownership: Harvest using a web-crawler will gather the look and feel of te social media site. This can include advertising or custom loon-and-feel of a platform. The rights to preserve either of these factors isn’t guaranteed. The accountholder has the rights to their data hosted by the social media platform (usually), but not the platform itself. This method of preserving the posts avoids this potential problem
3.	Records management domain. This tool is predicated on records management principles, one of which is that records creators have a responsibility (usually under law) to transfer archival records to the archive at a certain point. Rather than assuming the responsibility of the agency records management staff and trying to do that across the breadth of the domain (entire state government, for example), this tool replies upon the records manager to fulfill one of their essential duties.
4.	Scalability. Certain harvester services/platforms require ongoing permissions to harvest be granted by the accounts being harvested. At large scale, keeping contact with each entity (agency) one might want to harvest posts from is not feasible. Assuming this isn’t an issue, managing potentially hundreds of API harvest threads is not feasible for an archive with limited staff time, and services that do this on behalf of an archive can be costly.
5.	Ease of process. Once a social media transfer is completed by an agency, it is a matter of running the tool and perhaps some minor post-processing
# `social_media_processor.py`
## Usage notes

### Usage for non-archives
Ignore and do not check the `Export Metadata?` checkbox. This is for archives to extract metadata from the normalized social media file to enhance access.

Get correspondence checkbox is for you to download correspondence type records. As this is how it is being considered, it is not processed into the same directory as posts. 
### Usage notes for archives that aren't TSLAC
You will need a good text editor to bulk update the exported metadata to whatever standard you choose to use. Metadata is exported using tslac-specific schema details and tslac-specific metadata. This is not configurable within the tool, you will have to modify the script to make changes to how that is done. Or identify what you do not care for and use the text editor to make batch changes.
### Normal usage notes (for everyone)
This tool works on the premise of downloading account data from a social media company and directly processing the zip file. It is highly dependent on tracking the structure of the platform-provided zip file. As folder structures evolve over time as well as output data structures, we will endeavor to update the tool to be able to process using those changes. This adaptation is based on TSLAC’s specific exposure to changes so if a change occurs but there is a significant time-period lapse before an agency transfers social media with this change, no update will have happened in between unless notified by the community.
## Usage
### Top row
Select the social media type to be processed. The tool will load options based upon your selection but the tool used to compile the executable can require a couple of ‘clicks’ to register a change. The load options button prompts the program to make the update. Click on it.
### Middle section
Social media zip file: This is the full filepath to the zip file. YouTube uses a director harvest method so it won’t show up here. This is a text box technically, but you can use the Browse button to navigate to the correct file. Note that the file but be the original download, curated downloaded zip files cannot be processed as the structure will change.

Temporary staging location: This is a full folder path. Use the Browse button or manually enter the path into the text box beside it. If you want to create a new folder navigate to the closest parent folder and in the text box append `/folder_name_of_your_choice` and it will be generated during processing.

Note: Unzipping into the temporary staging folder can take a long time so the system will assume that if there is content in that folder the step has already completed and proceed to the next step. This helps with troubleshooting problems. Don’t use old data.

Target location: This is the folder of the processed social media. If this is a new set, create a new folder. If this is a accretion to an existing social media archive, target the existing folder. It is will only process in the new content

Upload staging: This is the folder where the new posts will be staged for upload. For new social archives it’ll incidentally be everything. For existing archives it should only be the previously unprocessed material. For playlists and albums where there may be accretions to an existing thing that may require some wrangling. It is okay to delete the staging folder only integration into your archive is completed.

TDA upload checkbox: TDA is an acronym for Texas Digital Archive, the digital repository this tool was developed for. Clicking this will trigger json normalization in-situ, exporting metadata for processed posts, and pushing previously unprocessed posts to the target upload folder. If you don’t check this box, the new posts won’t go into upload staging.

Get correspondence: This checkbox will process direct messages and put them into its own folder structure. Correspondence will not be normalized as it is unlikely to be an archival record.
### Middle section for YouTube
The YouTube parameters are a bit different as YouTube is directly harvested. Target location and upload staging will still exist, but the remainder will be different.

Channel url: input the YouTube url for the channel you are going to harvest from, even if not doing a full channel harvest. It can either end with the channel UUID or @channelName

Choose types: All videos will get everything, and will take a while. Generally an entire channel won’t be archival so archives are more likely to choose selected videos

Type checkboxes:
* Shorts: YouTube short. All of them. Will be processed into a “Shorts” subfolder
* Lives: YouTube livestreams. Will be processed into its own subfolder but should be a flat folder structure below that
* Podcasts: YouTube podcasts, all of them. Will be pushed into a podcasts subfolder
* Playlists: YouTube playlist, will be processed into a subfolder for playlists in general and then for the specific playlist. A playlist post file will be part of the download. Accretions to a playlist will still get new videos but may not necessarily update the playlist post data file Playlist test box: copy the URL for the playlist exactly. Only one playlist can be processed at a time
* Begin date/End date: YouTube permits date range harvests. Use this to limit results if needed.
* Get comments: Will harvest down YouTube video comments, if any, directly into the post data file. Note that this data is not normalized.
### Lower section
Normalize JSON: Check to normalize the social media json file into a standardized format. This is current based upon the standard activity stream. Documentation of that standard can be found here: `https://www.w3.org/TR/activitystreams-vocabulary/`
1. Normalize json will move the original processed post into a subfolder called `preservation1`. A duplicate is placed in a subfolder called `preservation2`
2. When subfoldering is completed, the tool will then crawl through the new post folders, load the json data, and crosswalk it as much as feasible into the Activity Streams data standard. Not all data crosswalks and some data is superfluous to the content of the post. For non-superfluous data that does not crosswalk, a special data field with either the `dcterms` prefix or `platform_name` prefix will be used.

3. Export metadata: If checked, after file normalization, the tool will recrawl the new posts, but this time on the normalized file and extract key data data elements into a variation of Qualified Dublin Core and TSLAC-specific metadata as XML, to be used in TSLAC’s preservation/access system to facilitation discovery/access/management.

4. Generate Wall too?: Checking this will make the tool recrawl the normalized file set, in its entirety including older processed posts, and rework it into a standards html page. This is meant to help a processor review the output and determine if something went wrong. Post text is directly saved into the html file, but pulling up media is highly dependent on keeping the post structure intact. Removing a post folder will media will result in a section of html that will have text but no picture/video/etc.
5. Generate access warc?: Checking this will tap into a tool called warcit to create a **W**eb**ARC**hive file that includes all of the normalized file contents and a constructed html version of the post to emulate a genericized version of how a post is rendered. Specialized tools can then read the WARC file in a web browser as if it were a live website. Each post gets its own warc file to maintain its status as a unit. The WARC will also include the json file and metadata file. WARC files get pushed to a special folder with the upload staging location folder name + _access. If metadata files were generated, access file metadata will include notes about WARCs and the url to input into the reader for rendering. **Note** that warc generation uses an external tool that is called from the command line automatically for each post and close when the process is done for that post, you will see a lot of screens pop up briefly. This is ***normal***, but it will cause the computer to become functionally impossible to use for other tasks until the process completes as the pop-up takes primacy over any task you were doing beforehand.
### Lowest section
Execute: Will start the processing. Once started you cannot stop it with the close button. The X on the upper right-hand will crash the processing as will right-clicking the icon in the tray and selecting close window or using task manager.

Status bar: This is the progress of the current step. For YouTube, the tool being used, youtube_dlp does in-fact have its own progress tracker but in order to utilitze that, it would require many other things to be rendered that were unnecessary. So for YouTube, the status bar will not update until harvesting is completed. The status bar is meant for users to get a quick ideo of how far along the current process it.

Dialog box: Certain steps are useful for monitoring the progress of the overall process, such as what post is being processed. If it crashes, this will be helpful as you can then go to that post to see why it crashed to troubleshoot.
## Processor notes
The output of this tool requires a very standardized structure in the same manner as the input social media platform files. A couple of notes about that:
1. `log_[platformName]IDs.txt` or `youtube.txt`: contained a full list of the post IDs for the posts already processed. This is populated towards the end of the processing. DO NOT DELETE IT UNLESS YOU WANT EVERYTHING REPROCESSED!
2. `backlog` parent folder: The original iteration of this tool treated the processed posts as “backlog” data for archival processing to differentiate from newer data should we ever decide to use a harvester tool instead. This was retained rather than trying to update the associated interwoven processes affected by it
3. Facebook substructures: Facebook is very complicated and the structure of the processed output reflects that.
4. Facebook post identifiers: Facebook doesn’t use post identifiers like other platforms, although it still managed to differentiate the posts. In lieu of a system-generated identifier we use the YYYY-MM-DD for when the post was created then the exact timestamp like so: `YYYY-MM-DD_[timestamp]`. The probability that tw posts were created by the same account at the same millisecond is minimal, but in cases where it does happen (by a scheduling tool most likely) a -# is appended so post don’t get overwritten.
5. Actor 1: The post content has to be self-encapsulated as much as possible. Originally modeled after twitter’s method of doing so with their API, this concept is very important as a social media archive expands to multiple entities. Thus, while processing a zip file, user data is also processed and inserted into every output json file as an “Actor”. This is always the first actor to be added so it will always show up first.
6. Lost files: The creator of this tool has already noticed that some of the media files involved with posts have been lost. If a file cannot be found in a download the tool will try to get the media directly from the social media platform. If still not available it will move on. If generating a wall, this will show up as a broken reference
7. Wall is not authoritative: The wall works off of normalized data so is drawing on shared elements and is meant for reference/quality control purposes only. It is not intended to be crawled to generate a wacz file to then be browsable in a web archive player. The underlying data is very likely going to massive as it will try to grab every single piece of media attached to the file.
## External tools
The warc generator for access copies of the social media posts/content runs using a tool called warcit. To utilize this functional you *must* have warcit installed on your computer. The program is written to test for warcit and move-on if not present, but do not push it.

You can install python on your computer by first installing a local version of python from https://www.python.org/downloads/. A pre-3.10 version is needed as 3.10 forward requires a labor-intensive workaround to install warcit outside of a virtual environment. Post-installation, reboot your computer to ensure installation takes full effect. After that run:

`python -m pip install warcit` or some variant of that command. Go to https://github.com/webrecorder/warcit/tree/master if you have trouble.
## Crashed processes
This tool was created by a single person (Brian Thomas) using available knowledge and resources. As such, not all eventualities have been accounted for, only those that they were exposed to and could resolve. Crashes seem to be isolated to oddball characters or non-latin character. If the processor crashes it is highly likely an error pop-up box will be generated that shows a section of code for the error. Also, the print-out in the dialog box should say more information about what was happening at the time of the crash. Please document both (the code message in its entirety including formatting of the message) as send it to the author for review. They may ask for additional information such as a copy of the post file for troubleshooting. No guarantees of a fix, but we’ll try.
# Requesting additional platforms support
If there is a platform not currently supported you think would be useful please let us know. This will be based on business needs so if it isn’t something used by state agencies it may be added but not necessarily on a quick turnaround. Also, the ability to add a platform is based on the data available to the author so it may ne necessary to send a copy of a platform data export, otherwise they will have to create their own account and populate it. The latter is a less organic in terms of actual usage of a platform approach.
# Getting your data
Specific instructions by platform on how to export your data. These are good as of the last attempt by the project creator. If the process changes let the author know.
## Twitter/X
As of the time of this writing, a user can only export from X.com as twitter.com no longer exists. TSLAC is happy to accept existing twitter account downloads. So...in X
1. Login
2. Go to the bottom  left-hand corner under the more button

![](./directions_media/twitter_start.jpg)

3. Click on it, then click on "Settings and privacy"

![](./directions_media/twitter_settings.jpg)

4. A new page will show up. Under "Your account" click on "Download an archive of your data"

![](./directions_media/twitter_settings_download.jpg)

5. You will be prompted to re-enter the account password, enter that. You will also be prompted to do two-factor authentication through email of text message. Choose the best option for your needs.
6. From here, click on the "Request archive" button

![](./directions_media/twitter_request_download.jpg)

7. You will receive an email notice when the account download becomes available. Follow the directions to do that.
## Facebook/Threads
To export Facebook content you will need login access to the account. The following directions are based upon an individual account, the method for a institutional page are likely to be the same or similar
1. Login
2. Go to the upper right-hand corner and click on the user profile picture

![](./directions_media/facebook_userSettings.jpg)

3. Click on "Settings & privacy"
4. Click on "Settings"

![](./directions_media/facebook_settings.jpg)

5. Click on the "See more in Accounts Center" in the far-left column

![](./directions_media/instagram_accountsCenter.jpg)

6. Follow steps 5-7 for Instagram
7. Hit the checkbox for the facebook account and click on next

![](./directions_media/facebook_downloadSelection.jpg)

8. Follow steps 9-13 for instagram
## Instagram/Reels
To export Instagram content you will need login access to the account. The following directions are for a individual account. Institutional accounts should be the same, but if not the gist will be similar.
1. Login
2. Go to the bottom left-hand "More" three dashes icon and click on it

![](./directions_media/instagram_start.jpg)

3. In the pop-up menu (opens directly above the "More"), click on "Settings"
4. In the middle column on the top should be an Accounts Center box, Click on "See more in Accounts Center"

![](./directions_media/instagram_accountsCenter.jpg)

5. On the next screen, click on "Your information and permissions" on the left-hand column

![](./directions_media/instagram_yourAccount.jpg)

6. The center screen will change, click on "Download your information"
7. If you've requested a download recently, it will show up here. If not, click on "Download or transfer information"

![](./directions_media/instagram_download.jpg)

8. Hit the checkbox for the instagram account and click on next

![](./directions_media/instagram_downloadSelection.jpg)

9. Choose "All available information"
10. Choose Download to device (this will generate the zip file for transfer)
11. Make the following selections and then hit "Create files"
    * Date range: All time
    * Notify: enter an appropriate email address
    * Format: JSON (DON'T CHOOSE HTML)
    * Media quality: High

![](./directions_media/instagram_downloadFinal.jpg)

12. The account download generation process will start and you will be notified when it is ready via the selected email address. You may need to navigate back to the Download screen to access it
13. Download the zip file for transfer to the State Archives

## Upcoming development wishlist
Documenting additional things I will try to add/modify over time. Will be ~~struck through~~ if I am successful or deleted if it becomes apparent it is not possible.
1. Threads processing
2. Instagram institutional account processing (high priority)
3. HTML processing of posts for instances where transferor messed up the download process.
   1. Facebook
   2. Twixter
   3. Instagram
   4. Threads
4. TikTok (unlikely due to restrictions in Texas on use of TikTok but useful for gathering historic TikTok data for agencies that adopted the platform)
5. Nextdoor processing
6. LinkedIn processing