#!/bin/python3

# Need these 2 lines to resolve unspecified gtk version warning
import gi
gi.require_version('Gtk', '3.0')

from typing import Annotated
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates

# Logic parsing grammar; check out pyparsing tutorials or docs
from grammar import *

app = FastAPI()
templates = Jinja2Templates(directory="templates")



@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/")
# Recommended to use Annotated according to the current FastAPI docs
async def parse(request: Request, logic_statement_input: Annotated[str, Form()]):
    tokens = expression.parseString(logic_statement_input)
    return templates.TemplateResponse("index.html", {"request": request, "tokens": tokens})