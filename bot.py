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
import time
import datetime
import os
import random
import urllib
import praw
import tweepy

#variables
TIMEBETWEENTWEETS = 15 * 60 
TIMEIFFAIL = 10 * 60

def getTwitter():
    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)

    return tweepy.API(auth)

def getReddit():
    return praw.Reddit(client_id = REDDIT_CLIENT_ID, client_secret = REDDIT_CLIENT_SECRET, user_agent = REDDIT_USER_AGENT)

def getImage():
    while True:
        timeLastTweet = datetime.datetime.now() - datetime.timedelta(seconds = TIMEBETWEENTWEETS)
        rPost = [post for post in getReddit().subreddit("dankmemes").submissions(start = time.mktime(timeLastTweet.timetuple()))] #get only posts since last tweet, so I dont repeat

        if len(rPost) == 0:
            print("No posts aviable, sleeping") #if no posts aviable, sleep for a while
            time.sleep(TIMEIFFAIL)
        else: break
   
    data = urllib.request.urlretrieve(rPost[random.randint(0, len(rPost) - 1)].url, "temp.jpg") #get image from post and download

    return "temp.jpg"

def getQuote():
    while True:
        timeLastTweet = datetime.datetime.now() - datetime.timedelta(seconds = TIMEBETWEENTWEETS)
        rPost = [post for post in getReddit().subreddit("quotes").submissions(start = time.mktime(timeLastTweet.timetuple()))] #do same as in images

        if len(rPost) == 0:
            print("No posts aviable, sleeping")
            time.sleep(TIMEIFFAIL)
        else: break

    Quote = rPost[random.randint(0, len(rPost) - 1)].title #get title of post

    if Quote.find("[") != -1: #if it starts with "[", its not a quote so get another
        return getQuote()

    if Quote.find("\"") != -1: #If quote is quoted, remove quotes
        Quote = Quote[Quote.find("\"") + 1 : str(Quote).rfind("\"")]

    if Quote.find("“") != -1: #check for various types of quotes
        Quote = Quote[Quote.find("“") + 1 : str(Quote).rfind("“")]

    if Quote.find("'") != -1:
        Quote = Quote[Quote.find("'") + 1 : str(Quote).rfind("'")]

    if Quote.find(".") != -1: #if there is a final point, remove it
        Quote = Quote[:Quote.find(".")]

    Quote = "\"" + Quote + "\" " #add a space so emojis wont get too near text, add quotes for better testing for equal ones

    #emotes to use
    emotes = ["👅", "🤷‍", "🤷‍", "🌎", "💫", "✨", "🙈", "🙉", "🙊", "😁", "😀", "😝", "😇", "🤣", "😎", "😡", "😱", "😳", "💩", "😈", "👍", "👌", "🤞", "👊", "🌝", "🌚", "💫", "⭐", "🌈", "🔥", "🍌", "🍆", "🍾", "🍸", "🍷", "🥂", "🍻", "⚽", "🥊", "🎖", "🏵", "🖥", "🖲", "🔮", "🎈", "🎀", "🏮", "📯", "❤", "💯", "💯"] 

    for i in range(random.randint(2, 5)):
        num = random.randint(0, len(emotes) - 1)
        Quote += emotes[num] + emotes[num] #add two times the same emoji

    return Quote

while True:
    #get data
    quote = getQuote() 
    img = getImage()
    
    getTwitter().update_with_media(img, status = quote.replace("\"", "")) #send tweet (without quotes)
    print("tweet sent") 

    os.remove(img) #remove the image

    time.sleep(TIMEBETWEENTWEETS)
