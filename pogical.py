#!/bin/python3

from typing import Annotated
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
# Logic parsing grammar; see pyparsing tutorials or docs
from grammar import *
# Manual simplification; see sympy docs
from simplify import *

app = FastAPI()
templates = Jinja2Templates(directory="templates")



@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/")
# Recommended to use Annotated according to the current FastAPI docs
async def simplify(request: Request, logic_statement_string: Annotated[str, Form()]):
    try:
        sympy_expression = expression.parse_string(logic_statement_string)[0] # W/o [0], the var would be ParseResult object
    except:
        return templates.TemplateResponse("output.html", {"hasException" : True}) # toggles other block definition in output.html
    sympy_expression_dot = dotprint(sympy_expression) # converts sympy_expression into a DOT string

    manual_simplification = manual_simplify(sympy_expression)
    manual_simplification_dot = dotprint(manual_simplification)

    sympyfication = simplify_logic(sympy_expression) # function only takes in sympy 'Boolean' input
    sympyfication_dot = dotprint(sympyfication)
    return templates.TemplateResponse("output.html", {"request": request,
                                                     "logic_statement_string": logic_statement_string,
                                                     "sympy_expression": sympy_expression,
                                                     "sympy_expression_dot": sympy_expression_dot,

                                                     "sympyfication": sympyfication,
                                                     "sympyfication_dot": sympyfication_dot})