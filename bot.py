#   This is the main file of the bot   
# 
#   Copyright (C) 2018  mocoma
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

#@postubot on twitter

from secrets import * #This is the secrets file, add yours, it must have the values of the consumers secret and key and access token and secret and reddits client id, client secret and user agent under the names below, in the getTwitter() and getReddit() functions
from PIL import Image
import time
import datetime
import os
import random
import urllib
import prawcore
import praw
import tweepy

#variables
TIMEBETWEENTWEETS = 1 * 60 * 60 #One hour
TIMEIFFAIL = 5 * 60

triedIds = []

#To get posts from hot instead of new
getHot = True

def getTwitter():
    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)

    return tweepy.API(auth)

def getReddit():
    return praw.Reddit(client_id = REDDIT_CLIENT_ID, client_secret = REDDIT_CLIENT_SECRET, user_agent = REDDIT_USER_AGENT)

def getClip(img):
    rgbImg = img.copy().convert("RGB")
    rgbPix = rgbImg.load()

    bounds = [0, 0, rgbImg.size[0], rgbImg.size[1]]

    #From top to bottom
    for y in range(1, rgbImg.size[1]): #Loop through every pixel
        for x in range(0, rgbImg.size[0]):
            Found = False

            R, G, B = rgbPix[x, y]
            diff = max(abs(R - G), abs(G - B), abs(R - B)) #Get max difference between pixels
            if diff > 60: #If difference its not too big, its a scale of gray
                bounds[1] = y
                Found = True
                break
            
        if Found:
            break   
        
    #From bottom to top
    for y in range(rgbImg.size[1] - 1, 0, -1):
        for x in range(0, rgbImg.size[0]):
            Found = False

            R, G, B = rgbPix[x, y]
            diff = max(abs(R - G), abs(G - B), abs(R - B))
            if diff > 60:
                bounds[3] = y
                Found = True
                break
            
        if Found: break

    #From left to right
    for x in range(0, rgbImg.size[0]):
        for y in range(1, rgbImg.size[1]):
            Found = False
            
            R, G, B = rgbPix[x, y]
            diff = max(abs(R - G), abs(G - B), abs(R - B))
            if diff > 60:
                bounds[0] = x
                Found = True
                break
            
        if Found: break

    #From right to left
    for x in range(rgbImg.size[0] - 1, 0, -1):
        for y in range(0, rgbImg.size[1]):
            Found = False
            
            R, G, B = rgbPix[x, y]
            diff = max(abs(R - G), abs(G - B), abs(R - B))
            if diff > 60:
                bounds[2] = x
                Found = True
                break
            
        if Found: break

    return  bounds

def getImage():
    while True:
        global getHot
        global triedIds

        tries = 0
        timeLastTweet = datetime.datetime.now() - datetime.timedelta(seconds = TIMEBETWEENTWEETS)

        if getHot:
            rPost = [post for post in getReddit().subreddit("dankmemes").hot(limit = 50)] #Get posts from HOT if we want to
        else:
            rPost = [post for post in getReddit().subreddit("dankmemes").submissions(start = time.mktime(timeLastTweet.timetuple()))] #do same as in images

        for submission in rPost: #Remove the tried ids
            if submission.id in triedIds:
                rPost.remove(submission.id)

        if len(rPost) == 0:
            print("No posts aviable in dankmemes, sleeping") #if no posts aviable, sleep for a while

            tries += 1
            if tries > TIMEBETWEENTWEETS / TIMEIFFAIL:
                getHot = True
                continue

            time.sleep(TIMEIFFAIL)
        else: break

    post = rPost[random.randint(0, len(rPost) - 1)]
    triedIds.append(post.id)

    imgPathJ = "temp.jpg"
    imgPathP = "temp.png"
    data = urllib.request.urlretrieve(post.url, imgPathJ) #get image from post and download

    with Image.open(imgPathJ) as img:
        clip = getClip(img)
        clipped = img.crop(clip)

        if clipped.size[0] / clipped.size[1] < 0.2 and clipped.size[0] / clipped.size[1] > 5: #If cropped image isnt valid, get another
            return getImage()

        clipped.save(imgPathP)

        os.remove(imgPathJ) #Remove jpg
        return imgPathP

def getQuote():
    while True:
        global getHot
        global triedIds

        tries = 0
        timeLastTweet = datetime.datetime.now() - datetime.timedelta(seconds = TIMEBETWEENTWEETS)
    
        if getHot:
            rPost = [post for post in getReddit().subreddit("quotes").hot(limit = 50)] #Same as images
        else:
            rPost = [post for post in getReddit().subreddit("quotes").submissions(start = time.mktime(timeLastTweet.timetuple()))] #do same as in images

        for submission in rPost:
            if submission.id in triedIds:
                rPost.remove(submission.id)
            
        if len(rPost) == 0:
            print("No posts aviable in quotes, sleeping")

            tries += 1
            if tries > TIMEBETWEENTWEETS / TIMEIFFAIL: #If we tried a lot of times, get Hot posts instead
                getHot = True
                continue

            time.sleep(TIMEIFFAIL)
        else: break

    post = rPost[random.randint(0, len(rPost) - 1)]
    triedIds.append(post.id)

    Quote = post.title #get title of post

    if "[" in Quote: #if it starts with "[", its not a quote so get another
        triedIds.append(post.id) #Add this to tried so we dont get in an infinite loop
        return getQuote()

    if "\"" in Quote: #If quote is quoted, remove quotes
        Quote = Quote[Quote.find("\"") + 1 : str(Quote).rfind("\"")]

    if "“" in Quote: #check for various types of quotes
        Quote = Quote[Quote.find("“") + 1 : str(Quote).rfind("“")]

    if "." in Quote: #if there is a final point, remove it
        Quote = Quote[:Quote.rfind(".")]

    if len(Quote.strip()) < 20 or len(Quote.strip()) > 240: #If there is no quote or its too short or too large, try again
        return getQuote()

    Quote += " " #add a space so emojis wont get too near text

    #emotes to use
    emotes = ["👅", "🤷‍", "🤷‍", "🌎", "💫", "✨", "🙈", "🙉", "🙊", "😁", "😀", "😝", "😇", "🤣", "😎", "😡", "😱", "😳", "💩", "😈", "👍", "👌", "🤞", "👊", "🌝", "🌚", "💫", "⭐", "🌈", "🔥", "🍌", "🍆", "🍾", "🍸", "🍷", "🥂", "🍻", "⚽", "🥊", "🎖", "🏵", "🖥", "🖲", "🔮", "🎈", "🎀", "🏮", "📯", "❤", "💯", "💯"] 

    for i in range(random.randint(2, 5)):
        num = random.randint(0, len(emotes) - 1)
        Quote += emotes[num] + emotes[num] #add two times the same emoji

    return Quote

def runBot():
    while True:
        #get data
        try:
            quote = getQuote()
            img = getImage()

        except prawcore.exceptions.ResponseException: #If some connection fails, retry after fail time
            print("Unable to access reddit, sleeping")
            time.sleep(TIMEIFFAIL)

            continue

        if os.stat(img).st_size > 3072 * 1000: #If file is too big, return
            print("File too big, retrying")

            continue

        try:
            getTwitter().update_with_media(img, status = quote) #send tweet (without quotes)

        except tweepy.TweepError as e:
            if e.api_code:
                if e.api_code > 500: #If its greater than 500 is some kind of twitter problem, not mine, sleep and retry
                    print("Unable to access tweeter, sleeping")
                    time.sleep(TIMEIFFAIL)

                    continue

        print("tweet sent") 

        os.remove(img) #remove the image

        triedIds = [] #reset tried ids

        getHot = False

        time.sleep(TIMEBETWEENTWEETS)

runBot()