#!/usr/bin/env python3


from fastapi import FastAPI, Response, Request, Cookie, HTTPException, status, Depends, Form

from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import models
from database import engine, sessionlocal
from sqlalchemy.orm import Session

from starlette import status
import os
import sys
import urllib.parse
import requests
import configparser


models.Base.metadata.create_all(bind=engine)
app = FastAPI()


def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()


# MAIN



# Load FastAPI
app = FastAPI()


app.mount("/static", StaticFiles(directory="/code/app/static"), name="static")
templates = Jinja2Templates(directory="/code/app/templates")


@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    boodschappen = db.query(models.Boodschap).order_by(models.Boodschap.id.desc())

    return templates.TemplateResponse("index.html",
                                        {"request": request,
                                         "boodschappen": boodschappen})


@app.post("/boodschappen", response_class=RedirectResponse, status_code=302)
async def boodschappen(response: Response, barcode: str = Form(),
                       boodschappen_direct: str = Form()):

    # Doe lookup, wel bestaan:
    #                   is +1 bij toevoegen. Of -1 bij verwijderen.
    #             niet bestaan:
    #                   redirect naar invoer veld


#async def add(request: Request, task: str = Form(...), db: Session = Depends(get_db)):
#    todo = models.Todo(task=task)
#    db.add(todo)
#    db.commit()
#    return RedirectResponse(url=app.url_path_for("home"), status
#
#
    print(barcode, boodschappen_direct)

    response.set_cookie(key="boodschappen_direct", value=boodschappen_direct)

    return "/"




#    # Generate a session, returns a session key to validate per call
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




