#!/bin/python3

# Need this to resolve unspecified gtk version warning
import gi
gi.require_version('Gtk', '3.0')

from pyparsing import ParserElement, infix_notation, opAssoc, Suppress, one_of, Word, pyparsing_unicode as ppu

from typing import Annotated
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates

from Node import Node

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Grammar; see pyparsing tutorials/docs
ParserElement.enablePackrat() # Simplifies delimiter parsing and speeds it up as well

# .printables would override delimiter parsing
bmp_alphas = ppu.BasicMultilingualPlane.alphas # Document allowed characters; still overrides 'T' and 'F'
variable = Word(bmp_alphas)

# ≡ and ⟚ is reserved for equivalence, not biconditional
# ≢ is reserved for non-equivalece, not exclusive disjunction
tautology = one_of("⊤ T 1")
contradiction = one_of("⊥ F 0")

negation = one_of("¬ ~ !")
conjunctions = one_of("∧ & · ↑ | ⊼") # Will be sorted in parse action
disjunctions = one_of("∨ ∥ + ↓ ⊽ ⊕ ⊻ ↮ ⊙") # Will be sorted in parse action
implication = one_of("→ ⇒ ⊃")
biconditional = one_of("↔ ⇔")

left_delimiter = one_of("( [ {").suppress()
right_delimiter = one_of(") ] }").suppress()

# Parse actions
def variable_node(tokens):
    return [Node(token) for token in tokens]

def tautology_node():
    return Node("true")

def contradiction_node():
    return Node("false")

def negation_node():
    return Node("not")

def conjunction_node():
    return Node("and")

def disjunction_node():
    return Node("or")

def implication_node():
    return Node("implies")

def biconditional_node():
    return Node("iff")

expression = infix_notation(variable.set_parse_action(variable_node) |
                            tautology.set_parse_action(tautology_node) |
                            contradiction.set_parse_action(contradiction_node),
    [
        (negation.set_parse_action(negation_node), 1, opAssoc.RIGHT),
        (conjunctions.set_parse_action(conjunction_node), 2, opAssoc.LEFT),
        (disjunctions.set_parse_action(disjunction_node), 2, opAssoc.LEFT),
        (implication.set_parse_action(implication_node), 2, opAssoc.LEFT),
        (biconditional.set_parse_action(biconditional_node), 2, opAssoc.LEFT),
    ],
    Suppress(left_delimiter), Suppress(right_delimiter)
)

# test: ~p & q ∨ r ⊕ s → t ↔ u & ⊤ & ⊥



@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/")
# Recommended to use Annotated according to the current FastAPI docs
async def parse(request: Request, logic_statement_input: Annotated[str, Form()]):
    tokens = expression.parseString(logic_statement_input)
    return templates.TemplateResponse("index.html", {"request": request, "tokens": tokens})