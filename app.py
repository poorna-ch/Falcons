from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session to work

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Dummy authentication (replace with real authentication logic)
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect(url_for('index'))  # Redirect to index after login
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

# Index route (requires login)
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))  # Redirect to login if not logged in
    return render_template('index.html')

# Submit route
@app.route('/submit', methods=['POST'])
def submit():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    city = request.form['city']
    country = request.form['country']
    phrase = request.form['phrase']
    target_lang = request.form['target_lang']

    # Example dummy data (you can use real APIs)
    safety_info = f"Safety info for {city}."
    emergency_info = f"Emergency contacts for {country}."
    
    # Translate using MyMemory API
    translation = ''
    if phrase:
        response = requests.get(
            'https://api.mymemory.translated.net/get',
            params={'q': phrase, 'langpair': f'en|{target_lang}'}
        )
        if response.ok:
            translation = response.json()['responseData']['translatedText']

    # Save in session
    session['safety_info'] = safety_info
    session['emergency_info'] = emergency_info
    session['translation'] = translation
    session['city'] = city  # Save city in session
    session['country'] = country  # Save country in session

    return redirect(url_for('results'))

# Results route
@app.route('/results')
def results():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template(
        'results.html',
        safety_info=session.get('safety_info'),
        emergency_info=session.get('emergency_info'),
        translation=session.get('translation'),
        city=session.get('city'),  # Pass city to the template
        country=session.get('country')  # Pass country to the template
    )

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/places')
def places():
    return render_template('places.html')

@app.route('/place_details')
def place_details():
    place = request.args.get('place', '')
    unsplash_access_key = 'YOUR_UNSPLASH_ACCESS_KEY'  # Replace with your Unsplash API key
    images = []

    if place:
        response = requests.get(
            f'https://api.unsplash.com/search/photos',
            params={'query': place, 'client_id': unsplash_access_key}
        )
        if response.ok:
            data = response.json()
            images = [result['urls']['small'] for result in data['results']]

    return render_template('place_details.html', place=place, images=images)

def get_wikipedia_summary(place):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{place}"
    try:
        response = requests.get(url)
        if response.ok:
            data = response.json()
            return data.get('extract', 'No description available.')
        else:
            return f"Error: {response.status_code} - {response.reason}"
    except Exception as e:
        return f"Error fetching data: {e}"

# Example usage
place = "Paris"
description = get_wikipedia_summary(place)
print(f"Description of {place}: {description}")

if __name__ == '__main__':
    app.run(debug=True)
