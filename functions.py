#! /usr/bin/python3
from bs4 import BeautifulSoup
import re
import urllib.request
import os.path
import sys
#from tabulate import tabulate
import functools
from datetime import datetime
from tinydb import TinyDB
import json

class Film:
    def __init__(self, time, title, country, releaseYear, location, roles, director, tmdb_id):
        self.time = time
        self.title = title
        self.country = country
        self.releaseYear = releaseYear
        self.location = location
        self.roles = roles
        self.director = director
        self.tmdb_id = tmdb_id

class Date:
    numDates = 0
    def __init__(self, day, dateNum, month, monthNum, year):
        self.day = day
        self.dateNum = dateNum
        self.month = month
        self.monthNum = monthNum
        self.year = year
        self.films = []
        self.filmNum = 0
        Date.numDates += 1

    def newFilm():
        self.filmNum += 1

def compare(film1, film2):
    return film1.time < film2.time;

def getKinotekaFile(url):
    kinotekaFile = re.sub('https:.*?\/[0-9]+\/[0-9]+\/', '', url)
    kinotekaFile = re.sub('repertoar[i]?-za-', '', kinotekaFile)
    kinotekaFile = kinotekaFile.replace('/', '')

    return "kinotekafiles/" + kinotekaFile + (".html")

def getDBFile(month_id):
    return "db/" + month_id + ".json"

badTitles = ["dokumentarni film", "dugometražni dokumentarni film", "dugometražni dokumentarni", 
			 "kratki igrani film", "igrano-dokumenarni film", "Muzički dokumentarni film", 
			 "dokumenarni film", "dokumentarni fulm", "Projekcija restaurisane kopije filma", 
			 "(Restaurisana kopija filma)", "dokumenarno-igrani film", "dugometražni animirani",
			 "dokumentarni tv film", "Premijera dokumentarnog filma", "Restaurirana verzija",
			 "dugometražni animirani film", "kratki film"]

def getTMDBID(title, year):
    url = "https://api.themoviedb.org/3/search/movie?"
    params = {"query": title,
              "year": year,
              "include_adult": "false",
              "api_key": "00710da794dddf1fe6fce8c165a3c178"}
    
    full_url = url + urllib.parse.urlencode(params)

    with urllib.request.urlopen(full_url) as res:
        jsonRes = json.loads(res.read())
        if (len(jsonRes["results"]) == 0):
            return -1
        else:
            return jsonRes['results'][0]["id"]

def getData(url, kinotekaFile, dbFile):
    if not os.path.exists(kinotekaFile):
        urllib.request.urlretrieve(url, kinotekaFile)

    db = TinyDB(dbFile)

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
    originalTitleReg = re.compile('(?<=[0-9]{4}\)\n\n).*')
    rolesReg = re.compile('(?<=Uloge: ).*')
    serbDirectorReg = re.compile('(?<=Režija: ).*?(?=,|$)')
    serbDirectorReg2 = re.compile('(?<=Režija: ).*(?=,?)')
    # bukvalno jedan lik samo nece da radi sa ovim prvim regexom
    # da me ubijes ne znam sta je
    # Pavle Pavlovic u reziji Mladomira Purise Djordjevica for future reference
    forDirectorReg = re.compile('(?<=\().*(?=\))')

    # for dates
    dayReg = re.compile('.*?(?=,)')
    dateNumReg = re.compile('(?<=, ).*?(?=\.)')
    monthReg = re.compile('(?<=[0-9]. ).*?(?= )')
    yearReg = re.compile('(?<=[a-z]\s).*?(?=\.)')

    # list of all dates
    dates = {}

    location = ""

    months = {
        "januar" : 1,
        "februar" : 2,
        "mart" : 3,
        "april" : 4,
        "maj" : 5,
        "jun" : 6,
        "jul" : 7,
        "avgust" : 8,
        "septembar" : 9,
        "oktobar" : 10,
        "novembar" : 11,
        "decembar" : 12
    }

    for br in soup.find_all('br'):
        br.replace_with('\n')

    for p in soup.find_all(['p', 'h2']):
        text = p.get_text().replace("…","")
        #print(text)

        if (uzunReg.search(text) != None):
            location = "Uzun Mirkova"
        elif (kosovskaReg.search(text) != None):
            location = "Kosovska"

        filmMatch = filmReg.search(text)
        dateMatch = dateReg.search(text)

        if (dateMatch != None):
            day = dayReg.search(dateMatch.group()).group()
            dateNum = dateNumReg.search(dateMatch.group()).group()
            month = monthReg.search(dateMatch.group()).group()
            monthNum = months[month.lower()]
            year = yearReg.search(dateMatch.group()).group()
            newDate = Date(day, int(dateNum), month, int(monthNum), year)
            monthAndDate = str(monthNum) + " " + dateNum
            if (dates.get(monthAndDate) == None):
                dates[monthAndDate] = newDate
            #dates.append(newDate)

        if (filmMatch != None):
            time = timeReg.search(filmMatch.group()).group().replace(".", ":")

            title = titleReg.search(filmMatch.group()).group()

            parantheses = paranthesesReg.search(filmMatch.group()).group()

            country = countryReg.search(parantheses).group().replace("/", "").replace(",", "")

            releaseYear = ""
            if releaseYearReg.search(parantheses) != None:
                releaseYear = releaseYearReg.search(parantheses).group()

            originalTitle = originalTitleReg.search(text)

            if (originalTitle != None and
                    rolesReg.search(originalTitle.group()) == None and
                    serbDirectorReg.search(originalTitle.group()) == None and
                    originalTitle.group() not in badTitles):
                    title = originalTitle.group()

            roles = rolesReg.search(text)
            if roles != None:
                roles = roles.group()

            director = ""
            if (serbDirectorReg.search(text) == None):
                if (serbDirectorReg2.search(text) != None):
                    director = serbDirectorReg2.search(text).group()
            else:
                director = serbDirectorReg.search(text).group()

            if (director):
                forDirector = forDirectorReg.search(director)
            if (forDirector != None):
                director = forDirector.group()

            tmdb_id = getTMDBID(title, releaseYear)

            # shorten long film titles
            maxTitleLength = 60
            if (len(title) > maxTitleLength):
                title = title[:maxTitleLength] + "..."

            newFilm = Film(time, title, country, releaseYear, location, roles, director, tmdb_id)
            #dates[Date.numDates-1].films.append(newFilm)
            dates[monthAndDate].films.append(newFilm)

    #for date in dates:
    #    print("%s, %s. %s" % (date.day, date.dateNum, date.month))
    #    for film in date.films:
    #        print("%s - %s (%s) - %s\nUloge: %s\nRezija: %s" % (film.time, film.title, film.releaseYear, film.location, film.roles, film.director))

    sortedDates = sorted(dates.items(), key=lambda x : (x[1].year, x[1].monthNum, x[1].dateNum) );

    table = [['Datum', 'Vreme', 'Naslov', 'Lokacija']]
    for datePair in sortedDates:
        date = datePair[1]
        date.films.sort(key = lambda film: datetime.strptime(film.time, '%H:%M'))
        row = []
        dateStr = date.day + ", " + str(date.dateNum) + ". " + date.month
        row.append(dateStr)

        filmList = []
        #dateAdded = 0
        for film in date.films:
            #if (dateAdded == 1):
            #    row.append("")
            row.append(film.time)
            row.append(film.title + " (" + film.releaseYear + ") (dir. " + film.director + ")")
            row.append(film.location)
            row.append(len(date.films))
            row.append(film.tmdb_id)
            table.append(row)

            filmList.append([film.time, film.title, film.releaseYear,
                             film.director, film.location, film.tmdb_id])
            #dateAdded = 1
            row = []
        if (filmList):
            newDoc = dict({dateStr: filmList})
            db.insert(newDoc)

    return table

def readFromDB(dbFile):
    table = [['Datum', 'Vreme', 'Naslov', 'Lokacija']]
    db = TinyDB(dbFile)

    for day in db.all():
        row = []
        dateStr = list(day.keys())[0]
        row.append(dateStr)

        films = list(day.values())[0]
        for film in films:
            filmTime = film[0]
            filmTitle = film[1]
            filmReleaseYear = film[2]
            filmDirector = film[3]
            filmLocation = film[4]
            filmID = film[5]
            titleStr = filmTitle + " (" + filmReleaseYear + ") (dir. " + filmDirector + ")"
            row.append(filmTime)
            row.append(titleStr)
            row.append(filmLocation)
            row.append(len(films))
            row.append(filmID)
            table.append(row)
            row = []

    return table

#url = "https://www.danubeogradu.rs/2021/05/kinoteka-repertoari-za-jun-2021/"
#kinotekaFile = getKinotekaFile(url)
#table = getData(url, kinotekaFile)
#print(tabulate(table, headers='firstrow', tablefmt='grid'))
