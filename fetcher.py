from bs4 import BeautifulSoup
import random
import re
import requests


def get_dom(url, headers=None):
    if not headers:
        headers = {}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print url
        return False
    dom = BeautifulSoup(r.text, "html.parser")
    return dom


def get_azlyrics(artist, title, raw=False):
    artist = artist.replace(' ', '').lower()
    title = title.replace(' ', '').lower()
    url = "http://www.azlyrics.com/lyrics/%s/%s.html" % (artist, title)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'}
    dom = get_dom(url, headers)
    if not dom:
        return False
    try:
        lyrics = dom.find('div', class_='ringtone').find_next('div').text
    except AttributeError:
        return False
    if raw:
        return lyrics
    lyrics_array = lyrics.split('\n')
    del lyrics_array[0]
    del lyrics_array[0]
    for i in range(0,len(lyrics_array)):
        lyrics_array[i] = lyrics_array[i].replace('\r','')
    return lyrics_array


def get_metrolyrics(artist, title, raw=False):
    artist = artist.replace(' ', '-').lower()
    title = title.replace(' ', '-').lower()
    url = "http://www.metrolyrics.com/%s-lyrics-%s.html" % (title, artist)
    dom = get_dom(url)
    if not dom:
        return False
    if raw:
        return dom.find('div', id='lyrics-body-text').text
    lyrics_array = []
    for v in dom.find_all('p', class_='verse'):
        lyrics_array = lyrics_array + v.text.split('\n')
    return lyrics_array


def get_lyricsfreak(artist, title, raw=False):
    url = "http://www.lyricsfreak.com/search.php?a=search&type=song&q=%s" % title
    dom = get_dom(url)
    if not dom:
        return False
    try:
        lyrics_link = dom.find(string=re.compile(artist)).find_next('a')['href']
    except AttributeError:
        return False
    lyrics_link = "http://www.lyricsfreak.com" + lyrics_link
    dom = get_dom(lyrics_link)
    if raw:
        return dom.find('div', id='content_h').text
    lyrics_array = []
    lyrics = dom.find('div', id='content_h').contents
    while True:
        if len(lyrics) > 1:
            lyrics_array.append(lyrics[0])
            lyrics = lyrics[1].contents
        else:
            try:
                lyrics = lyrics[0].contents
            except AttributeError:
                lyrics_array.append(lyrics[0])
                break
    return lyrics_array


def get_songlyrics(artist, title, raw=False):
    artist = artist.replace(' ', '-').lower()
    title = title.replace(' ', '-').lower()
    url = "http://www.songlyrics.com/%s/%s-lyrics/" % (artist, title)
    dom = get_dom(url)
    if not dom:
        return False
    lyrics = dom.find('p', id='songLyricsDiv').text
    if raw:
        return lyrics
    lyrics_array = lyrics.split('\n')
    return lyrics_array


def get_musixmatch(artist, title, raw=False):
    artist = artist.replace(' ', '-')
    title = title.replace(' ', '-')
    url = "https://www.musixmatch.com/lyrics/%s/%s" % (artist, title)
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'}
    dom = get_dom(url, headers)
    if not dom:
        return False
    try:
        lyrics = dom.find('div', id='selectable-lyrics').text
    except AttributeError:
        return False
    if raw:
        return lyrics
    lyrics_array = lyrics.split('\n')
    return lyrics_array


def get_lyrics(artist, title, sites_attempted=None):
    available_sites = {'musixmatch.com': get_musixmatch, 'songlyrics.com': get_songlyrics,
                       'lyricsfreak.com': get_lyricsfreak, 'metrolyrics.com': get_metrolyrics,
                       'azlyrics.com': get_azlyrics}
    if not sites_attempted:
        sites_attempted = []
    if len(sites_attempted) == len(available_sites):
        return False
    chosen_site = ''
    while chosen_site in sites_attempted or chosen_site == '':
        chosen_site = random.choice(available_sites.keys())
    sites_attempted.append(chosen_site)
    lyrics = available_sites[chosen_site](artist, title)
    if not lyrics:
        get_lyrics(artist, title, sites_attempted)
    else:
        return lyrics