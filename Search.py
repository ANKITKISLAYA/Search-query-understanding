import json
import requests
import urllib.parse
from pandas.io.json import json_normalize
import pandas as pd
import numpy as np
import copy
from datetime import datetime


import sys
import base64
from hashlib import md5
from Crypto import Random
from Crypto.Cipher import AES


from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import pandas as pd
import json

import warnings
warnings.filterwarnings("ignore")


from flask import Flask , jsonify
from flask import render_template
from flask import url_for
from aes256 import aes256
from flask import request
from flask_cors import CORS #to remove cross origin issue

app1 = Flask(__name__)
app1.debug = True

CORS(app1)    # to remove Error:- No 'Access-Control-Allow-Origin' header is present on the requested resource

class PrefixMiddleware(object):
#class for URL sorting 
    def __init__(self, app1, prefix=''):
        self.app1 = app1
        self.prefix = prefix

    def __call__(self, environ, start_response):
        #in this line I'm doing a replace of the word flaskredirect which is my app name in IIS to ensure proper URL redirect
        if environ['PATH_INFO'].lower().replace('/flaskredirect','').startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'].lower().replace('/flaskredirect','')[len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app1(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])            
            return ["This url does not belong to the app.".encode()]

app1.wsgi_app = PrefixMiddleware(app1.wsgi_app, prefix='/foo')


@app1.route('/search')
def search():


    text = request.args['text']
    warehouseid = request.args['warehouseid']

    warehouseid = int(warehouseid)
    url = "https://uat.shopkirana.in/api/itemMaster/Getitemmasterscentral"
    resp = requests.get(url)
    json_data = resp.json()



    if(json_data["Status"] =="OK"):
        redisAesKey = datetime.today().strftime('%Y%m%d') + "1201"
        jso = aes256().decrypt(json_data["Data"],redisAesKey)
        js = json.loads(jso)
        df = json_normalize(js)
    
    
    df=df[df.WarehouseId==warehouseid]
#     df=df[['itemname', 'ItemId','WarehouseId']]
    df=df[['itemname', 'ItemId','CategoryName','SubsubcategoryName','WarehouseId']]

    p= df.groupby('itemname').max() 

    p=p.reset_index()

    df=p

   
    Row_list =[] 

    
    for index, rows in df.iterrows(): 
#         my_list =[rows.itemname, rows.ItemId,rows.CategoryName,rows.SubsubcategoryName]
        my_list =[rows.itemname, rows.ItemId]
        Row_list.append(my_list) 


    lst=Row_list

    choices = lst

#     text=input("enter the text:")
    t=process.extract(text, choices, limit=10)

    l=list()

    for j in range(len(t)):
        if (t[j][1]>50):
            a=(t[j][0])
            l.append(a)

    item=list()
    if len(l)>=1:
        for i in l:
            a=(i[1])
            item.append(a)
            
    t = json.dumps(item) 
    return t



if __name__ == '__main__':
    app1.run(host='0.0.0.0',port=9010)
