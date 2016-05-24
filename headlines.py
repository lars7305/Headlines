# -*- coding: utf-8 -*-
import feedparser
import json
import sys
import urllib
import urllib2



from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

# Code umstellen, von asii auf utf8, damit auch Umlaute encodet werden können
if sys.version_info.major < 3:
    reload(sys)
sys.setdefaultencoding('utf8')

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640'}

BBC_FEED = "http://feeds.bbci.co.uk/news/rss.xml"

DEFAULTS = {'publication':'bbc',
            'city':'Billerbeck,de'}

@app.route("/")
#@app.route("/<publication>")
def home():
    # get customized headlines, based on user input or default
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articales = get_news(publication)
    # get customized weather based on user input or default
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)
    return render_template("home.html", articales=articales, weather=weather)

def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS["publication"]
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']

def get_weather(query):
    query = query.replace(" ", "+")
    anfrage = "http://api.openweathermap.org/data/2.5/weather?q=" \
              + query + "&units=metric&APPID=841bc14a9faedaf4b13017e890cebd5f"
    try:
        response = urllib2.urlopen(anfrage)
    except:
        print anfrage
    mydata = response.read()
    parsed = json.loads(mydata)
    weather = None
    if parsed.get("weather"):
        weather = {"description":
                       parsed["weather"][0]["description"],
                   "temperature": parsed["main"]["temp"],
                   "city": parsed["name"]
                   }
    return weather


if __name__ == '__main__':
    app.run(port=5000, debug=True)