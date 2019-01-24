import ast

rarity_to_int = {
    'basic' : 0,
    'common' : 1,
    'uncommon' : 2,
    'rare' : 3,
    'mythic' : 4
}

int_to_rarity = {
    0 : 'basic',
    1 : 'common',
    2 : 'uncommon',
    3 : 'rare',
    4 : 'mythic'
}

def card_legality(row, key):

    legality_lookup = ast.literal_eval(row['legalities'])

    if key in legality_lookup:
        return legality_lookup[key] == 'Legal'

    return False

def card_color(row, color):

    color_list = ast.literal_eval(row['colorIdentity'])

    return color in color_list

def card_combine_types(row, key):

    type_list = ast.literal_eval(row[key])

    type_combined = ""

    for type_name in type_list:
        type_combined += type_name

    return type_combined

def set_release_year(row):

    date_str = row['releaseDate']

    if len(date_str) >= 4:
        return date_str[:4]

    return ""

def card_process_price_info(row, price_info):

    row['usd'] = price_info[row['scryfallId']]['usd']
    row['eur'] = price_info[row['scryfallId']]['eur']

    return row

def card_process_set_info(row, set_info, rarity_info):

    set_list = ast.literal_eval(row['printings'])
    year_list = []
    rarity_list = []

    set_combined = ""

    for set in set_list:

        if set not in set_info.index:
            continue

        year_list.append(int(set_info.loc[set]['releaseYear']))

        if row['uuid'] in rarity_info[set]:
            rarity_list.append(rarity_to_int[rarity_info[set][row['uuid']]])

        set_combined += set

    row['numPrintings'] = len(set_list)
    row['setCombined'] = set_combined
    row['firstPrinting'] = min(year_list) if len(year_list) > 0 else -1
    row['lastPrinting'] = max(year_list) if len(year_list) > 0 else -1
    row['rarity'] = int_to_rarity[rarity_list[0]] if len(rarity_list) > 0 else 'UNKNOWN'

    '''
    if len(rarity_list) > 0 and min(rarity_list) != max(rarity_list):
        print("Rarity mismatch on card ", row.index)
    '''

    return row
