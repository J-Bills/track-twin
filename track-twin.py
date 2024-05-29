import requests
import re
import spotipy
import os
from bottle import route, run, request
from time import sleep
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup

SPOTIPY_CLIENT_ID ='7f05be8de1c94e12b64488a34834e8aa'
SPOTIPY_CLIENT_SECRET = '0ff23932b077457292f7a575a38a5bf9'
SPOTIPY_URI = 'http://localhost:8080'
SCOPE = "user-modify-private"
CACHE = '.spotipycache'

sp_oauth = spotipy.oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_URI,scope=SCOPE,cache_path=CACHE)

@route('/')
def index():
        
    access_token = ""

    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("Found cached token!")
        access_token = token_info['access_token']
    else:
        url = request.url
        code = sp_oauth.parse_response_code(url)
        if code != url:
            print("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']

    if access_token:
        print("Access token available! Trying to get user information...")
        sp = spotipy.Spotify(access_token)
        results = sp.current_user()
        return results

    else:
        return htmlForLoginButton()
    
def generateLink(input:str):
    url = 'https://www.youtube.com/results?search_query='
    url += input
    
    # response = requests.get(url)
    # yt_html = response.text
    # yt_soup = BeautifulSoup(yt_html, 'html.parser')
    # song_link = yt_soup.find(id='thumbnail')['href']

def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton

def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url

run(host='localhost', port=8080)


