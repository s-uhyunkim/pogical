"""
    TEMP
"""
from typing import Annotated, Optional
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from sympy import pretty
from sympy.logic.boolalg import simplify_logic, to_cnf, to_dnf, to_anf, to_nnf
from sympy.printing.dot import dotprint
# from pyeda.boolalg import espresso

from grammar import expression, reveal_conjunctions

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_root(request: Request):
    """Return a ``Coroutine`` of the ``index.html`` template and the ``request`` value."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/")
async def simplify(request: Request, input_string: Annotated[str, Form()], implicit_conjunctions: Optional[bool] = Form(None)):
    """Return a ``Coroutine`` of the ``output.html`` template and the ``request``, ``input_string``,
    and ``implicit_conjunctions`` values."""
    # FastAPI recommends `Annotated`
    # If the HTML checkbox is unchecked, then `implicit_conjunctions` is unassigned. Thus, `None` is its default value

    if implicit_conjunctions is None:
        boolean_expression = expression.parse_string(input_string)[0]
        # Without [0], `boolean_expression` would be a ParseResult object
    else:
        boolean_expression = expression.parse_string(reveal_conjunctions(input_string))[0]
    boolean_expression_dot = dotprint(boolean_expression)

    simplified = simplify_logic(boolean_expression, deep=False, force=True)
    simplified_dot = dotprint(simplified)
    cnf_simplified = to_cnf(simplified)  # `to_cnf()` automatically detects if an expression is already in CNF
    cnf_simplified_dot = dotprint(cnf_simplified)
    dnf_simplified = to_dnf(simplified)  # Vice versa for `to_dnf()`
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
