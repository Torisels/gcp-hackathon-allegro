# Copyright 2020 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import logging
from flask import Flask, request
from google.cloud import bigquery
import time

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__name__)

app = Flask(__name__)
moves = ['F', 'T', 'L', 'R']

from concurrent.futures import ThreadPoolExecutor

client = bigquery.Client()
executor = ThreadPoolExecutor()




@app.route("/", methods=['GET'])
def index():
    return "Llet the python beguin"


@app.route("/", methods=['POST'])
def move():
    b = request.get_json()

    href = b["_links"]["self"]["href"]
    me = b["arena"]["state"][href]
    direction = me["direction"]

    xme = me["x"]
    yme = me["y"]
    dirme = me["direction"]
    dimx = b["arena"]["dims"][0]
    dimy = b["arena"]["dims"][1]
    del b["arena"]["state"][href]

    if xme == 0 and dirme == "W":
        return "R"

    if (xme == (dimx - 1) or xme == (dimx - 2)) and dirme == "E":
        return "R"

    if yme == 0 and dirme == "N":
        return "L"

    if (xme == (dimx - 1) or xme == (dimx - 2)) and dirme == "S":
        return "L"

    distances = []

    ts = time.time()
    executor.submit(client.insert_rows_json, 'allegro-hackathon12-2018.snowball.events', [
        {
            'x': stats['x'],
            'y': stats['y'],
            'direction': stats['direction'],
            'wasHit': stats['wasHit'],
            'score': stats['score'],
            'player': player,
            'timestamp': ts,
        } for player, stats in b['arena']['state'].items()
    ])

    for url, obj in b["arena"]["state"].items():
        xen = obj["x"]
        yen = obj["y"]

        diff_x = abs(xen - xme)
        diff_y = abs(yen - yme)

        if diff_x <= 3 or diff_y <= 3:
            distances.append((diff_x + diff_y, (xen, yen)))

    if len(distances) == 0:
        return "F"

    for d, point in distances:
        x = point[0]
        y = point[1]

        if x == xme:
            if y < yme and dirme == "N":
                return "T"
            if y > yme and dirme == "S":
                return "T"

        if y == yme:
            if x < xme and dirme == "W":
                return "T"

            if x > xme and dirme == "E":
                return "T"

    # if dirme == "N":
    #     for d, point in distances:
    #         x = point[0]
    #         y = point[1]
    #
    #         if y < yme and x == xme:
    #             return "T"

    return "T"


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
