# -*- coding: utf-8 -*-
import datetime
import feedparser
import json
import urllib2
import sys


from flask import Flask
from flask import make_response
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
            'city':'Billerbeck,de',
            'currency_from':'EUR',
            'currency_to':'USD'
            }

WEATHER_URL_A = "http://api.openweathermap.org/data/2.5/weather?q="
WEATHER_URL_B = "&units=metric&APPID=841bc14a9faedaf4b13017e890cebd5f"
CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=7765d208a2b24b148f42c224f02becec"

@app.route("/")
#@app.route("/<publication>")
def home():
    # get customized headlines, based on user input or default
    publication = get_value_with_fallback("publication")
    articales = get_news(publication)

    # get customized weather based on user input or default
    city = get_value_with_fallback("city")
    weather = get_weather(city)

    #get customized currency based on user input or default
    currency_from = get_value_with_fallback("currency_from")
    currency_to = get_value_with_fallback("currency_to")
    rate, currencies = get_rates(currency_from, currency_to)

    #save cookie and return template
    response = make_response(render_template("home.html",articales=articales, weather=weather, currency_from=currency_from,
                                             currency_to=currency_to, rate=rate,currencies=sorted(currencies)))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)
    return response

def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS["publication"]
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']

def get_weather(query):
    query = query.replace(" ", "+")
    anfrage = WEATHER_URL_A + query + WEATHER_URL_B
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
                   "city": parsed["name"],
                   "country": parsed["sys"]["country"]
                   }
    return weather

def get_rates(frm, to):
    all_currency = urllib2.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate / frm_rate, parsed.keys())

def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]

if __name__ == '__main__':
    app.run(port=5000, debug=True)