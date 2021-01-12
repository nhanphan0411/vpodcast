#!/usr/bin/env python3
from flask import Flask, Blueprint, jsonify, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

import os
import glob
import io
from io import BytesIO
import imageio
import shutil
import cv2

import random
import numpy as np
from matplotlib.figure import Figure
import librosa
from librosa import display

from PIL import Image


app = Flask(__name__)

cmaps = ['Accent', 'Blues', 'BrBG', 'BuGn','BuPu','CMRmap','Dark2','GnBu', 'Greens','Greys', 'OrRd','Oranges','PRGn','Paired','Pastel1','Pastel2','PiYG','PuBu','PuBuGn','PuOr','PuRd','Purples','RdBu','RdGy','RdPu','RdYlBu','RdYlGn','Reds','Set1','Set2','Set3','Spectral','Wistia','YlGn','YlGnBu','YlOrBr','YlOrRd','afmhot','afmhot','autumn','binary','bone','brg','bwr','cividis','cool','coolwarm','copper','cubehelix','flag','gist_earth','gist_gray','gist_heat','gist_ncar','gist_rainbow','gist_stern','gist_yarg','gnuplot','gnuplot2','gray','hot','hsv','inferno','jet','magma','nipy_spectral','ocean','pink','plasma','prism','rainbow','seismic','spring','summer','tab10','tab20','tab20b','tab20c','terrain','twilight','twilight_shifted','viridis','winter']

app.config['UPLOAD_FOLDER'] = os.getcwd() + '/static/audio/'
app.config['OUTPUT_FOLDER'] = os.getcwd() + '/static/output/'
app.config['TEMP_FOLDER'] = os.path.join(app.config['OUTPUT_FOLDER'], 'temp')


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
    print('SHAPE', img_arr.shape)

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
    bps = (tempo / 60)*2

    # Reset output folder
    shutil.rmtree(app.config['TEMP_FOLDER'], ignore_errors=True)
    os.mkdir(app.config['TEMP_FOLDER'])
    
    # Visualize and export images
    gif_imgs = []
    for style in random.choices(cmaps, k=10):
        fig = Figure(figsize=(15, 10), frameon=False, dpi=72)
        ax = fig.subplots()
        librosa.display.specshow(Xdb, sr=sr, cmap=style, x_axis=None, y_axis=None, ax=ax)
        ax.axis('off')
        
        img_arr = get_img_from_fig(fig)
        gif_imgs.append(img_arr)

    # Create GIF
    audio_name = path.split('.')[0].split('/')[-1]
    f_out = os.path.join(app.config['TEMP_FOLDER'], f'{audio_name}.gif')
    imageio.mimsave(f_out, gif_imgs, fps=bps)


    # # Creating gif
    # f_out = os.path.join(app.config['TEMP_FOLDER'], f'{audio_name}.gif')
    # img, *imgs = [Image.open(f) for f in gif_imgs]
    # img.save(fp=f_out, format='GIF', append_images=imgs, save_all=True, duration=1000, loop=0)

@app.route('/predict/<filename>', methods=['GET'])
def predict(filename):
    visualize(filename)

    fname = filename.split('.')[0]
    fimg = os.path.join('/static/output/temp', fname + '.gif')
    fname = os.path.join('/static/audio', filename)

    return render_template('predict.html', fimg=fimg, fname=fname)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
