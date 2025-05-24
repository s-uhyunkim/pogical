from sympy import *
from sympy.logic.boolalg import Xnor

# def quine_mccluskey(input_expression):
    # simplifies in terms of amount of operators
    # for expressions like "{~p} ∧ q ∨ r ⊕ s ↓ [a ⊙ ~b] → c → (t ↔ u) & ⊤ ↑ ⊥ | ⊥ ⊼ ⊥,"
    # this is to prevent the outrageous output of simplify_logic() when force=True