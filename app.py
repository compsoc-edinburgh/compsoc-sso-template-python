from flask import Flask, redirect, url_for, render_template
from flask_dance.contrib.google import make_google_blueprint, google
import json

secrets = json.load(open('instance/secret.json', 'r'))

app = Flask(__name__)
app.secret_key = 'supersekrit'
blueprint = make_google_blueprint(
    client_id=secrets['client_id'],
    client_secret=secrets['client_secret'],
    scope=['profile', 'email']
)
app.register_blueprint(blueprint, url_prefix='/login')

# magic happens here
def email_valid(email):
    if email.endswith('@comp-soc.com') or email.endswith('@hacktheburgh.com'):
        return True
    return False

@app.route('/')
def index():
    if google.authorized:
        return redirect(url_for('profile'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    # retrieve token
    token = blueprint.token["access_token"]

    # revoke permission from Google's API
    resp = google.post(
        "https://accounts.google.com/o/oauth2/revoke",
        params={"token": token},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert resp.ok, resp.text
    del blueprint.token  # Delete OAuth token from storage
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if not google.authorized:
        return redirect(url_for('google.login'))
    resp = google.get('/plus/v1/people/me')
    assert resp.ok, resp.text

    person_info = resp.json()

    print(person_info)

    return render_template('profile.html',
            profile=person_info,
            valid=email_valid(person_info['emails'][0]['value'])
    )

if __name__ == '__main__':
    app.run()
