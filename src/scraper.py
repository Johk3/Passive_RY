from bs4 import BeautifulSoup
import urllib.parse
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from os import listdir
from os.path import isfile, join
import os
import glob
import subprocess
import pyautogui


class VideoScraper:
    def __init__(self, reddit):
        self.reddit = reddit
        self.title = []
        self.ups = []
        self.awards = []
        self.files = []
    
    def batchContent(self, sub, lim):
        print("Removing previous merge files...")
        os.system("rm -rf merge/*")
        subdata = self.reddit.subreddit(sub).hot(limit=lim)
        for submission in subdata:
            self.title.append(submission.title)
            self.ups.append(submission.ups)
            self.awards.append(submission.total_awards_received)
            
            # Retrieve the link to the video by using BS4
            try:
                mypath = "/home/johk/Downloads/"
                # This is for checking if the new file has downloaded
                pastfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
                downloaded = False

                content = submission.media_embed["content"]
                soup = BeautifulSoup(content, features="html.parser")
                data = soup.find("iframe")
                content = data["src"]

                # Downloading the video with selenium
                options = Options()
                # You need to have Ublock extension here to block all the ads that will get in the way
                options.add_argument('load-extension=' + '/home/johk/Documents/1.19.2_0')
                # options.add_extension('/home/johk/Documents/ublock.zip')
                executable_path = "/home/johk/Projects/Passive_RY/chromedriver"

                # Uploads the twitch link to the service and then pulls the best quality video from the service
                driver = webdriver.Chrome(executable_path=executable_path, chrome_options=options)
                driver.get("http://en.fetchfile.net/?url={}".format(urllib.parse.quote(content)))
                sleep(10)
                pyautogui.click(909, 414)
                sleep(1)
                links = driver.find_elements_by_link_text('Download video')
                links[-1].click()
                sleep(4)
                print("Extra check")
                check = [f for f in listdir(mypath) if isfile(join(mypath, f))]
                if len(check) != len(pastfiles):
                    while not downloaded:
                        newfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
                        if len(newfiles) > len(pastfiles):
                            still_downloading = False
                            for file in newfiles:
                                if file.split(".")[-1] == "crdownload":
                                    still_downloading = True
                                    print("Waiting...")

                            if not still_downloading:
                                downloaded = True
                                print("Done downloading")

                                newfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
                                newfile = list(set(newfiles) - set(pastfiles))[0]
                                self.files.append(newfile)
                                print("Processing new file {}".format(newfile))
                                os.system("mv /home/johk/Downloads/{} /home/johk/Projects/Passive_RY/merge".format(newfile))
                                print("Done!")
                                driver.close()

                        sleep(1)
                else:
                    print("Skipping")
                    driver.close()
            except Exception as e:
                print(e)
                print("Skipping")

    print("Done batching content!")

    def mergeContent(self):
        print("Removing previous files...")
        os.system("rm -rf output/*")
        os.system("rm -rf ts/*")
        print("Starting to merge the contents together...")
        print("Sorting based on date...")
        search_dir = "/home/johk/Projects/Passive_RY/merge/"
        # remove anything from the list that is not a file (directories, symlinks)
        # thanks to J.F. Sebastion for pointing out that the requirement was a list
        # of files (presumably not including directories)
        files = list(filter(os.path.isfile, glob.glob(search_dir + "*")))
        files.sort(key=lambda x: os.path.getmtime(x))
        print("Processing")
        submission = "concat:"
        for file in files:
            if file[-2:] != "md":
                if file.split(".")[-1] == "mp4":
                    file = file.split(".")[0]
                    file = file.split("/")[-1]
                    os.system("ffmpeg -i {}.mp4 -c copy -bsf:v h264_mp4toannexb -f mpegts {}.ts".format("/home/johk/Projects/Passive_RY/merge/"+file, "/home/johk/Projects/Passive_RY/ts/"+file))
                    submission += "/home/johk/Projects/Passive_RY/ts/"+file+".ts|"

        submission = submission[:-1]
        print("Compressing...")
        os.system('ffmpeg -i "{}" -c copy -bsf:a aac_adtstoasc output/output.mp4'.format(submission))
        print("Done!")

    def upYoutube(self):
        print("Uploading to youtube...")
        tags = ""
        for i in range(5):
            tags += "{}, ".format(self.title[i])
        title = self.title[0] + " & More -LiveStreamFails"
        os.system('youtube-upload --title="{}" --description="{}" --category="Entertainment" --tags="{} twitch, '
                  'streamers, entertainment, comedy, ninja, pewdiepie, shroud, forsen, epicfail, livestreamfails, '
                  'livestream, stream, tyler1, greekgodx, content" --default-language="en" '
                  '--default-audio-language="en" --client-secrets="secret.json" {}'.format(title, title, tags,
                                                                                           "output/output.mp4"))

        print("Successfully uploaded!")


