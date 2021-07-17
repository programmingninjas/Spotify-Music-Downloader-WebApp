from flask import Flask,render_template,send_file
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import os
from shutil import make_archive
from pathlib import Path
from subprocess import run

app = Flask(__name__)
app.config['SECRET_KEY'] = "@programmingninjas"

class Song_form(FlaskForm):
    
    song_link = StringField("song link", validators=[DataRequired()])
    submit = SubmitField("Submit")

song_link = None

def downloader(song_link):

    command = 'spotdl '+ song_link

    song_location = os.path.abspath(os.getcwd()+'/static/Songs')

    os.chdir(song_location)

    run(command)

    return 1

@app.route('/', defaults={'status':0},methods=['GET','POST'])
@app.route('/<status>',methods=['GET','POST'])
def song(status):

    global song_link
    form = Song_form()    

    if form.validate_on_submit():

        song_link = form.song_link.data

        [f.unlink() for f in Path(os.path.abspath(os.getcwd()+'/static/Songs')).glob("*") if f.is_file()] #deleting all previous songs before downloading new

        os.remove('all_songs.zip') if os.path.isfile('all_songs.zip') else None #deleting zip file of all playlist songs

        status = downloader(song_link)

        os.chdir(os.path.abspath(os.getcwd()[:len(os.getcwd())-13]))

    return render_template("home.html",status=status,form=form)

@app.route("/download", methods=["GET","POST"])
def download():

    paths = [x for x in os.listdir(os.getcwd()+'/static/Songs')]
    
    for path in paths:
        
        if 'track' in song_link:
            
            if '.mp3' in path:
                
                song_path = os.path.abspath(os.getcwd()+'/static/Songs'+'/'+path)
                return send_file(song_path, as_attachment=True)

        if 'playlist' in song_link:

            make_archive('all_songs', 'zip', os.path.abspath(os.getcwd()+'/static/Songs'))
            playlist_path = os.path.abspath(os.getcwd()+'/'+'all_songs.zip')
            return send_file(playlist_path, as_attachment=True)

if __name__ == '__main__':

    app.run()