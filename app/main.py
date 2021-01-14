from flask import Flask, Blueprint, jsonify, render_template, request, redirect, url_for

import os
import io
from io import BytesIO
import base64
import random
import numpy as np

from matplotlib.figure import Figure
import librosa
from librosa import display

import imageio
import cv2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/audio'

cmaps = ['Accent', 'Blues', 'BrBG', 'BuGn','BuPu','CMRmap','Dark2','GnBu', 'Greens','Greys', 
         'OrRd','Oranges','PRGn','Paired','Pastel1','Pastel2','PiYG','PuBu','PuBuGn','PuOr','PuRd',
         'Purples','RdBu','RdGy','RdPu','RdYlBu','RdYlGn','Reds','Set1','Set2','Set3','Spectral','Wistia',
         'YlGn','YlGnBu','YlOrBr','YlOrRd','afmhot','afmhot','autumn','binary','bone','brg','bwr','cividis',
         'cool','coolwarm','copper','cubehelix','flag','gist_earth','gist_gray','gist_heat','gist_ncar',
         'gist_rainbow','gist_stern','gist_yarg','gnuplot','gnuplot2','gray','hot','hsv','inferno','jet','magma',
         'nipy_spectral','ocean','pink','plasma','prism','rainbow','seismic','spring','summer','tab10','tab20',
         'tab20b','tab20c','terrain','twilight','twilight_shifted','viridis','winter']


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('home_page.html', cmaps=cmaps)


@app.route('/upload', methods=['GET','POST'])
def upload_file():
    if 'file' not in request.files:
        print('No file part')
        return redirect(request.url)
    file = request.files['file']
    filename = file.filename
    filename = filename.replace(' ', '')

    # if user does not select file, browser also
    # submit an empty part without filename
    if filename == '':
        print('No selected file')
        return redirect(request.url)
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('predict',
                                filename=filename))
    return

def get_img_from_fig(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=72, transparent=True, bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    buf.close()

    img = cv2.imdecode(img_arr, 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def visualize(path):
    # Load path into librosa format
    path = os.path.join(app.config['UPLOAD_FOLDER'], path)
    
    x, sr = librosa.load(path)
    X = librosa.stft(x)
    Xdb = librosa.amplitude_to_db(abs(X))

    onset_env = librosa.onset.onset_strength(x, sr=sr)
    tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
    print('TEMPO:', tempo)

    # Calculate frame per second    
    bps = tempo / 60
    
    # Visualize and export images
    gif_imgs = []
    for style in random.choices(cmaps, k=10):
        fig = Figure(figsize=(15, 10), frameon=False, dpi=72)
        ax = fig.subplots()
        librosa.display.specshow(Xdb, sr=sr, cmap=style, x_axis=None, y_axis=None, ax=ax)
        ax.axis('off')
        
        img_arr = get_img_from_fig(fig)
        gif_imgs.append(img_arr)

    # Make gif
    gif_file = io.BytesIO()
    imageio.mimsave(gif_file, gif_imgs, 'GIF', fps=bps)
    base64_img = 'data:image/gif;base64,{}'.format(base64.b64encode(gif_file.getvalue()).decode())

    return base64_img
    
@app.route('/predict/<filename>', methods=['GET'])
def predict(filename):
    fimg = visualize(filename)
    fname = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    return render_template('predict.html', fimg=fimg, fname=fname)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
