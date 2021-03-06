import unicodedata

# Instruction syntax:
#   Inst (reg )*
#
#   where reg is any of
#       $ip, $ra, ...
#       #N (N is 64 bit integer)

# Label syntax:
#   'label:

# Constant syntax:
# #`py-expr` is compiled into #N where N is the result of evaluating `py-expr`

def assign_kinds(text):
    # TODO: Turn this into classes with methods for transitions

    transition_to_whitespace = (lambda ch: ch in " \t\n", "whitespace")
    transition_to_register = (lambda ch: ch == "$", "register")
    transition_to_constant = (lambda ch: ch == "#", "constant")
    transition_to_pyexpr = (lambda ch: ch == "`", "py-expr")
    transition_to_label = (lambda ch: ch == "'", "labeldef")

    is_letter = lambda ch: unicodedata.category(ch)[0] == "L" or ch in "-_"
    is_number = lambda ch: unicodedata.category(ch)[0] == "N"

    transition_to_instruction = (is_letter, "instruction")

    otherwise = lambda _: True

    transition_table = {
        "cat-break": [
            transition_to_whitespace,
            transition_to_register,
            transition_to_constant,
            transition_to_pyexpr,
            transition_to_label,
            transition_to_instruction,
        ],
        "instruction": [
            (is_letter, "instruction"),
            (otherwise, "cat-break"),
        ],
        "labeldef": [
            (is_letter, "labeldef"),
            (otherwise, "cat-break"),
        ],
        "register": [
            (is_letter, "register"),
            (otherwise, "cat-break"),
        ],
        "constant": [
            (is_number, "constant"),
            (otherwise, "cat-break"),
        ],
        "py-expr": [
            (lambda x: x == '`', "py-expr-end"),
            (otherwise, "py-expr"),
        ],
        "py-expr-end": [
            (otherwise, "cat-break"),
        ],
        "whitespace": [
            transition_to_whitespace,
            (otherwise, "cat-break"),
        ],
    }

    current_category = "cat-break"
    at = 0
    result = []
    while at < len(text):
        current_ch = text[at]
        transition = None

        for case, resulting_category in transition_table[current_category]:
            if case(current_ch):
                transition = resulting_category
                break

        if transition == None:
            print("Unexpected", text[at-5:at+1], "<---")

        if transition == "cat-break":
            result.append(('', transition))
        else:
            result.append((current_ch, transition))
            at += 1

        current_category = transition

    return result

def tokenize(text):
    assigned_cats = assign_kinds(text)
    assigned_cats.append(('', 'cat-break'))

    current_group, current_category = assigned_cats[0]
    result = []
    for (ch, cat) in assigned_cats[1:]:
        if cat == current_category or current_category == None:
            current_group += ch
            current_category = cat
        else:
            result.append((current_group, current_category))
            current_group = ch
            current_category = cat

    return result

def cleanup(tokens):
    result = []
    for (token, cat) in tokens:
        if cat == "register":
            assert(token[0] == "$")
            result.append((token[1:], cat))
        if cat == "instruction":
            result.append((token, cat))
        if cat == "constant":
            assert(token[0] == "#")
            result.append((int(token), cat))
        if cat == "py-expr":
            assert(token[0] == "`")
            result.append((token[1:], cat))
        if cat == "labeldef":
            assert(token[0] == "'")
            result.append((token[1:], cat))

    return result
