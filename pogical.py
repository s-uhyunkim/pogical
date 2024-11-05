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

#poop = expression.parse_string("{~p} ∧ q ∨ r ⊕ s ↓ [a ⊙ ~b] → c → (t ↔ u) & ⊤ ↑ ⊥ | ⊥ ⊼ ⊥")[0]
poop = expression.parse_string("p ∨ q ∥ r + s ↓ t ⊽ u ⊕ v ⊻ w ↮ x ⊙ y")[0]
print(type(poop))
print(simplify_logic(poop))



@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/")
# Recommended to use Annotated according to the current FastAPI docs
async def simplify(request: Request, logic_statement_input: Annotated[str, Form()]):
    sympy_expression = expression.parse_string(logic_statement_input)[0] # W/o [0], the var would be ParseResult object
    simplification = simplify_logic(sympy_expression) # function only takes in sympy 'Boolean' input
    return templates.TemplateResponse("index.html", {"request": request, "sympy_expression": sympy_expression,
                                                     "simplification": simplification })