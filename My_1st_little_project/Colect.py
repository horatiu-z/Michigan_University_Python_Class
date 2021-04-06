import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
import re
import sqlite3


#ignore SSL certificate error:
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

conn = sqlite3.connect('filme.sqlite')
cur=conn.cursor()

cur.executescript('''
CREATE TABLE IF NOT EXISTS Movies(
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT UNIQUE,
score INTEGER);

CREATE TABLE IF NOT EXISTS Actors(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
apparitions INTEGER);

CREATE TABLE IF NOT EXISTS Link(
movie_id INTEGER,
actor_id INTEGER,
PRIMARY KEY(movie_id,actor_id))
''')

baseurl='https://www.imdb.com/find?'
file = input('file?')
if len(file) < 1:
    file='Movies.txt'

fhopen=open(file)
for line in fhopen:
    parms=dict()
    parms['q'] = line

    imdburl = baseurl + urllib.parse.urlencode(parms)
    #(imdburl)

    imdbsrch = urllib.request.urlopen(imdburl, context=ctx).read()
    #print(imdbsrch)
    isoup = BeautifulSoup(imdbsrch,'html.parser')
    reslst=list()
    tags=isoup.find_all('td',{'class':"result_text"})
    tag = tags[0]
    ancor = str(tag('a'))
    x=re.findall('[a-z]*/title/[a-z0-9]*',ancor)
    y=x[0]
    print (y)

    imdbbase='https://www.imdb.com'
    resurl=imdbbase+y
    print(resurl)
    htmlres=urllib.request.urlopen(resurl,context=ctx).read()
    irsoup = BeautifulSoup(htmlres,'html.parser')
    cast=irsoup.find_all('table',{'class':'cast_list'})
    for actor in cast:
        name=str(actor('a'))
        actorname=re.findall('[a-z]* alt="([A-Za-z]* [A-Za-z]*)', name)
    for rname in actorname:
        cur.execute('''INSERT OR IGNORE INTO Movies(title) VALUES (?)''',(line,))
        cur.execute('''SELECT id FROM Movies WHERE title=?''',(line,))
        movie_id=cur.fetchone()[0]

        cur.execute('''SELECT name FROM Actors WHERE name=?''',(rname,))
        linie=cur.fetchone()
        print(linie)
        if linie == None:
            cur.execute('''INSERT INTO Actors(name,apparitions) VALUES (?,?)''',(rname,1))
        else:
            cur.execute('''UPDATE Actors SET apparitions=apparitions+1 WHERE name=?''',(rname,))
        cur.execute('''SELECT id FROM Actors WHERE name=?''',(rname,))
        actor_id = cur.fetchone()[0]

        cur.execute('''INSERT OR IGNORE INTO Link(movie_id,actor_id) VALUES(?,?)''',(movie_id,actor_id))
        conn.commit()
