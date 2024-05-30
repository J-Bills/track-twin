import requests
import spotipy
import config
import chompjs
from bottle import route, run, request
from time import sleep
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
from selectolax.parser import HTMLParser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

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




def getRelatedTracks(yt_link):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('detach', True)
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.get('https://cosine.club')
    
    upload_link = driver.find_element(By.XPATH, value='/html/body/main/div/div[2]/span')
    upload_link.click()
    driver.implicitly_wait(5)
    
    uri_field = driver.find_element(By.NAME, value='uri')
    uri_field.clear()
    uri_field.send_keys(yt_link, Keys.ENTER)
    
    driver.implicitly_wait(10)
    songs_list = driver.find_elements(By.CSS_SELECTOR, '#track-list div span')
    
    related_songs_dict = dict()
    for indx, song in enumerate(songs_list):
        song_info= song.text.split(' - ')
        related_songs_dict[str(indx)] = {'artist':song_info[0], 'track':song_info[1]}
    
    driver.quit()
    return related_songs_dict
    
    #Use Selenium to paste the track link in the submission box
    #Scrape the tracks from the resulting webpage
    




def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton

def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url

#run(host='localhost', port=8080)

yt_link = generateLink('sad+robots+dont+cry')
related_songs_dict = getRelatedTracks(yt_link=yt_link)