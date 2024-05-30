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
        access_token = token_info['access_token']
    
    if access_token:
        usr_input = input('Input a song and artist name!\n')
        yt_link = generateLink(usr_input)
        related_songs_dict, source_song = getRelatedTracks(yt_link=yt_link)
        createPlaylist(access_token, related_songs_dict, source_song)
    
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
    
    driver.implicitly_wait(5)
    source = driver.find_element(By.XPATH, value='/html/body/div[1]/main/div/section[1]/div/span')
    origin_song = source.text
    songs_list = driver.find_elements(By.CSS_SELECTOR, '#track-list div span')
    
    
    related_songs_dict = dict()
    for indx, song in enumerate(songs_list):
        song_info= song.text.split(' - ')
        related_songs_dict[str(indx)] = {'artist':song_info[0], 'track':song_info[1]}
    
    driver.quit()
    return related_songs_dict, origin_song
    
    #Use Selenium to paste the track link in the submission box
    #Scrape the tracks from the resulting webpage

def createPlaylist(access_token, related_songs_dict, source_song):
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

#things= {'0': {'artist': 'Resoe', 'track': "Dubcuttin'"}, '1': {'artist': 'Nuage', 'track': 'Pay Your Love'}, '2': {'artist': 'Xxxy', 'track': 'This Much'}, '3': {'artist': 'Photay', 'track': 'Aura'}, '4': {'artist': 'Sinske', 'track': 'Belgian Woods'}, '5': {'artist': 'Deborah Jordan', 'track': 'Innervision'}, '6': {'artist': 'Big Bang', 'track': 'Ping Pong'}, '7': {'artist': 'Photek', 'track': "Can't Come Down"}, '8': {'artist': 'Jazzanova', 'track': 'Konklave'}, '9': {'artist': 'Yoofee', 'track': 'Heavenly Poison'}, '10': {'artist': 'Darcey Electronics', 'track': 'Morgen'}, '11': {'artist': 'Max Frith', 'track': 'Slipstream'}, '12': {'artist': 'Soul Bossa Trio', 'track': 'Words Of Love (Reloved By Jazzanova)'}, '13': {'artist': 'Nikitch', 'track': '507 Miles High'}, '14': {'artist': 'Cvd', 'track': 'Inner Mind Jazz'}, '15': {'artist': 'K15', 'track': "Tomorrow's Promise"}, '16': {'artist': 'Minimal Orchestra', 'track': 'Beat 2'}, '17': {'artist': 'Exhibitor', 'track': 'Boring Day'}, '18': {'artist': 'Audio Lotion', 'track': 'The Diet Plan'}, '19': {'artist': 'Kevin Murning', 'track': 'Crimson Sphere'}, '20': {'artist': 'Pavel Kostiuk', 'track': 'Mikado'}, '21': {'artist': 'Lostlojic', 'track': 'So Much'}, '22': {'artist': 'K15', 'track': 'Starburst 3'}, '23': {'artist': 'SBTRKT', 'track': 'Pause For Thought'}, '24': {'artist': '30/70', 'track': 'Get To Me (Setwun Remix)'}, '25': {'artist': '4 Hero', 'track': 'We Who Are Not As Others (Jazzanova Remix)'}, '26': {'artist': 'Wei Chi', 'track': 'Sun, My Sea'}, '27': {'artist': "P'Taah", 'track': 'Staring At The Sun'}, '28': {'artist': 'Jem Gemini', 'track': 'Yrs 4evr'}, '29': {'artist': 'UNKLE', 'track': 'Nothing To Give (Rōnin Reconstruction)'}, '30': {'artist': 'Cai Bojsen-Møller', 'track': 'Swinging Machines'}, '31': {'artist': 'The Beard', 'track': 'Someday (Phuturistix Mix)'}, '32': {'artist': 'Kaidi Tatham', 'track': "Your Dreams Don't Mean A Thing"}, '33': {'artist': 'Tennyson', 'track': 'With You'}, '34': {'artist': 'Tennyson', 'track': "L'oiseau Qui Danse"}, '35': {'artist': '30/70', 'track': 'All 4 U'}, '36': {'artist': 'Paleape', 'track': 'Whiskey For One'}, '37': {'artist': 'Ogris Debris', 'track': 'G-Thong (Dorian Concept Restring)'}, '38': {'artist': 'Yelfris Valdés', 'track': 'Ancestry (K15 Remix)'}, '39': {'artist': 'Ilkae', 'track': 'Penguin Offering Peanuts'}, '40': {'artist': 'Kaidi Tatham', 'track': 'So Amazed'}}



