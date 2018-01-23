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
import os
import random
import urllib
import praw
import tweepy

#variables
TIMEBETWEENTWEETS = 15 * 60 

def getTwitter():
    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)

    return tweepy.API(auth)

def getReddit():
    return praw.Reddit(client_id = REDDIT_CLIENT_ID, client_secret = REDDIT_CLIENT_SECRET, user_agent = REDDIT_USER_AGENT)

def getImage():
    rPost = [post for post in getReddit().subreddit("dankmemes").new(limit = 10)][random.randint(0, 9)]
    data = urllib.request.urlretrieve(rPost.url, "temp.jpg") #get image from post and download

    return "temp.jpg"

def getQuote():
    rPost = [post for post in getReddit().subreddit("quotes").new(limit = 10)][random.randint(0, 9)]
    Quote = rPost.title

    if Quote.find("\"") != -1: #If quote is quoted, remove quotes
        Quote = Quote[Quote.find("\"") + 1 : str(Quote).rfind("\"")]

    if Quote.find(".") != -1:
        Quote = Quote[:Quote.find(".")]

    Quote += " "

    #emotes to use
    emotes = ["👅", "🤷‍", "🤷‍", "🌎", "💫", "✨", "🙈", "🙉", "🙊", "😁", "😀", "😝", "😇", "🤣", "😎", "😡", "😱", "😳", "💩", "😈", "👍", "👌", "🤞", "👊", "🌝", "🌚", "💫", "⭐", "🌈", "🔥", "🍌", "🍆", "🍾", "🍸", "🍷", "🥂", "🍻", "⚽", "🥊", "🎖", "🏵", "🖥", "🖲", "🔮", "🎈", "🎀", "🏮", "📯", "❤", "💯", "💯"] 

    for i in range(4):
        num = random.randint(0, len(emotes) - 1)
        Quote += emotes[num] + emotes[num] #add two times the same emoji

    return Quote

while True:
    #retrieve posts in last 3 days (1 tweet per hour) to check that the quote is not repeated, eliminate emojis
    statuses = getTwitter().user_timeline(user_id = "955467286323843076", count = 24 * 3)
    lastOnes = []
    for status in statuses:
        lastOnes.append(status.text[: status.text.rfind(" ")])

    quote = ""
    while quote == "" or (quote[: quote.rfind(" ")] in lastOnes):
        quote = getQuote() #while tweet was sent or is empty, try again

    img = getImage()
    
    getTwitter().update_with_media(img, status = quote) #send tweet
    print("tweet sent") 

    os.remove(img) #remove the image

    time.sleep(TIMEBETWEENTWEETS)
