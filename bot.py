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

from secrets import *
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
TIMEBETWEENTWEETS = 15 * 60 
TIMEIFFAIL = 5 * 60

#Debug
ISFIRST = True

def getTwitter():
    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)

    return tweepy.API(auth)

def getReddit():
    return praw.Reddit(client_id = REDDIT_CLIENT_ID, client_secret = REDDIT_CLIENT_SECRET, user_agent = REDDIT_USER_AGENT)

def getImage():
    while True:
        timeLastTweet = datetime.datetime.now() - datetime.timedelta(seconds = TIMEBETWEENTWEETS)

        if ISFIRST:
            rPost = [post for post in getReddit().subreddit("dankmemes").new(limit = 10)] #for debug pruposes, if its first tweet, get from anywhere within 10 last posts
        else:
            rPost = [post for post in getReddit().subreddit("dankmemes").submissions(start = time.mktime(timeLastTweet.timetuple()))] #do same as in images

        if len(rPost) == 0:
            print("No posts aviable in dankmemes, sleeping") #if no posts aviable, sleep for a while
            time.sleep(TIMEIFFAIL)
        else: break

    imgPath = "temp.jpg"
    data = urllib.request.urlretrieve(rPost[random.randint(0, len(rPost) - 1)].url, imgPath) #get image from post and download

    img = Image.open(imgPath)

    if img.size[0] / img.size[1] > 3 or img.size[0] / img.size[1] < 0.33:
        return getImage() #If image has bad dimensions, dont use, get another

    return imgPath

def getQuote():
    while True:
        timeLastTweet = datetime.datetime.now() - datetime.timedelta(seconds = TIMEBETWEENTWEETS)

        if ISFIRST:
            rPost = [post for post in getReddit().subreddit("quotes").new(limit = 10)] #for debug pruposes, if its first tweet, get from anywhere within 10 last posts
        else:
            rPost = [post for post in getReddit().subreddit("quotes").submissions(start = time.mktime(timeLastTweet.timetuple()))] #do same as in images
            
        if len(rPost) == 0:
            print("No posts aviable in quotes, sleeping")
            time.sleep(TIMEIFFAIL)
        else: break

    Quote = rPost[random.randint(0, len(rPost) - 1)].title #get title of post

    if "[" in Quote: #if it starts with "[", its not a quote so get another
        return getQuote()

    if "\"" in Quote: #If quote is quoted, remove quotes
        Quote = Quote[Quote.find("\"") + 1 : str(Quote).rfind("\"")]

    if "“" in Quote: #check for various types of quotes
        Quote = Quote[Quote.find("“") + 1 : str(Quote).rfind("“")]

    if "." in Quote: #if there is a final point, remove it
        Quote = Quote[:Quote.rfind(".") - 1]

    if len(Quote.strip()) == 0: #If there is no quote (only whitespace), try again
        return getQuote()

    Quote += " " #add a space so emojis wont get too near text

    #emotes to use
    emotes = ["👅", "🤷‍", "🤷‍", "🌎", "💫", "✨", "🙈", "🙉", "🙊", "😁", "😀", "😝", "😇", "🤣", "😎", "😡", "😱", "😳", "💩", "😈", "👍", "👌", "🤞", "👊", "🌝", "🌚", "💫", "⭐", "🌈", "🔥", "🍌", "🍆", "🍾", "🍸", "🍷", "🥂", "🍻", "⚽", "🥊", "🎖", "🏵", "🖥", "🖲", "🔮", "🎈", "🎀", "🏮", "📯", "❤", "💯", "💯"] 

    for i in range(random.randint(2, 5)):
        num = random.randint(0, len(emotes) - 1)
        Quote += emotes[num] + emotes[num] #add two times the same emoji

    return Quote

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
        if e.api_code > 500: #If its greater than 500 is some kind of twitter problem, not mine, sleep and retry
            print("Unable to access tweeter, sleeping")
            time.sleep(TIMEIFFAIL)
            
            continue
            
    print("tweet sent") 

    os.remove(img) #remove the image

    ISFIRST = False

    time.sleep(TIMEBETWEENTWEETS)
