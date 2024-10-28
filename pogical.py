#!/bin/python3

# Need these 2 lines to resolve unspecified gtk version warning
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
ParserElement.enablePackrat() # Simplifies delimiter parsing and speeds up parsing in general

bmp_printables = ppu.BasicMultilingualPlane.printables # Mention bmp_printables in docs
variable = Word(bmp_printables, excludeChars='⊤ ⊥ T F 1 0 ( ) [ ] { }')
# Must exclude above chars for tautologies, contradictions and delimiters

# ≡ and ⟚ are reserved for equivalence, not biconditional
# ≢ is reserved for non-equivalence, not exclusive disjunction
tautology = one_of("⊤ T 1")
contradiction = one_of("⊥ F 0")

negation = one_of("¬ ~ !")
conjunctions = one_of("∧ & · ↑ | ⊼") # Will be sorted in conjunction_node(tokens)
disjunctions = one_of("∨ ∥ + ↓ ⊽ ⊕ ⊻ ↮ ⊙") # Will be sorted in disjunction_node(tokens)
implication = one_of("→ ⇒ ⊃")
biconditional = one_of("↔ ⇔")

left_delimiter = one_of("( [ {").suppress()
right_delimiter = one_of(") ] }").suppress()

# Parse actions
def variable_node(tokens):
    return [Node(token) for token in tokens]

def tautology_node():
    return Node("tautology")

def contradiction_node():
    return Node("contradiction")

def negation_node():
    return Node("negation")

def conjunction_node(tokens):
    if tokens[0] == one_of("↑ | ⊼"): # I'm not sure if tokens[0] is the best workaround.
        return Node("non-conjunctive")
    return Node("conjunctive")

def disjunction_node(tokens):
    if tokens[0] == one_of("⊕ ⊻ ↮"):
        return Node("exlusive disjuncion")
    if tokens[0] == one_of("↓ ⊽"):
        return Node("inclusive non-disjuncion")
    elif tokens[0] == "⊙":
        return Node("exclusive non-disjuncion")
    return Node("inclusive disjuncion")

def implication_node():
    return Node("implication")

def biconditional_node():
    return Node("biconditional")

# expression definition
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

# test cases: ~p & q ∨ r ⊕ s ↓ a ⊙ b → t ↔ u & ⊤ ↑ (⊥ | {⊥ ⊼ [⊥]})



@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/")
# Recommended to use Annotated according to the current FastAPI docs
async def parse(request: Request, logic_statement_input: Annotated[str, Form()]):
    tokens = expression.parseString(logic_statement_input)
    return templates.TemplateResponse("index.html", {"request": request, "tokens": tokens})