#! /usr/bin/python3
from bs4 import BeautifulSoup
import re
from tabulate import tabulate
import urllib.request
import os.path
import sys

class Film:
    def __init__(self, time, title, country, releaseYear, location, roles, director):
        self.time = time
        self.title = title
        self.country = country
        self.releaseYear = releaseYear
        self.location = location
        self.roles = roles
        self.director = director

class Date:
    numDates = 0
    def __init__(self, day, dateNum, month, year):
        self.day = day
        self.dateNum = dateNum
        self.month = month
        self.year = year
        self.films = []
        self.filmNum = 0
        Date.numDates += 1

    def newFilm():
        self.filmNum += 1

"""
https://www.danubeogradu.rs/2020/12/kinoteka-repertoari-za-januar-2021/
https://www.danubeogradu.rs/2021/01/kinoteka-repertoari-za-februar-2021/
https://www.danubeogradu.rs/2021/02/kinoteka-repertoari-za-mart-2021/
https://www.danubeogradu.rs/2021/04/kinoteka-repertoari-za-april-2021/
https://www.danubeogradu.rs/2021/04/kinoteka-repertoari-za-maj-2021/'
"""

if (len(sys.argv) == 2):
    url = sys.argv[1]
else:
    print("Too few arguments.")
    exit()

kinotekaFile = re.sub('https:.*?\/[0-9]+\/[0-9]+\/', '', url)
kinotekaFile = re.sub('repertoari-za-', '', kinotekaFile)
kinotekaFile = kinotekaFile.replace('/', '')

kinotekaFile += ".html"

if not os.path.exists(kinotekaFile):
    urllib.request.urlretrieve(url, kinotekaFile)

with open(kinotekaFile) as fp:
    soup = BeautifulSoup(fp, "lxml")

uzunReg = re.compile("Uzun Mirkova 1")
kosovskaReg = re.compile("Kosovska 11")

dateReg = re.compile('Č?[A-Z]?[a-z]+, [0-9]+\. [a-z]+ [0-9]+\.')
filmReg = re.compile('[0-9]{2}\.[0-9]{2} .* \(.*\)')

# for films
timeReg = re.compile('[0-9]{2}\.[0-9]{2}')
titleReg = re.compile('(?<=[0-9]{2}\.[0-9]{2} ).*?(?= \()')
paranthesesReg = re.compile('(?<=\().*(?=\))')
countryReg = re.compile('^.{3}')
releaseYearReg = re.compile('[0-9]{4}')
rolesReg = re.compile('(?<=Uloge: ).*')
serbDirectorReg = re.compile('(?<=Režija: ).*?(?=,|$)')
serbDirectorReg2 = re.compile('(?<=Režija: ).*(?=,?)')
# bukvalno jedan lik samo nece da radi sa ovim prvim regexom
# ubi me ako znam sta je
# Pavle Pavlovic u reziji Mladomira Purise Djordjevica for future reference
forDirectorReg = re.compile('(?<=\().*(?=\))')

# for dates
dayReg = re.compile('.*?(?=,)')
dateNumReg = re.compile('(?<=, ).*?(?=\.)')
monthReg = re.compile('(?<=[0-9]. ).*?(?= )')
yearReg = re.compile('(?<=[a-z]\s).*?(?=\.)')

# list of all dates
dates = []

location = ""

for br in soup.find_all('br'):
    br.replace_with('\n')

for p in soup.find_all(['p', 'h2']):
    text = p.get_text().replace("…","")

    if (uzunReg.search(text) != None):
        location = "Uzun Mirkova"
    if (kosovskaReg.search(text) != None):
        location = "Kosovska"

    filmMatch = filmReg.search(text)
    dateMatch = dateReg.search(text)

    if (dateMatch != None):
        day = dayReg.search(dateMatch.group()).group()
        dateNum = dateNumReg.search(dateMatch.group()).group()
        month = monthReg.search(dateMatch.group()).group()
        year = yearReg.search(dateMatch.group()).group()
        newDate = Date(day, dateNum, month, year)
        dates.append(newDate)

    if (filmMatch != None):
        time = timeReg.search(filmMatch.group()).group().replace(".", ":")

        title = titleReg.search(filmMatch.group()).group()

        parantheses = paranthesesReg.search(filmMatch.group()).group()

        country = countryReg.search(parantheses).group().replace("/", "").replace(",", "")

        releaseYear = releaseYearReg.search(parantheses).group()

        roles = rolesReg.search(text)
        if roles != None:
            roles = roles.group()

        director = serbDirectorReg.search(text)
        if (director == None):
            director = serbDirectorReg2.search(text).group()
        else:
            director = director.group()
        forDirector = forDirectorReg.search(director)
        if (forDirector != None):
            director = forDirector.group()

        newFilm = Film(time, title, country, releaseYear, location, roles, director)
        dates[Date.numDates-1].films.append(newFilm)

#for date in dates:
#    print("%s, %s. %s" % (date.day, date.dateNum, date.month))
#    for film in date.films:
#        print("%s - %s (%s) - %s\nUloge: %s\nRezija: %s" % (film.time, film.title, film.releaseYear, film.location, film.roles, film.director))

table = [['Datum', 'Vreme', 'Naslov', 'Lokacija']]
for date in dates:
    row = []
    row.append(date.day + ", " + date.dateNum + ". " + date.month)
    dateAdded = 0
    for film in date.films:
        if (dateAdded == 1):
            row.append("")
        row.append(film.time)
        row.append(film.title + " (" + film.releaseYear + ") (dir. " + film.director + ")")
        row.append(film.location)
        table.append(row)
        dateAdded = 1
        row = []

print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))
