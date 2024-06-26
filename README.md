# track-twin

track-twin is a project that creates personalized Spotify playlists based on the similarity to a given track using machine learning. Simply input a song, and track-twin will webscrape cosine.club and create a Spotify playlist on your account containing the results!

## Exclaimer
- For use, reach out to me and I will send client_id and key, and add you to my spotify dev team so that you can give it a spin. If requests for this go up then I will make the app readily available to everyone!
- Only works well with edm genres ex: House - Dubstep - DNB
- If you want to hear some funny music I recommend trying a country or rap song

## Features

- Personalized Spotify playlists
- Input a song to get similar track recommendations
- Utilizes web scraping for track similarity

## Usage

1. Input a song
2. track-twin scrapes cosine.club for similar tracks
3. Generates a Spotify playlist with the results

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/J-Bills/track-twin.git
    ```
2. Navigate to the project directory:
    ```bash
    cd track-twin
    ```
3. Install the necessary dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Create a config.py:
    ```bash
    touch config.py
    ```
5. add client_id and client_key vars to config.py:
    ```python
    client_id = #Spotify Client id
    client_key = #Spotify Client key
    ```

## Running the Project

To run TrackMatch, use the following command:
```bash
python3 track_twin.py
