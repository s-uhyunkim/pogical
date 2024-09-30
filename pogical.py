#!/bin/python3

from pyparsing import ParserElement, infix_notation, opAssoc, Suppress, one_of, Word, pyparsing_unicode as ppu

from typing import Annotated
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Grammar
ParserElement.enablePackrat()

bmp_alphas = ppu.BasicMultilingualPlane.alphas
variable = Word(bmp_alphas)

tautology = one_of("⊤ T")
contradiction = one_of("⊥ F")

negation = one_of("¬ ~")
conjunction = one_of("∧ &")
non_conjunction = one_of("↑ | ⊼")
inclusive_disjunction = one_of("∨ ∥")
inclusive_non_disjunction = one_of("↓ ⊽")
exclusive_disjunction = one_of("⊕ ⊻ ↮")
exclusive_non_disjunction = one_of("⊙")
implication = one_of("→ ⇒")
biconditional = one_of("↔ ⇔")

left_delimiter = one_of("( [ {").suppress()
right_delimiter = one_of(") ] }").suppress()

expression = infix_notation(variable | tautology | contradiction,
    [
        (negation, 1, opAssoc.RIGHT),
        (conjunction, 2, opAssoc.LEFT), # TODO: include the non-conjunctive
        (inclusive_disjunction, 2, opAssoc.LEFT), # TODO: include all disjunctives
        (implication, 2, opAssoc.LEFT),
        (biconditional, 2, opAssoc.LEFT),
    ],
    Suppress(left_delimiter), Suppress(right_delimiter)
)

# test: ~p & q ∨ r ⊕ s → t ↔ u



@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/")
async def parse(request: Request, logic_statement_input: Annotated[str, Form()]):
    tokens = expression.parseString(logic_statement_input)
    return templates.TemplateResponse("index.html", {"request": request, "tokens": tokens})