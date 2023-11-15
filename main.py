import requests, os
from requests.auth import HTTPBasicAuth
from flask import Flask, render_template, request
#from dotenv import load_dotenv
#load_dotenv()


def get_response(year):
	################ log in API ##################
	# clientID = os.getenv("clientID")
	# clientSecret = os.getenv("clientSecret")
	clientID = os.environ["clientID"]
	clientSecret = os.environ["clientSecret"]
	
	url = "https://accounts.spotify.com/api/token"
	data = {"grant_type": "client_credentials"}
	auth = HTTPBasicAuth(clientID, clientSecret)
	response = requests.post(url, data=data, auth=auth)
	accessToken = response.json()["access_token"]
	headers = {"Authorization": f"Bearer {accessToken}"}

	############## get response ######################
	url = "https://api.spotify.com/v1/search"
	search = f"?q=year%3A{year}&genre%3Arock&type=track&limit=40"
	full_url = url + search
	response = requests.get(full_url, headers=headers)

	if response.status_code == 200:
		response = response.json()
	elif response.status_code == 401:
		print("Bad or expired token.")
	elif response.status_code == 403:
		print("Bad OAuth request.")
	elif response.status_code == 429:
		print("The app has exceeded it's rate limits.")

	return response


def get_songs(response):
	global playlist
	playlist = ""
	playlist_size = len(response['tracks']['items'])
	for n in range(playlist_size):
		artist = response['tracks']['items'][n]['album']['artists'][0]['name']
		album = response['tracks']['items'][n]['album']['name']
		music = response['tracks']['items'][n]['name']
		preview = response['tracks']['items'][n]['preview_url']
		album_page = response['tracks']['items'][n]['external_urls']['spotify']
		icon = response['tracks']['items'][n]['album']['images'][1]['url']
		playlist += f"""
  			<h4>{n+1}. {artist} - {music}</h4>
			<p>album: {album}</p>
			<img src="{icon}"><br>
			<audio controls><source src="{preview}" type="audio/mpeg"></audio><br>
   			<a href="{album_page}">Ouça direto no Spotify</a>
			<hr>		
			"""


app = Flask(__name__)


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/search', methods=['POST'])
def run_search_songs():
	year = request.form['year']
	get_songs(get_response(year))
	with open('Spotify API/templates/index.html') as f:
		page = f.read()
		page += str(playlist)
	return page
		
		
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=81, debug=True)
	
 
