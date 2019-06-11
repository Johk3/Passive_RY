import json
import src.scraper as scraper
import praw

if __name__ == "__main__":
    print("Logging in...")
    with open('creds/creds.json') as json_file:  
        data = json.load(json_file)

        reddit = praw.Reddit(client_id=data["id"],
                         client_secret=data["secret"],
                         password=data["password"],
                         user_agent='testscript by /u/fakebot3',
                         username=data["username"])
    
    videoScraper = scraper.VideoScraper(reddit)
    print("Getting money with {}...".format(reddit.user.me()))
    # videoScraper.batchContent("LivestreamFail", 25)
    # videoScraper.mergeContent()
    videoScraper.upYoutube()
    print("Done!")