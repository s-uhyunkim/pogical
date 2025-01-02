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
async def simplify(request: Request, logic_statement_input: Annotated[str, Form()]):
    sympy_expression = expression.parse_string(logic_statement_input)[0] # W/o [0], the var would be ParseResult object
    sympy_expression_dot = dotprint(sympy_expression) # converts sympy_expression into Graphviz by DOT description
    simplification = simplify_logic(sympy_expression) # function only takes in sympy 'Boolean' input
    simplification_dot = dotprint(simplification)
    return templates.TemplateResponse("index.html", {"request": request, "sympy_expression": sympy_expression,
                                                     "sympy_expression_dot": sympy_expression_dot,
                                                     "simplification_dot": simplification_dot,
                                                     "simplification": simplification })