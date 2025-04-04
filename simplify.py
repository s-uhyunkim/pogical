from sympy import *
from sympy.logic.boolalg import Xnor

def manual_simplify(input_expression):
    # simplifies in terms of amount of operators
    # for expressions like "{~p} ∧ q ∨ r ⊕ s ↓ [a ⊙ ~b] → c → (t ↔ u) & ⊤ ↑ ⊥ | ⊥ ⊼ ⊥,"
    # this is to prevent the outrageous output of simplify_logic() when force=True

def equivalent_replace(p, q): # recursive call for each node higher than lowest level
    identity(p, q)

# General Laws

def identity(p, b):
    # p & T = p
    # p || F = p

def domination(p, b):
    # p || T = T
    # p & F = F

def idempotent(p, q):
    # p || p = p
    # p & p = p

def double_negation(p):
    # ~~p = p

def communication(p, q, r):
    # p || q = q || p
    # p & q = q & p

def association(p, q, r):
    # (p || q) || r = p || (q || r)
    # (p & q) & r = p & (q & r)

def distribution(p, q, r):
    # (p || q) & (p || r) = p || (q & r)
    # (p & q) || (p & r) = p & (q || r)

def de_morgans(p, q):
    # ~p || ~q = ~(p & q)
    # ~p & ~q = ~(p || q)

def nand_nor_defs(p, q):
    # ~(p & q) = p | q
    # ~(p || q) = p ~| q

def absoprtion(p, q):
    # p || (p & q) = p
    # p & (p || q) = p

def negation(p):
    # p || ~p = T
    # p & ~p = F

# Implication Laws

def cond_exchange(p, q):
    # ~p || q = p -> q
    # ~(p -> q) = p & ~q

def contraposition(p, q):
    # ~q -> ~p = p -> q

def exportation(p, q, r):
    # (p & q) -> r = p -> (q -> r)

def reverse_cond_exchange(p, q):
    # ~p -> q = p || q
    # ~(p -> ~q) = p & q

def cond_distribution(p, q, r):
    # (p -> q) & (p -> r) = p -> (q & r)
    # (p -> q) || (p -> r) = p -> (q || r)
    # (p -> r) & (q -> r) = (p || q) -> r
    # (p -> r) || (q -> r) = (p & q) -> r

# Biconditional Laws

def decomposition(p, q):
def bi_inverse(p, q):
def bi_exchange(p, q):
def single_negation(p, q):
def xor_definition(p, q):