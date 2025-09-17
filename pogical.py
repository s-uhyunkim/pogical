"""
    TEMP
"""
from typing import Annotated
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from sympy import pretty
from sympy.logic.boolalg import simplify_logic, to_cnf, to_dnf, to_anf, to_nnf
from sympy.printing.dot import dotprint

from grammar import expression, make_conjunctions_explicit

from pyeda.boolalg import espresso

# Boilerplate code
app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_root(request: Request):
    """Return a ``Coroutine`` of the ``index.html`` template and the ``request`` value."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/")
# Recommended to use Annotated according to the FastAPI docs
# Since the checkbox is in the <form> tag, implicit_conjunctions is processed like input_string, but instead None is a valid value
async def simplify(request: Request, input_string: Annotated[str, Form()], implicit_conjunctions: Annotated[str, Form()] = None):
    # without [0], boolean_expression would be ParseResult object
    if implicit_conjunctions is not None:
        boolean_expression = expression.parse_string(make_conjunctions_explicit(input_string))[0]
    else:
        boolean_expression = expression.parse_string(input_string)[0]
    boolean_expression_dot = dotprint(boolean_expression) # converts boolean_expression into a DOT string

    simplified = simplify_logic(boolean_expression, deep=False, force=True) # function only takes in sympy 'Boolean' input
    simplified_dot = dotprint(simplified)
    cnf_simplified = to_cnf(simplified) # to_cnf() automatically detects if an expression is already in CNF
    cnf_simplified_dot = dotprint(cnf_simplified)
    dnf_simplified = to_dnf(simplified) # to_dnf() automatically detects if an expression is already in DNF
    dnf_simplified_dot = dotprint(dnf_simplified)
    anf_simplified = to_anf(simplified)
    anf_simplified_dot = dotprint(anf_simplified)
    nnf_simplified = to_nnf(simplified)
    nnf_simplified_dot = dotprint(nnf_simplified)


    return templates.TemplateResponse("output.html", {"request": request,
                                                     "input_string": input_string,
                                                     "boolean_expression": pretty(boolean_expression),
                                                     "boolean_expression_dot": boolean_expression_dot,

                                                     "simplified": pretty(simplified),
                                                     "simplified_dot": simplified_dot,
                                                     "cnf_simplified": pretty(cnf_simplified),
                                                     "cnf_simplified_dot": cnf_simplified_dot,
                                                     "dnf_simplified": pretty(dnf_simplified),
                                                     "dnf_simplified_dot": dnf_simplified_dot,
                                                     "anf_simplified": pretty(anf_simplified),
                                                     "anf_simplified_dot": anf_simplified_dot,
                                                     "nnf_simplified": pretty(nnf_simplified),
                                                     "nnf_simplified_dot": nnf_simplified_dot
                                                     })