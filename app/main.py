#!/usr/bin/env python3


from fastapi import FastAPI, Response, Request, Cookie, HTTPException, status, Depends

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette import status
import os
import sys
import urllib.parse
import requests
import configparser


def read_config_url(filepath="config.ini"):
    if not os.path.exists(filepath):
        return None

    config = configparser.ConfigParser()
    config.read(filepath)
    return config


def load_oui_file(filepath):
    data = {}

    f = open(filepath, "r")
    source = f.read().splitlines()

    # Parse it
    for l in source:
        key, value = l.split("\t")
        data[key.upper()] = value
    return data

def lookup_oui_key(data, key):
    if key.upper() not in data.keys():
        return None

    return data[key.upper()]

def lookup_oui_mac(data, mac):
    n_mac = mac
    n_mac = n_mac.replace(':', '') # Unix, Linux, BSD, Apple
    n_mac = n_mac.replace('-', '') # Windows
    n_mac = n_mac.replace('.', '') # Cisco
    n_mac = n_mac[0:6] # To OUI
    return lookup_oui_key(data, n_mac)


# MAIN
data = {}

boodschappen = []


# Load FastAPI
app = FastAPI()



app.mount("/static", StaticFiles(directory="/code/app/static"), name="static")

templates = Jinja2Templates(directory="/code/app/templates")


@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})


@app.get("/", response_class=HTMLResponse)
async def read_items(request: Request):
    return templates.TemplateResponse("index.html",
                                        {"request": request,
                                         "boodschappen": boodschappen})


@app.get("/api/oui-lookup/oui")
async def lookup_oui(key: str):
    decode_key = urllib.parse.unquote(key)
    v = lookup_oui_key(data, decode_key)
    if v is None:
        raise HTTPException(status_code=404, detail="Item not found")

    r = {}
    r['value'] = v
    return r


@app.get("/api/oui-lookup/mac")
async def lookup_mac(key: str):
    decode_key = urllib.parse.unquote(key)
    v = lookup_oui_mac(data, decode_key)
    if v is None:
        raise HTTPException(status_code=404, detail="Item not found")

    r = {}
    r['value'] = v
    return r


@app.post("/api/oui-lookup/update")
async def update_oui_file():
    print("Using settings:")
    print(config['settings']['oui_url'])
    print(config['settings']['oui_file'])

    print("Downloading...")
    response = requests.get(config['settings']['oui_url'])
    if response.status_code < 200 or response.status_code > 299:
        raise HTTPException(status_code=500, detail="Error in OUI updating.")
        print("Error: downloading.")
        return

    print("Done downloading.")

    print("Writing...")
    open(config['settings']['oui_file'], "wb").write(response.content)
    print("Done writing to disk")

    print("Reloading OUI file from disk...")
    data = load_oui_file(config['settings']['oui_file'])
    print("Done reloading in memory.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)




