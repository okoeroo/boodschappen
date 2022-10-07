#!/usr/bin/env python3


from fastapi import FastAPI, Response, Request, Cookie, HTTPException, status, Depends, Form

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette import status
import os
import sys
import urllib.parse
import requests
import configparser




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


@app.post("/boodschappen")
async def boodschappen(barcode: str = Form(),
                       boodschappen_direct: str = Form()):
    print(barcode, boodschappen_direct)

#
#        # Generate a session, returns a session key to validate per call
#    session_key = authnz.generate_session_key(authlevel)
#
#    # Set the session key
#    response.set_cookie(key="sessionkey",  value=session_key)
#
#
#    print(



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




