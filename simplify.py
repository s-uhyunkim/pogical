from sympy import *
from sympy.logic.boolalg import Xnor

def manual_simplify(input_expression):

def equivalent_replace(p, q):

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
def communicative(p, q, r):
    # p || q = q || p
    # p & q = q & p
def associative(p, q, r):
    # (p || q) || r = p || (q || r)
    # (p & q) & r = p & (q & r)
def distributive(p, q, r):
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

def cond_equiv(p, q):
    # ~p || q = p -> q
    # ~(p -> q) = p & ~q
def contrapositive(p, q):
    # ~q -> ~p = p -> q
def reverse_cond_equiv(p, q):
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
def bi_equiv(p, q):
def single_negation(p, q):
def xor_definition(p, q):