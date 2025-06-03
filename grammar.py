from pyparsing import ParserElement, infix_notation, opAssoc, Suppress, one_of, Word, pyparsing_unicode as ppu
from sympy import *
from sympy.logic.boolalg import Xnor, Boolean

ParserElement.enablePackrat() # Simplifies delimiter parsing and speeds up parsing in general

bmp_printables = ppu.BasicMultilingualPlane.printables # Mention bmp_printables in docs
variable = Word(bmp_printables, excludeChars="1 0 T F ⊤ ⊥ ' ′ ̅ ( ) [ ] { }")
# Must exclude above chars for tautologies, contradictions, and delimiters lest they get treated as variables!

# ≡ and ⟚ are reserved for equivalence, not biconditional TODO: parse!
# ≢ is reserved for non-equivalence, not exclusive disjunction TODO: parse!
tautology = one_of("1 T ⊤")
contradiction = one_of("0 F ⊥")

prefix_negation = one_of("~ ! - ¬ −")
postfix_negation = one_of("' ′ ̅")
conjunction = one_of("& * ∧ · ×")
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

def make_postfix_negation(tokens): # TODO: p'' currently parses as p'
    atom = tokens[0][0]
    return Not(atom, evaluate=False)

# Dispatch parse actions like make_conjunction parse left to right *by pairs*
# I think parsing all AND and NAND chains at once, by sorting them and then combining them,
# is much less efficient and readable
def make_conjunction(tokens):
    chain = tokens[0]

    if len(chain) == 3: # Base case where it's just an operator and two literals
        left_operand, operator, right_operand = chain
    else:
        left_operand = chain[0]
        for i in range(1, len(chain), 2):
            operator = chain[i]
            right_operand = chain[i + 1]

            if operator == non_conjunction:
                left_operand = Nand(left_operand, right_operand, evaluate=False)
            else:
                left_operand = And(left_operand, right_operand, evaluate=False)
        return left_operand # Aids in recursive parsing from infix_notation()

    # Executed if base case is reached
    if operator == non_conjunction:
        return Nand(left_operand, right_operand, evaluate=False)
    return And(left_operand, right_operand, evaluate=False)

def make_disjunction(tokens):
    chain = tokens[0]

    if len(chain) == 3:  # Base case where it's just an operator and two literals
        left_operand, operator, right_operand = chain
    else:
        left_operand = chain[0]
        for i in range(1, len(chain), 2):
            operator = chain[i]
            right_operand = chain[i + 1]

            if operator == exclusive_disjunction:
                left_operand = Xor(left_operand, right_operand, evaluate=False)
            elif operator == non_disjunction:
                left_operand = Nor(left_operand, right_operand, evaluate=False)
            elif operator == exclusive_non_disjunction:
                left_operand = Xnor(left_operand, right_operand, evaluate=False)
            else:
                left_operand = Or(left_operand, right_operand, evaluate=False)
        return left_operand  # Aids in recursive parsing from infix_notation()

    # Executed if base case is reached
    if operator == exclusive_disjunction:
        return Xor(left_operand, right_operand, evaluate=False)
    elif operator == non_disjunction:
        return Nor(left_operand, right_operand, evaluate=False)
    elif operator == exclusive_non_disjunction:
        return Xnor(left_operand, right_operand, evaluate=False)
    return Or(left_operand, right_operand, evaluate=False)

def make_implication(tokens):
    chain = tokens[0]

    if len(chain) == 3:  # Base case where it's just an operator and two literals
        left_operand, operator, right_operand = chain
    else:
        left_operand = chain[0]
        for i in range(1, len(chain), 2):
            operator = chain[i]
            right_operand = chain[i + 1]

            if operator == converse:
                left_operand = Implies(right_operand, left_operand, evaluate=False)
            elif operator == non_implication:
                left_operand = Not(Implies(left_operand, right_operand, evaluate=False))
            elif operator == non_converse:
                left_operand = Not(Implies(right_operand, left_operand, evaluate=False))
            else:
                left_operand = Implies(left_operand, right_operand, evaluate=False)
        return left_operand  # Aids in recursive parsing from infix_notation()

    # Executed if base case is reached
    if operator == converse:
        return Implies(right_operand, left_operand, evaluate=False)
    elif operator == non_implication:
        return Not(Implies(left_operand, right_operand, evaluate=False))
    elif operator == non_converse:
        return Not(Implies(right_operand, left_operand, evaluate=False))
    return Implies(left_operand, right_operand, evaluate=False)

def make_biconditional(tokens):
    chain = tokens[0]

    if len(chain) == 3: # Base case where it's just an operator and two literals
        left_operand, operator, right_operand = chain
    else:
        left_operand = chain[0]
        for i in range(1, len(chain), 2):
            operator = chain[i]
            right_operand = chain[i + 1]

            if operator == non_conjunction:
                left_operand = Not(Equivalent(left_operand, right_operand, evaluate=False))
            else:
                left_operand = Equivalent(left_operand, right_operand, evaluate=False)
        return left_operand # Aids in recursive parsing from infix_notation()

    # Executed if base case is reached
    if operator == non_biconditional:
        return Not(Equivalent(left_operand, right_operand, evaluate=False))
    return Equivalent(left_operand, right_operand, evaluate=False)

# expression definition
expression = infix_notation(variable.set_parse_action(make_variable) |
                            tautology.set_parse_action(make_tautology) |
                            contradiction.set_parse_action(make_contradiction),
    [
        (prefix_negation, 1, opAssoc.RIGHT, make_prefix_negation),  # \ Ordered so due to left-to-right precedence
        (postfix_negation, 1, opAssoc.LEFT, make_postfix_negation), # /
        (conjunction ^ non_conjunction, 2, opAssoc.LEFT, make_conjunction), # See pyparsing docs for Or and MatchFirst
        (disjunction ^ exclusive_disjunction ^ non_disjunction ^ exclusive_non_disjunction, 2, opAssoc.LEFT, make_disjunction),
        (implication ^ converse ^ non_implication ^ non_converse, 2, opAssoc.LEFT, make_implication),
        (biconditional ^ non_biconditional, 2, opAssoc.LEFT, make_biconditional),
    ],
    Suppress(left_delimiter), Suppress(right_delimiter)
)