#!/bin/python3

from typing import Annotated
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
# Logic parsing grammar; see pyparsing tutorials or docs
from grammar import *
# Manual simplification; see sympy docs
# from simplify import *

app = FastAPI()
templates = Jinja2Templates(directory="templates")



@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/")
# Recommended to use Annotated according to the current FastAPI docs
async def simplify(request: Request, input_string: Annotated[str, Form()]):
    try:
        boolean_expression = expression.parse_string(input_string)[0] # W/o [0], the var would be ParseResult object
    except:
        return templates.TemplateResponse("output.html", {"hasException" : True}) # toggles other block definition in output.html
    boolean_expression_dot = dotprint(boolean_expression) # converts boolean_expression into a DOT string

    simplified = simplify_logic(boolean_expression, deep=False) # function only takes in sympy 'Boolean' input
    simplified_dot = dotprint(simplified)

    return templates.TemplateResponse("output.html", {"request": request,
                                                     "input_string": input_string,
                                                     "boolean_expression": boolean_expression,
                                                     "boolean_expression_dot": boolean_expression_dot,

                                                     "simplified": simplified,
                                                     "simplified_dot": simplified_dot})