from flask import Flask, render_template, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import os
from shutil import make_archive
from pathlib import Path
from subprocess import run, CalledProcessError
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = "@programmingninjas"

logging.basicConfig(level=logging.DEBUG)

class SongForm(FlaskForm):
    song_link = StringField("song link", validators=[DataRequired()])
    submit = SubmitField("Submit")

song_link = None

def downloader(song_link):
    try:
        command = f'spotdl {song_link}'
        song_location = os.path.abspath(os.getcwd() + '/static/Songs')
        
        if not os.path.exists(song_location):
            os.makedirs(song_location)
        
        os.chdir(song_location)
        logging.debug(f"Running command: {command} in {song_location}")
        result = run(command, check=True, capture_output=True, text=True)
        logging.debug(f"Command output: {result.stdout}")
        logging.debug(f"Command errors: {result.stderr}")
        return 1
    except CalledProcessError as e:
        logging.error(f"Command '{command}' returned non-zero exit status {e.returncode}.")
        logging.error(f"Output: {e.output}")
        logging.error(f"Error: {e.stderr}")
        return 0
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return 0

@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico')

@app.route('/', defaults={'status': 0}, methods=['GET', 'POST'])
@app.route('/<status>', methods=['GET', 'POST'])
def song(status):
    global song_link
    form = SongForm()
    if form.validate_on_submit():
        song_link = form.song_link.data
        logging.debug(f"Form submitted with song link: {song_link}")
        for f in Path(os.path.abspath(os.getcwd() + '/static/Songs')).glob("*"):
            if f.is_file():
                f.unlink() # Deleting all previous songs before downloading new
        if os.path.isfile('all_songs.zip'):
            os.remove('all_songs.zip') # Deleting zip file of all playlist songs
        status = downloader(song_link)
        os.chdir(os.path.abspath(os.getcwd()[:len(os.getcwd()) - 13]))
    return render_template("home.html", status=status, form=form)

@app.route("/download", methods=["GET", "POST"])
def download():
    paths = [x for x in os.listdir(os.getcwd() + '/static/Songs')]
    for path in paths:
        if 'track' in song_link:
            if '.mp3' in path:
                song_path = os.path.abspath(os.getcwd() + '/static/Songs' + '/' + path)
                return send_file(song_path, as_attachment=True)
        if 'playlist' in song_link:
            make_archive('all_songs', 'zip', os.path.abspath(os.getcwd() + '/static/Songs'))
            playlist_path = os.path.abspath(os.getcwd() + '/' + 'all_songs.zip')
            return send_file(playlist_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
