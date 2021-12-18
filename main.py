import configparser

import requests
from pandas import DataFrame
from bs4 import BeautifulSoup


ITUNES_API_SEARCH_URL = 'https://itunes.apple.com/search?'


def get_album_title(artist='Jack Johnson', song_title='Hope'):
    """ Get album title by artist and song title"""
    # Normalise params
    norm_artist = artist.lower().replace(' ', '+')
    norm_song_title = song_title.lower().replace(' ', '+')

    r = requests.get(ITUNES_API_SEARCH_URL + f'term={norm_artist}+{norm_song_title}&entity=song&limit=1').json()
    album = r['results'][0]['collectionName']
    return album


def get_all_album_songs_dataframe(artist='Jack Johnson', album_title='Sleep Through the Static'):
    """ Get album songs by artist and album title"""
    # Normalise params
    norm_artist = artist.lower().replace(' ', '+')
    norm_album_title = album_title.lower().replace(' ', '+')

    r = requests.get(ITUNES_API_SEARCH_URL + f'term={norm_artist}+{norm_album_title}&entity=song').json()
    songs = [s for s in r['results'] if s['artistName'] == artist and s['collectionName'] == album_title]

    songs_dataframe = DataFrame(songs, columns=[
                       'artistId', 'collectionId', 'trackId', 'artistName', 'collectionName',
                       'trackName', 'collectionCensoredName', 'trackCensoredName', 'artistViewUrl',
                       'collectionViewUrl', 'trackViewUrl', 'previewUrl', 'collectionPrice',
                       'trackPrice', 'releaseDate', 'discCount', 'discNumber', 'trackCount',
                       'trackNumber', 'trackTimeMillis', 'country', 'currency', 'primaryGenreName'])
    return songs_dataframe


def write_songs_dataframe_to_csv(songs_df, filename):
    songs_df.to_csv(filename, sep=',', encoding='utf-8', index=False)


def download_lyrics(artist, song_title):
    url = f'https://www.azlyrics.com/lyrics/{artist.lower().replace(" ", "")}/{song_title.lower()}.html'
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    lyrics = ''
    if 'Welcome to AZLyrics!' not in soup:
        lyrics = soup.find_all("div", {"id": "", "class": ""})[0].text
    return lyrics


def main():
    config = configparser.ConfigParser()
    config.read("config.ini")

    artist = config["Parser"]["artist"]
    song_title = config["Parser"]["song_title"]

    album = get_album_title(artist, song_title)
    songs_df = get_all_album_songs_dataframe(artist, album)
    write_songs_dataframe_to_csv(songs_df, 'songs.csv')

    lyrics = download_lyrics(artist, song_title)
    with open('lyrics.txt', 'w') as f:
        f.write(lyrics)


if __name__ == '__main__':
    main()
