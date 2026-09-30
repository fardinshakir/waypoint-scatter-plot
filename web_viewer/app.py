from flask import Flask, render_template, request, send_from_directory, jsonify
from flask_apscheduler import APScheduler
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

import contextily as ctx
import geopandas as gpd
from pyproj import Transformer
from matplotlib import rcParams
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import time
import pytz
from pprint import pprint
import math
import numpy as np
from maphotspot import plotter, calculate_zoom_level
load_dotenv()

app = Flask(__name__)


IMAGE_FOLDER = os.path.join(app.root_path, 'images')

systems_env = os.getenv('SYSTEMS')
years_env = os.getenv('YEARS')
if not systems_env:
    raise ValueError("SYSTEMS environment variable must be set")
if not years_env:
    raise ValueError("YEARS environment variable must be set")
systems = systems_env.split(',')
years = years_env.split(',')

scheduler = APScheduler()
scheduler.init_app(app)
@scheduler.task('interval', id='map_updater', hours=1, misfire_grace_time=900, max_instances=1)
def update_all_maps():
    for system in systems:
        try:
            plotter(system)
        except Exception as e:
            print(e)
            print(f"Cannot do {system}")
scheduler.start()

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_system = None
    image_path = None
    selected_month = None
    selected_year = None
    last_modified = None
    now = datetime.now(pytz.timezone('US/Eastern'))
    current_month = now.month
    current_year = now.year
    if request.method == 'POST':
        selected_system = request.form.get('system')
        selected_month = int(request.form.get('month'))
        selected_year = request.form.get('year')

        if selected_month:
            current_month = int(selected_month)
        if selected_year:
            current_year = int(selected_year)

        if selected_system:
            image_filename = f"{selected_system}_hotspot_{current_month}_{current_year}.png"
            image_path = os.path.join(app.static_folder, 'images', image_filename)
            image_path = os.path.normpath(image_path)
            if not os.path.exists(image_path):
                image_path = None
                last_modified = None
            else:
                last_seconds_modified = os.path.getmtime(image_path)
                last_modified = time.ctime(last_seconds_modified)
    return render_template('index.html', systems=systems, selected_system=selected_system,
                           image_path=image_path, current_month=current_month, current_year=current_year,
                           years=years, selected_month=selected_month, selected_year=selected_year, last_modified=last_modified)


@app.route('/images/<filename>')
def send_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/get-new-hotspot', methods=['POST'])
def new_hotspot(system):
    try:
        result = plotter(system)
        return jsonify ({'success': True, 'result': result})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5058'))
    app.run(host=host, port=port, debug=True)