import os
from flask import Flask, request, redirect, render_template
import firebase_admin
from firebase_admin import credentials, firestore
import string
import random

app = Flask(__name__)

# Initialize Firebase using environment variable
cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
firebase_admin.initialize_app(cred)
db = firestore.client()

BASE62 = string.digits + string.ascii_letters

def generate_short_url(length=6):
    return ''.join(random.choices(BASE62, k=length))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        long_url = request.form['long_url']
        short_url = generate_short_url()
        db.collection('urls').add({
            'long_url': long_url,
            'short_url': short_url
        })
        return f'Short URL is: {request.host_url}{short_url}'
    return render_template('index.html')

@app.route('/<short_url>')
def redirect_to_long_url(short_url):
    urls_ref = db.collection('urls')
    query = urls_ref.where('short_url', '==', short_url).stream()
    result = None
    for doc in query:
        result = doc.to_dict()
        break
    if result:
        return redirect(result['long_url'])
    else:
        return 'URL not found', 404

if __name__ == '__main__':
    app.run(debug=True)
