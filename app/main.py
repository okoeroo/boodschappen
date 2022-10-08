#!/usr/bin/env python3


from fastapi import FastAPI, Response, Request, Cookie, HTTPException, status, Depends, Form, UploadFile, File

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
import csv
from io import StringIO


# os.remove('/data/boodschappen.sqlite3')

models.Base.metadata.create_all(bind=engine)
app = FastAPI()


def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()


# MAIN
def test():
    boodschap = models.Boodschap()

    boodschap.barcode = "baaarrrrr"
    boodschap.omschrijving = 'boo'
    boodschap.prijs = 0.10
    boodschap.aantal = 1

    print(boodschap)

    db = sessionlocal()
    db.add(boodschap)
    db.commit()

##### TEST
# test()


# Load FastAPI
app = FastAPI()


app.mount("/static", StaticFiles(directory="/code/app/static"), name="static")
templates = Jinja2Templates(directory="/code/app/templates")


@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})


@app.get("/", response_class=HTMLResponse)
async def home(request: Request,
                db: Session = Depends(get_db), 
                boodschappen_direct: str | None = Cookie(default=None)):

    boodschappen_direct_add = \
        boodschappen_direct_remove = \
        boodschappen_direct_view = ""

    if boodschappen_direct is None or \
            boodschappen_direct == "add":
        boodschappen_direct_add = "checked"
    elif boodschappen_direct == "remove":
        boodschappen_direct_remove = "checked"
    elif boodschappen_direct == "view":
        boodschappen_direct_view = "checked"
    else:
        # Hacker detected
        boodschappen_direct_add = "checked"


    boodschappen = db.query(models.Boodschap).order_by(models.Boodschap.id.desc())

    # Display home
    return templates.TemplateResponse("index.html",
                                        {"request": request,
                                         "boodschappen": boodschappen,
                                         "boodschappen_direct_add": boodschappen_direct_add,
                                         "boodschappen_direct_remove": boodschappen_direct_remove,
                                         "boodschappen_direct_view": boodschappen_direct_view})



@app.post("/boodschappen", response_class=RedirectResponse, status_code=302)
async def boodschappen(response: Response, barcode: str = Form(),
                       boodschappen_direct: str = Form(),
                       db: Session = Depends(get_db)):

    # Doe lookup, wel bestaan:
    #                   is +1 bij toevoegen. Of -1 bij verwijderen.
    #             niet bestaan:
    #                   redirect naar invoer veld

    print("post data:", barcode, boodschappen_direct)

    boodschap = db.query(models.Boodschap).filter(models.Boodschap.barcode == barcode).first()
    if not boodschap:
        boodschap = models.Boodschap()
        boodschap.barcode = barcode
        boodschap.aantal = 1

        db.add(boodschap)
        db.commit()

        print("id is:", boodschap.id)
        return f"/boodschappen/edit/{boodschap.id}"

    else:
        if boodschappen_direct == "add":
            boodschap.aantal = boodschap.aantal + 1
            db.commit()
        elif boodschappen_direct == "remove":
            if boodschap.aantal != 0:
                boodschap.aantal = boodschap.aantal - 1
                db.commit()
            else:
                print("Warning: blocked going below 0")
        else:
            print("Unsupported")

    print("lookup:", boodschap)

    response.set_cookie(key="boodschappen_direct", value=boodschappen_direct)
    return "/"


@app.get("/boodschappen/edit/{id}", response_class=HTMLResponse)
async def boodschappen_edit_id(request: Request,
                                response: Response,
                                id: str,
                                db: Session = Depends(get_db)):
    boodschap = db.query(models.Boodschap).filter(models.Boodschap.id == id).first()

    if boodschap.barcode is None:
        boodschap.barcode = ""

    if boodschap.omschrijving is None:
        boodschap.omschrijving = ""

    if boodschap.prijs is None:
        boodschap.prijs = ""


    return templates.TemplateResponse("edit.html", {"request": request,
                                                       "id": boodschap.id, 
                                                       "barcode": boodschap.barcode,
                                                       "omschrijving": boodschap.omschrijving,
                                                       "prijs": boodschap.prijs})


@app.post("/boodschappen/edit", response_class=RedirectResponse, status_code=302)
async def boodschappen_edit(response: Response,
                            barcode: str = Form(),
                            omschrijving: str = Form(None),
                            prijs: str = Form(None),
                            db: Session = Depends(get_db)):

    boodschap = db.query(models.Boodschap).filter(models.Boodschap.barcode == barcode).first()
    if not boodschap:
        boodschap = models.Boodschap()
        boodschap.barcode = barcode
        boodschap.omschrijving = omschrijving
        boodschap.prijs = prijs
        boodschap.aantal = 1

        db.add(boodschap)
        db.commit()

    else:
        boodschap.barcode = barcode
        boodschap.omschrijving = omschrijving
        boodschap.prijs = prijs
        boodschap.aantal = 1

        db.commit()

    return "/"


@app.get("/boodschappen/delete/{id}", response_class=RedirectResponse, status_code=302)
async def boodschappen_edit_id(request: Request,
                                response: Response,
                                id: str,
                                db: Session = Depends(get_db)):
    boodschap = db.query(models.Boodschap).filter(models.Boodschap.id == id).first()

    db.delete(boodschap)
    db.commit()

    return "/"


@app.post("/boodschappen/upload_csv", response_class=RedirectResponse, status_code=302)
async def boodschappen_edit_id(request: Request,
                                response: Response,
                                upload_csv_file: UploadFile = File(...),
                                db: Session = Depends(get_db)):

    content_csv_file = await upload_csv_file.read()
    print(content_csv_file)

    buffer = StringIO(content_csv_file.decode('utf-8'))
    csvReader = csv.DictReader(buffer)
    for row in csvReader:  

        print("Barcode:", row['barcode'])
        boodschap = db.query(models.Boodschap).filter(models.Boodschap.barcode == row['barcode']).first()
        if not boodschap:
            boodschap = models.Boodschap()
            boodschap.barcode = row['barcode']
            boodschap.omschrijving = row['omschrijving']
#            boodschap.prijs = prijs
            boodschap.aantal = row['aantal']

            db.add(boodschap)
            db.commit()

    buffer.close()

    return "/"


