from bs4 import BeautifulSoup
import urllib.parse
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from os import listdir
from os.path import isfile, join
import os
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
                executable_path = "/home/johk/Projects/Passive_RTY/chromedriver"

                # Uploads the twitch link to the service and then pulls the best quality video from the service
                driver = webdriver.Chrome(executable_path=executable_path, chrome_options=options)
                driver.get("http://en.fetchfile.net/?url={}".format(urllib.parse.quote(content)))
                sleep(20)
                pyautogui.click(909, 414)
                sleep(1)
                links = driver.find_elements_by_link_text('Download video')
                links[-1].click()
                sleep(3)
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
                                os.system("mv /home/johk/Downloads/{} /home/johk/Projects/Passive_RTY/merge".format(newfile))
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
        mypath = "/home/johk/Projects/Passive_RTY/merge"
        files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        print("Processing")
        submission = "concat:"
        for file in files:
            if file[-2:] != "md":
                os.system("ffmpeg -i {} -c copy -bsf:v h264_mp4toannexb -f mpegts {}.ts".format("/home/johk/Projects/Passive_RTY/merge/"+file, "/home/johk/Projects/Passive_RTY/ts/"+file.split(".")[0]))
                submission += "/home/johk/Projects/Passive_RTY/ts/"+file.split(".")[0]+".ts|"

        submission = submission[:-1]
        print("Compressing...")
        os.system('ffmpeg -i "{}" -c copy -bsf:a aac_adtstoasc output/output.mp4'.format(submission))
        print("Done!")
        os.system("rm ts/*")

    def upYoutube(self):
        print("Uploading to youtube...")
        title = self.title[0] + " & More -LiveStreamFails"
        os.system('youtube-upload --title="{}" --description="{}" --category="Entertainment" --tags="{}, twitch, '
                  'streamers, entertainment, comedy, ninja, pewdiepie, shroud, forsen, epicfail, livestreamfails, '
                  'livestream, stream, tyler1, greekgodx, content" --default-language="en" '
                  '--default-audio-language="en" --client-secrets="secret.json" {}'.format(title, title, title,
                                                                                           "output/output.mp4"))

        print("Successfully uploaded!")


