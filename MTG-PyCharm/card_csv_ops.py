import ast

def card_legality(row, key):

    legality_lookup = ast.literal_eval(row['legalities'])

    if key in legality_lookup:
        return legality_lookup[key] == 'Legal'

    return False

def card_color(row, color):

    color_list = ast.literal_eval(row['colorIdentity'])

    return color in color_list
