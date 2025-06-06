from pyparsing import ParserElement, infix_notation, opAssoc, Suppress, one_of, Word, pyparsing_unicode
from sympy import Symbol
from sympy.logic.boolalg import true, false, Not, And, Nand, Or, Xor, Nor, Xnor, Implies, Equivalent

ParserElement.enablePackrat() # Simplifies delimiter parsing and speeds up parsing in general

def is_atom_start(char):
    return char.isalpha() or char == prefix_negation or char == left_delimiter
def is_atom_end(char):
    return char.isalpha() or char == postfix_negation or char == right_delimiter

def preprocess(input_string):
    input_string_list = list(input_string)
    i = 1
    while i < len(input_string_list):
        if is_atom_start(input_string_list[i]) and is_atom_end(input_string_list[i - 1]):
            input_string_list.insert(i, '.')
            i += 1  # Skip the inserted conjunction
        i += 1
    return ''.join(input_string_list)



variable = Word(pyparsing_unicode.BasicMultilingualPlane.alphas)
# ≡ and ⟚ are reserved for equivalence, not biconditional TODO: parse!
# ≢ is reserved for non-equivalence, not exclusive disjunction TODO: parse!
tautology = one_of("1 T ⊤")
contradiction = one_of("0 F ⊥")

prefix_negation = one_of("~ ! - ¬ −")
postfix_negation = one_of("' ′ ̅")
conjunction = one_of(". & * ∧ · ×")
non_conjunction = one_of("| ↑ ⊼")
disjunction = one_of("+ ∨ ∥")
exclusive_disjunction = one_of("^ ⊕ ⊻")
non_disjunction = one_of("↓ ⊽")
exclusive_non_disjunction = one_of("⊙")
implication = one_of("> → ⇒ ⊃")
converse = one_of("< ← ⇐ ⊂")
non_implication = one_of("↛ ⇏ ⊅")
non_converse = one_of("↚ ⇍ ⊄")
biconditional = one_of("↔ ⇔")
non_biconditional = one_of("↮ ⇎")

left_delimiter = one_of("( [ {").suppress()
right_delimiter = one_of(") ] }").suppress()

# Parse actions
# evaluate=False prevents Sympy from auto-simplifying expressions during parsing

def make_variable(tokens):
    return Symbol(tokens[0])

def make_tautology():
    return true

def make_contradiction():
    return false

def make_prefix_negation(tokens):
    atom = tokens[0][1]
    return Not(atom, evaluate=False)

def make_postfix_negation(tokens):
    literal = tokens[0][0] # Start with the atom, but it'll be appended recursively
    for _ in tokens[0][1:]: # Just applies Not() n times
        literal = Not(literal, evaluate=False)
    return literal

# Dispatch parse actions like make_conjunction parse left to right *by pairs*
# I think parsing all AND and NAND chains at once, by sorting them and then combining them,
# is much less efficient and readable
def make_conjunction(tokens):
    chain = tokens[0]
    left_operand = chain[0]
    for operator, right_operand in zip(chain[1::2], chain[2::2]): # Must iterate because tokens is a flat list
        if operator == non_conjunction:
            left_operand = Nand(left_operand, right_operand, evaluate=False)
        else:
            left_operand = And(left_operand, right_operand, evaluate=False)
    return left_operand

def make_disjunction(tokens):
    chain = tokens[0]
    left_operand = chain[0]
    for operator, right_operand in zip(chain[1::2], chain[2::2]):
        if operator == exclusive_disjunction:
            left_operand = Xor(left_operand, right_operand, evaluate=False)
        elif operator == non_disjunction:
            left_operand = Nor(left_operand, right_operand, evaluate=False)
        elif operator == exclusive_non_disjunction:
            left_operand = Xnor(left_operand, right_operand, evaluate=False)
        else:
            left_operand = Or(left_operand, right_operand, evaluate=False)
    return left_operand

def make_implication(tokens):
    chain = tokens[0]
    left_operand = chain[0]
    for operator, right_operand in zip(chain[1::2], chain[2::2]):
        if operator == converse:
            left_operand = Implies(right_operand, left_operand, evaluate=False)
        elif operator == non_implication:
            left_operand = Not(Implies(left_operand, right_operand, evaluate=False))
        elif operator == non_converse:
            left_operand = Not(Implies(right_operand, left_operand, evaluate=False))
        else:
            left_operand = Implies(left_operand, right_operand, evaluate=False)
    return left_operand

def make_biconditional(tokens):
    chain = tokens[0]
    left_operand = chain[0]
    for operator, right_operand in zip(chain[1::2], chain[2::2]):
        if operator == non_conjunction:
            left_operand = Not(Equivalent(left_operand, right_operand, evaluate=False))
        else:
            left_operand = Equivalent(left_operand, right_operand, evaluate=False)
    return left_operand

# expression definition
expression = infix_notation(variable.set_parse_action(make_variable) | # See pyparsing docs for Or and MatchFirst
                            tautology.set_parse_action(make_tautology) |
                            contradiction.set_parse_action(make_contradiction),
    [
        (prefix_negation, 1, opAssoc.RIGHT, make_prefix_negation),  # \ Ordered so due to left-to-right precedence
        (postfix_negation, 1, opAssoc.LEFT, make_postfix_negation), # /
        (conjunction ^ non_conjunction, 2, opAssoc.LEFT, make_conjunction),
        (disjunction ^ exclusive_disjunction ^ non_disjunction ^ exclusive_non_disjunction, 2, opAssoc.LEFT, make_disjunction),
        (implication ^ converse ^ non_implication ^ non_converse, 2, opAssoc.LEFT, make_implication),
        (biconditional ^ non_biconditional, 2, opAssoc.LEFT, make_biconditional),
    ],
    Suppress(left_delimiter), Suppress(right_delimiter)
)