#! /usr/bin/python3
from bs4 import BeautifulSoup
import re
import urllib.request
import os.path
import sys
from flask import Flask, render_template
from flask_caching import Cache
from functions import getKinotekaFile, getDBFile, getData, readFromDB
from tinydb import TinyDB
import json

config = {
    "DEBUG": True,
    "CACHE_TYPE": "UWSGICache",
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

with open("db/calendar.json", "r") as calendarFile:
    calendars = json.load(calendarFile)

@app.route("/")
@cache.cached(timeout=50)
def index():
    return render_template("index.html",  calendars=calendars)

@app.route("/<string:month_id>")
def month(month_id):

    month = month_id[:-4].title()
    year = month_id[-4:]
    try:
        int(year)
    except ValueError:
        return

    url = calendars[year][month]
    kinotekaFile = getKinotekaFile(url)
    dbFile = getDBFile(month_id)

    if os.path.exists(dbFile) and os.stat(dbFile).st_size != 0:
        table = readFromDB(dbFile)
    else:
        table = getData(url, kinotekaFile, dbFile)

    headings = table[0]
    data = table[1:]

    return render_template("table.html", headings=headings, data=data,
                                         calendars=calendars, monthName=month + " " + year,
                                         currentMonth = month_id, year = year)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
