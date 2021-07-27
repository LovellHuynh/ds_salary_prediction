# -*- coding: utf-8 -*-
"""
Created on Tue Jul 27 21:00:12 2021

@author: HuynhDat
"""

import requests
from data_input import data_in

URL = " http://127.0.0.1:5000/predict"
data = {'input': data_in}
headers = {"Content-Type": "application/json"}

r = requests.get(url = URL, headers = headers, json=data)

r.json()