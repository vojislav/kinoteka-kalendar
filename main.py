#! /usr/bin/python3
from bs4 import BeautifulSoup
import re
import urllib.request
import os.path
import sys
from flask import Flask, render_template
from functions import getKinotekaFile, getData

app = Flask(__name__)

months = [
     ["Januar 2021", "jan2021", "https://www.danubeogradu.rs/2020/12/kinoteka-repertoari-za-januar-2021/"]
    ,["Februar 2021", "feb2021", "https://www.danubeogradu.rs/2021/01/kinoteka-repertoari-za-februar-2021/"]
    ,["Mart 2021", "mart2021", "https://www.danubeogradu.rs/2021/02/kinoteka-repertoari-za-mart-2021/"]
    ,["April 2021", "apr2021", "https://www.danubeogradu.rs/2021/04/kinoteka-repertoari-za-april-2021/"]
    ,["Maj 2021", "maj2021", "https://www.danubeogradu.rs/2021/04/kinoteka-repertoari-za-maj-2021/"]
]

@app.route("/")
def index():
    return render_template("index.html",  months=months)

@app.route("/<string:month_id>")
def month(month_id):
    for month in months:
        if (month[1] == month_id):
            url = month[2]
            break;
    kinotekaFile = getKinotekaFile(url)

    table = getData(url, kinotekaFile)
    headings = table[0]
    data = []
    for row in table[1:]:
        data.append(row)

    return render_template("table.html", headings=table[0], data=data,
                                         months=months, monthName=month[0])

if __name__ == "__main__":
    app.run(host="0.0.0.0")
