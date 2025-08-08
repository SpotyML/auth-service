from flask import Flask, request, jsonify, redirect, session
from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timedelta
import urllib.parse

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")
AUTH_URL = os.getenv("AUTH_URL")
REDIRECT_URI = os.getenv("REDIRECT_URI")
TOKEN_URL = os.getenv("TOKEN_URL")
API_BASE_URL = os.getenv("API_BASE_URL")

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY

@app.route('/')
def index():
    return "Welcome to the Auth Spotify Service! <a href='/login'>Login with Spotify</a>"

@app.route('/login')
def login():
    scope = "user-read-private user-read-email"
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': scope,
        'response_type': 'code',
        'show_dialog': 'true'
    }
    print("CLIENT_ID:", CLIENT_ID)
    print("REDIRECT_URI:", REDIRECT_URI)
    print("params:", params)
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}" #Encoding the parameters for the URL
    print("Auth URL:", auth_url)
    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    
    if 'code' in request.args:
        request_body = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': request.args.get('code'),
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code',
            
        }

    response = requests.post(TOKEN_URL, data=request_body)
    token_info = response.json()

    session['access_token'] = token_info.get('access_token')
    session['refresh_token'] = token_info.get('refresh_token')
    session['expires_at'] = datetime.now().timestamp() + token_info.get('expires_in') #timestamp for different time zones

    return redirect('/playlists')

@app.route('/playlists')
def playlists():
    if 'access_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(f"{API_BASE_URL}/me/playlists", headers=headers)
    playlists = response.json()

    return jsonify(playlists)

@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')

    if datetime.now().timestamp() > session['expires_at']: 
        request_body = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'refresh_token': session['refresh_token'],
            'grant_type': 'refresh_token'
        }

    response = requests.post(TOKEN_URL, data=request_body)
    token_info = response.json()

    session['access_token'] = token_info.get('access_token')
    session['expires_at'] = datetime.now().timestamp() + timedelta(seconds=token_info.get('expires_in'))

    return redirect('/playlists')
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001, ssl_context=('cert.pem', 'key.pem'))  # Use your SSL certificate and key
