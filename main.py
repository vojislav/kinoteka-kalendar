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
    ,["Jun 2021", "jun2021", "https://www.danubeogradu.rs/2021/05/kinoteka-repertoari-za-jun-2021/"]
    ,["Jul 2021", "jul2021", "https://www.danubeogradu.rs/2021/06/kinoteka-repertoar-za-jul-2021/"]
    ,["Avgust 2021", "avgust2021", "https://www.danubeogradu.rs/2021/07/kinoteka-repertoar-za-avgust-2021/"]
    ,["Septembar 2021", "septembar2021", "https://www.danubeogradu.rs/2021/08/kinoteka-repertoar-za-septembar-2021/"]
    ,["Oktobar 2021", "oktobar2021", "https://www.danubeogradu.rs/2021/09/kinoteka-repertoari-za-oktobar-2021/"]
    ,["Novembar 2021", "novembar2021", "https://www.danubeogradu.rs/2021/10/kinoteka-repertoari-za-novembar-2021/"]
    ,["Decembar 2021", "decembar2021", "https://www.danubeogradu.rs/2021/11/kinoteka-repertoari-za-decembar-2021/"]
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
