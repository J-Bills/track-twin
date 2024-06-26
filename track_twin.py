import requests
import spotipy
import chompjs
from bottle import route, run, request
from selectolax.parser import HTMLParser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import config

SPOTIPY_CLIENT_ID = config.client_id
SPOTIPY_CLIENT_SECRET = config.client_key
SPOTIPY_URI = 'http://localhost:8080/callback'
SCOPE = "user-modify-private, playlist-modify-public"
CACHE = '.spotipycache'

sp_oauth = spotipy.oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_URI,scope=SCOPE,cache_path=CACHE)

@route('/')
def index():
    access_token = ""
    token_info = sp_oauth.get_cached_token()
    if token_info:
        print("Found cached token!")
        access_token = token_info['access_token']
        usr_input = input('Input a song and artist name!\n')
        yt_link = generateLink(usr_input)
        related_songs_dict, source_song = getRelatedTracks(yt_link=yt_link)
        createPlaylist(access_token, related_songs_dict, source_song)
    else:
        return htmlForLoginButton()
    
@route('/callback')
def callback():
    url = request.url
    code = sp_oauth.parse_response_code(url)
    if code != url:
        print("Found Spotify auth code in Request URL! Trying to get valid access token...")
        token_info = sp_oauth.get_access_token(code)
        
    
    if token_info:
        access_token = token_info['access_token']
        usr_input = input('Input a song and artist name!\n')
        yt_link = generateLink(usr_input)
        related_songs_dict, source_song = getRelatedTracks(yt_link=yt_link)
        createPlaylist(access_token, related_songs_dict, source_song)
    
def generateLink(usr_input:str) -> str:
    url = 'https://www.youtube.com/results?search_query='
    url += usr_input
    print(url)
    
    response = requests.get(url)
    html = HTMLParser(response.text)
    data = html.css("script[nonce]")
    
    for script in data:
        try:
            new = chompjs.parse_js_object(script.text())
        except ValueError:
            pass
        
        #spaghetti because youtube randomly inserts ads into json
        if "responseContext" in new:
            bit = 0
            content_path = new["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"]
            content_list_size = (len(content_path))
            if content_list_size > 2:
                bit = 1
            testURL= content_path[bit]["itemSectionRenderer"]["contents"]
            vidURL = content_path[bit]["itemSectionRenderer"]["contents"][0]
            content_iter = iter(vidURL)
            next_key = next(content_iter)
            if next_key == "videoRenderer":
                finalURL = vidURL['videoRenderer']['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']
            else:
                finalURL = testURL[1]['videoRenderer']['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']
            ytURL = f"https://www.youtube.com{finalURL}"
    return ytURL

def getRelatedTracks(yt_link:str) -> dict:
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
    
    driver.implicitly_wait(9)
    source = driver.find_element(By.CSS_SELECTOR, value='main div section span')
    origin_song = source.text
    songs_list = driver.find_elements(By.CSS_SELECTOR, '#track-list div span')
    
    
    related_songs_dict = dict()
    for indx, song in enumerate(songs_list):
        song_info= song.text.split(' - ')
        related_songs_dict[str(indx)] = {'artist':song_info[0], 'track':song_info[1]}
    
    return related_songs_dict, origin_song
    
def createPlaylist(access_token:str, related_songs_dict:dict, source_song:str):
    user = spotipy.Spotify(access_token)
    user_id = user.current_user().get('id')
    track_collection_ids = list()
    for inner_dict in related_songs_dict.values():
        query_string = f"track:{inner_dict['track']} artist:{inner_dict['artist']}" 
        response = user.search(q=query_string, limit=1, offset=0, type='track', market='ES')
        try:
            track_collection_ids.append(response['tracks']['items'][0]['uri'])
        except IndexError:
            pass
    playlist = user.user_playlist_create(user_id,f"Songs like: {source_song}")
    user.playlist_add_items(playlist.get('id'), track_collection_ids)
    print("Added playlist to your spotify account!")
    
def htmlForLoginButton():
    auth_url = getSPOauthURI()
    htmlLoginButton = "<a href='" + auth_url + "'>Login to Spotify</a>"
    return htmlLoginButton

def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url

def main():
    run(host='localhost', port=8080)
    
main()