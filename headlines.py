import json
import urllib

import feedparser

from flask import Flask
from flask import request
from flask import render_template

APP = Flask(__name__)

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'publication': 'bbc', 'city': 'Winnipeg, CA', 'currency_from': 'GBP', 'currency_to': 'USD'}
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=cb932829eacb6a0e9ee4f38bfbf112ed"

CURRENCY_URL = "https://openexchangerates.org//api/latest.json?app_id=ec59c8967d854d44bee8cff24525a050"

@APP.route("/")

def home():
    """
    Function
    """
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles = get_news(publication)
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    weather = get_weather(city)
    currency_from = request.args.get("currency_from")
    if not currency_from:
        currency_from = DEFAULTS['currency_from']
        currency_to = request.args.get("currency_to")
    if not currency_to:
        currency_to = DEFAULTS['currency_to']
        rate, currencies = get_rate(currency_from, currency_to)
    return render_template("home.html", articles=articles, weather=weather, currency_from=currency_from, currency_to=currency_to, rate=rate, currencies=sorted(currencies))

def get_news(publication="bbc"):
    """
    Function
    """
    query = request.args.get("publication")
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS["publication"]
    else:
        publication = query.lower()
    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']

def get_weather(query):
    """
    Get Weather Function
    """
    api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&APPID=cb932829eacb6a0e9ee4f38bfbf112ed"
    query = urllib.parse.quote(query)
    #url = api_url.format(query)
    url = WEATHER_URL.format(query)
    data = urllib.request.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get("weather"):
        weather = {"description": parsed["weather"][0]["description"],
                   "temperature":parsed["main"]["temp"],
                   "city":parsed["name"],
                   "country": parsed["sys"]["country"]},
    return weather

def get_rate(frm, to):
    """
    Get Rates
    """
    all_currency = urllib.request.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate / frm_rate, parsed.keys())

if __name__ == '__main__':
    APP.run(port=5000, debug=True)
