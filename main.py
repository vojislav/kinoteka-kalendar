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

config = {
    "DEBUG": True,
    "CACHE_TYPE": "UWSGICache",
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)

calendars =  {
    "2023": [
        ["Septembar 2023", "septembar2023", "https://www.danubeogradu.rs/2023/08/kinoteka-repertoari-za-septembar-2023/"],
        ["Avgust 2023", "avgust2023", "https://www.danubeogradu.rs/2023/07/kinoteka-repertoari-za-avgust-2023/"],
        ["Jul 2023", "jul2023", "https://www.danubeogradu.rs/2023/06/kinoteka-repertoari-za-jul-2023/"],
        ["Jun 2023", "jun2023", "https://www.danubeogradu.rs/2023/06/kinoteka-repertoari-za-jun-2023/"],
        ["Maj 2023", "maj2023", "https://www.danubeogradu.rs/2023/04/kinoteka-repertoari-za-maj-2023/"],
        ["April 2023", "april2023", "https://www.danubeogradu.rs/2023/03/kinoteka-repertoari-za-april-2023/"],
        ["Mart 2023", "mart2023", "https://www.danubeogradu.rs/2023/03/kinoteka-repertoari-za-mart-2023/"],
        ["Februar 2023", "februar2023", "https://www.danubeogradu.rs/2023/01/kinoteka-repertoari-za-februar-2023/"],
        ["Januar 2023", "januar2023", "https://www.danubeogradu.rs/2022/12/kinoteka-repertoari-za-januar-2023/"]
    ],
    "2022": [
        ["Decembar 2022", "decembar2022", "https://www.danubeogradu.rs/2022/11/kinoteka-repertoari-za-decembar-2022/"],
        ["Novembar 2022", "novembar2022", "https://www.danubeogradu.rs/2022/11/kinoteka-repertoari-za-novembar-2022/"],
        ["Oktobar 2022", "oktobar2022", "https://www.danubeogradu.rs/2022/09/kinoteka-repertoari-za-oktobar-2022/"],
        ["Septembar 2022", "septembar2022", "https://www.danubeogradu.rs/2022/08/kinoteka-repertoari-za-septembar-2022/"],
        ["Avgust 2022", "avgust2022", "https://www.danubeogradu.rs/2022/07/kinoteka-repertoari-za-avgust-2022/"],
        ["Jul 2022", "jul2022", "https://www.danubeogradu.rs/2022/06/kinoteka-repertoari-za-jul-2022/"],
        ["Jun 2022", "jun2022", "https://www.danubeogradu.rs/2022/05/kinoteka-repertoari-za-jun-2022/"],
        ["Maj 2022", "maj2022", "https://www.danubeogradu.rs/2022/04/kinoteka-repertoari-za-maj-2022/"],
        ["April 2022", "april2022", "https://www.danubeogradu.rs/2022/03/kinoteka-repertoari-za-april-2022/"],
        ["Mart 2022 - ne radi :(", "#", "https://www.danubeogradu.rs/2022/03/kinoteka-repertoari-za-mart-2022/"],
        ["Februar 2022", "februar2022", "https://www.danubeogradu.rs/2022/01/kinoteka-repertoari-za-februar-2022/"],
        ["Januar 2022", "januar2022", "https://www.danubeogradu.rs/2021/12/kinoteka-repertoari-za-januar-2022/"]
    ],
    "2021": [
        ["Decembar 2021", "decembar2021", "https://www.danubeogradu.rs/2021/11/kinoteka-repertoari-za-decembar-2021/"],
        ["Novembar 2021", "novembar2021", "https://www.danubeogradu.rs/2021/10/kinoteka-repertoari-za-novembar-2021/"],
        ["Oktobar 2021", "oktobar2021", "https://www.danubeogradu.rs/2021/09/kinoteka-repertoari-za-oktobar-2021/"],
        ["Septembar 2021", "septembar2021", "https://www.danubeogradu.rs/2021/08/kinoteka-repertoar-za-septembar-2021/"],
        ["Avgust 2021", "avgust2021", "https://www.danubeogradu.rs/2021/07/kinoteka-repertoar-za-avgust-2021/"],
        ["Jul 2021", "jul2021", "https://www.danubeogradu.rs/2021/06/kinoteka-repertoar-za-jul-2021/"],
        ["Jun 2021", "jun2021", "https://www.danubeogradu.rs/2021/05/kinoteka-repertoari-za-jun-2021/"],
        ["Maj 2021", "maj2021", "https://www.danubeogradu.rs/2021/04/kinoteka-repertoari-za-maj-2021/"],
        ["April 2021", "april2021", "https://www.danubeogradu.rs/2021/04/kinoteka-repertoari-za-april-2021/"],
        ["Mart 2021", "mart2021", "https://www.danubeogradu.rs/2021/02/kinoteka-repertoari-za-mart-2021/"],
        ["Februar 2021", "februar2021", "https://www.danubeogradu.rs/2021/01/kinoteka-repertoari-za-februar-2021/"],
        ["Januar 2021", "januar2021", "https://www.danubeogradu.rs/2020/12/kinoteka-repertoari-za-januar-2021/"]
    ]
}

@app.route("/")
@cache.cached(timeout=50)
def index():
    return render_template("index.html",  calendars=calendars)

@app.route("/<string:month_id>")
def month(month_id):
    year = month_id[-4:]
    for month in calendars[year]:
        if (month[1] == month_id):
            url = month[2]
            break;
    kinotekaFile = getKinotekaFile(url)
    dbFile = getDBFile(month_id)

    if os.path.exists(dbFile) and os.stat(dbFile).st_size != 0:
        table = readFromDB(dbFile)
    else:
        table = getData(url, kinotekaFile, dbFile)

    headings = table[0]
    data = []
    for row in table[1:]:
        data.append(row)

    return render_template("table.html", headings=table[0], data=data,
                                         calendars=calendars, monthName=month[0],
                                         currentMonth=month[1], year = year)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
