"""
    Provides a grammar for parsing any string containing logical expressions.
"""

import re
from pyparsing import ParserElement, infix_notation, opAssoc, Suppress, one_of, Word
from pyparsing.unicode import pyparsing_unicode
from sympy import Symbol
from sympy.logic.boolalg import true, false, Not, And, Nand, Or, Xor, Nor, Xnor, Implies, Equivalent

ParserElement.enable_packrat()  # since there are 6 levels of precedence in infix_notation()


PREFIX_NEGATION_LITERALS = "~ ! - ¬ −"
POSTFIX_NEGATION_LITERALS = "' ′ ̅"
LEFT_DELIMITER_LITERALS = "( [ {"
RIGHT_DELIMITER_LITERALS = ") ] }"

NON_ALNUM_LOOKBEHINDS = (POSTFIX_NEGATION_LITERALS + RIGHT_DELIMITER_LITERALS).replace(" ", "")
NON_ALNUM_LOOKAHEADS = (PREFIX_NEGATION_LITERALS + LEFT_DELIMITER_LITERALS).replace(" ", "")
ESCAPED_LOOKBEHINDS = re.escape(NON_ALNUM_LOOKBEHINDS)
ESCAPED_LOOKAHEADS = re.escape(NON_ALNUM_LOOKAHEADS)

IMPLICIT_CONJUNCTION = re.compile(rf"(?<=[a-zA-Z{ESCAPED_LOOKBEHINDS}])(?=[a-zA-Z{ESCAPED_LOOKAHEADS}])")

def reveal_conjunctions(input_string):  # since parsing all implicit conjunctions directly is inefficient
    """Reveal every implicit conjunction and return a new string."""
    return IMPLICIT_CONJUNCTION.sub('.', input_string)


# TODO: parse ≡ and ⟚ as equivalences
# TODO: parse ≢ as non-equivalence
BMP = pyparsing_unicode.BasicMultilingualPlane
VARIABLE = Word(BMP.identchars, BMP.identbodychars)

LEFT_DELIMITER = one_of(LEFT_DELIMITER_LITERALS).suppress()
RIGHT_DELIMITER = one_of(RIGHT_DELIMITER_LITERALS).suppress()

TAUTOLOGY = one_of("1 T ⊤")
CONTRADICTION = one_of("0 F ⊥")

# TODO: include easy-to-type strings for all operators
PREFIX_NEGATION = one_of(PREFIX_NEGATION_LITERALS)
POSTFIX_NEGATION = one_of(POSTFIX_NEGATION_LITERALS)
CONJUNCTION = one_of(". & * ∧ · ×")
NON_CONJUNCTION = one_of("| ↑ ⊼")
EXCLUSIVE_DISJUNCTION = one_of("^ ⊕ ⊻")
EXCLUSIVE_NON_DISJUNCTION = one_of("⊙")
DISJUNCTION = one_of("+ ∨ ∥")
NON_DISJUNCTION = one_of("↓ ⊽")
IMPLICATION = one_of("> → ⇒ ⊃")
NON_IMPLICATION = one_of("↛ ⇏ ⊅")
CONVERSE = one_of("< ← ⇐ ⊂")
NON_CONVERSE = one_of("↚ ⇍ ⊄")
BICONDITIONAL = one_of("↔ ⇔")
NON_BICONDITIONAL = one_of("↮ ⇎")


def make_variable(tokens):
    """Parse a token as a ``Symbol`` object and return it."""
    return Symbol(tokens[0])


def make_tautology():
    """Parse a token as ``BooleanTrue`` and return it."""
    return true


def make_contradiction():
    """Parse a token as ``BooleanFalse`` and return it."""
    return false


def make_prefix_negation(tokens):
    """Parse a token as ``Not`` with parsed arguments and return it."""
    literal = tokens[0][1]
    return Not(literal, evaluate=False) # `evaluate=False` keeps the original parsed input


def make_postfix_negation(tokens):
    """Parse a token as ``Not`` with parsed arguments and return it."""
    literal = tokens[0][0]
    for _ in tokens[0][1:]:
        literal = Not(literal, evaluate=False)
    return literal


def make_conjunction(tokens):
    """Parse three tokens as ``And`` or ``Nand`` with parsed arguments and return it."""
    # Parsing pair-wise is much more efficient and readable than parsing a chain of args
    chain = tokens[0]
    left_operand = chain[0]
    for operator, right_operand in zip(chain[1::2], chain[2::2]):  # Must iterate because tokens is a flat list
        if operator == NON_CONJUNCTION:
            left_operand = Nand(left_operand, right_operand, evaluate=False)
        else:
            left_operand = And(left_operand, right_operand, evaluate=False)
    return left_operand


def make_exclusive_disjunction(tokens):
    """Parse three tokens as ``Xor`` or ``Xnor`` with parsed arguments and return it."""
    chain = tokens[0]
    left_operand = chain[0]
    for operator, right_operand in zip(chain[1::2], chain[2::2]):
        if operator == EXCLUSIVE_NON_DISJUNCTION:
            left_operand = Xnor(left_operand, right_operand, evaluate=False)
        else:
            left_operand = Xor(left_operand, right_operand, evaluate=False)
    return left_operand


def make_inclusive_disjunction(tokens):
    """Parse three tokens as ``Or`` or ``Nor`` with parsed arguments and return it."""
    chain = tokens[0]
    left_operand = chain[0]
    for operator, right_operand in zip(chain[1::2], chain[2::2]):
        if operator == NON_DISJUNCTION:
            left_operand = Nor(left_operand, right_operand, evaluate=False)
        else:
            left_operand = Or(left_operand, right_operand, evaluate=False)
    return left_operand


def make_implication(tokens):
    """Parse three tokens as ``Implies``, non-implication, converse, or non-converse with parsed arguments and return it."""
    chain = tokens[0]
    left_operand = chain[0]
    for operator, right_operand in zip(chain[1::2], chain[2::2]):
        if operator == CONVERSE:
            left_operand = Implies(right_operand, left_operand, evaluate=False)
        elif operator == NON_IMPLICATION:
            left_operand = Not(Implies(left_operand, right_operand, evaluate=False))
        elif operator == NON_CONVERSE:
            left_operand = Not(Implies(right_operand, left_operand, evaluate=False))
        else:
            left_operand = Implies(left_operand, right_operand, evaluate=False)
    return left_operand


def make_biconditional(tokens):
    """Parse three tokens as ``Equivalence`` or non-biconditional with parsed arguments and return it."""
    chain = tokens[0]
    left_operand = chain[0]
    for operator, right_operand in zip(chain[1::2], chain[2::2]):
        if operator == NON_CONJUNCTION:
            left_operand = Not(Equivalent(left_operand, right_operand, evaluate=False))
        else:
            left_operand = Equivalent(left_operand, right_operand, evaluate=False)
    return left_operand


# MatchFirst (|) is more efficient than Or (^) since each ParserElement contains unique chars
expression = infix_notation(VARIABLE.set_parse_action(make_variable) |
                            TAUTOLOGY.set_parse_action(make_tautology) |
                            CONTRADICTION.set_parse_action(make_contradiction),
                            [  # The first two are ordered so due to left-to-right precedence
                                (PREFIX_NEGATION, 1, opAssoc.RIGHT, make_prefix_negation),
                                (POSTFIX_NEGATION, 1, opAssoc.LEFT, make_postfix_negation),
                                (CONJUNCTION | NON_CONJUNCTION, 2, opAssoc.LEFT, make_conjunction),
                                (EXCLUSIVE_DISJUNCTION | EXCLUSIVE_NON_DISJUNCTION, 2, opAssoc.LEFT, make_exclusive_disjunction),
                                (DISJUNCTION | NON_DISJUNCTION, 2, opAssoc.LEFT, make_inclusive_disjunction),
                                (IMPLICATION | NON_IMPLICATION | CONVERSE | NON_CONVERSE, 2, opAssoc.LEFT, make_implication),
                                (BICONDITIONAL | NON_BICONDITIONAL, 2, opAssoc.LEFT, make_biconditional),
                            ],
                            Suppress(LEFT_DELIMITER), Suppress(RIGHT_DELIMITER)
                        )
