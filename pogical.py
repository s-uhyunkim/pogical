#!/bin/python3

# Need these 2 lines to resolve unspecified gtk version warning
import gi

gi.require_version('Gtk', '3.0')

from pyparsing import ParserElement, infix_notation, opAssoc, Suppress, one_of, Word, pyparsing_unicode as ppu
from sympy import *
from sympy.logic.boolalg import Xnor

from typing import Annotated
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates

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
conjunctions = one_of("∧ & · ↑ | ⊼") # Will be sorted in make_conjunction_node(tokens)
disjunctions = one_of("∨ ∥ + ↓ ⊽ ⊕ ⊻ ↮ ⊙") # Will be sorted in make_disjunction_node(tokens)
implication = one_of("→ ⇒ ⊃")
biconditional = one_of("↔ ⇔")

left_delimiter = one_of("( [ {").suppress()
right_delimiter = one_of(") ] }").suppress()

# Parse actions
# evaluate=False prevents Sympy from auto-simplifying expressions during parsing
def make_variable_node(tokens):
    return Symbol(tokens[0])

def make_tautology_node():
    return true

def make_contradiction_node():
    return false

def make_negation_node(tokens):
    term = tokens[0][1]
    return Not(term, evaluate=False)

def make_conjunction_node(tokens):
    left_term, right_term = tokens[0][0], tokens[0][2]
    operator = tokens[0][1] # 'operator' is a string

    if operator == one_of("↑ | ⊼"): # Comparing two strings
        return Nand(left_term, right_term, evaluate=False)
    return And(left_term, right_term, evaluate=False)

def make_disjunction_node(tokens):
    left_term, right_term = tokens[0][0], tokens[0][2]
    operator = tokens[0][1]

    if operator == one_of("⊕ ⊻ ↮"):
        return Xor(left_term, right_term, evaluate=False)
    elif operator == one_of("↓ ⊽"):
        return Nor(left_term, right_term, evaluate=False)
    elif operator == "⊙":
        return Xnor(left_term, right_term, evaluate=False)
    return Or(left_term, right_term, evaluate=False)

def make_implication_node(tokens):
    left_term, right_term = tokens[0][0], tokens[0][2]
    return Implies(left_term, right_term, evaluate=False)

def make_biconditional_node(tokens):
    left_term, right_term = tokens[0][0], tokens[0][2]
    return Equivalent(left_term, right_term, evaluate=False)

# expression definition
expression = infix_notation(variable.set_parse_action(make_variable_node) |
                            tautology.set_parse_action(make_tautology_node) |
                            contradiction.set_parse_action(make_contradiction_node),
    [ # All operators must be right-associative for recursive parsing to work!
        (negation, 1, opAssoc.RIGHT, make_negation_node),
        (conjunctions, 2, opAssoc.RIGHT, make_conjunction_node),
        (disjunctions, 2, opAssoc.RIGHT, make_disjunction_node),
        (implication, 2, opAssoc.RIGHT, make_implication_node),
        (biconditional, 2, opAssoc.RIGHT, make_biconditional_node),
    ],
    Suppress(left_delimiter), Suppress(right_delimiter)
    )

# test cases:
# ~p ∧ q ∨ r ⊕ s ↓ a ⊙ ~b → c → t ↔ u & ⊤ ↑ (⊥ | {⊥ ⊼ [⊥]})
# p & q ∧ r & s
# t ↑ r | q ⊼ p
# r → q ⇒ p ⊃ o
# ~¬¬¬¬!!~p
# p ↔ a ⇔ b
# p ∨ q ∥ r + s ↓ t ⊽ u ⊕ v ⊻ w ↮ x ⊙ y



@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/")
# Recommended to use Annotated according to the current FastAPI docs
async def parse(request: Request, logic_statement_input: Annotated[str, Form()]):
    tokens = expression.parseString(logic_statement_input)
    return templates.TemplateResponse("index.html", {"request": request, "tokens": tokens})