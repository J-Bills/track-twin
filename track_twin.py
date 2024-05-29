import requests
import spotipy
import config
import chompjs
from bottle import route, run, request
from time import sleep
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser

SPOTIPY_CLIENT_ID = config.client_id
SPOTIPY_CLIENT_SECRET = config.client_key
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
    



def generateLink(usr_input:str) -> str: 
    url = 'https://www.youtube.com/results?search_query='
    url += usr_input
    
    response = requests.get(url)
    html = HTMLParser(response.text)
    data = html.css("script[nonce]")
    
    for script in data:
        try:
            new = chompjs.parse_js_object(script.text())
        except ValueError:
            pass
        
        if "responseContext" in new:
            vidURL = new["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]['videoRenderer']['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']
            ytURL = f"https://www.youtube.com{vidURL}"
    return ytURL

yt_link = generateLink('sad+robots+dont+cry')

def getRelatedTracks(yt_link):
    #Use Selenium to paste the track link in the submission box
    #Scrape the tracks from the resulting webpage
    pass




def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton

def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url

run(host='localhost', port=8080)


