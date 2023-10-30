import json
import pandas as pd

from multiprocessing import Process

from run import run_loop
from blockchain.utils.analyzer import CryptoAnalyzer

from flask import Flask, Response, request

app = Flask(__name__)

processes = []

# Create and start a new proccess in the loop
p = Process(target=run_loop)
p.start()

processes.append(p)


@app.route('/')
def index():
    return "BotDex API"


"""
Below those lines you can create routes | e: if you need to modify config values for your sell function, etc...
"""

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)