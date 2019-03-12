'''
card_csv_ops.py
(c) Samantha Stahlke 2019
This script contains utility functions for transforming attributes of the downloaded dataset.
'''

import ast

#Rarity encoding lookups.
rarity_to_int = {
    'common' : 1,
    'uncommon' : 2,
    'rare' : 3,
    'mythic' : 4
}

int_to_rarity = {
    1 : 'common',
    2 : 'uncommon',
    3 : 'rare',
    4 : 'mythic'
}

#Game formats for legality information.
legalities = ['1v1',
              'brawl',
              'commander',
              'duel',
              'frontier',
              'future',
              'legacy',
              'modern',
              'pauper',
              'penny',
              'standard',
              'vintage']

#Card colour codes.
colors = ['B',
          'G',
          'R',
          'U',
          'W']

#Take row entries of legalities input as lists and convert to multi-column boolean values.
def card_process_legality(row):

    legality_lookup = ast.literal_eval(row['legalities'])
    total_legal = 0

    for key in legalities:
        if key in legality_lookup and legality_lookup[key] == 'Legal':
            row[key] = True
            total_legal += 1
        else:
            row[key] = False

    row['numLegalFormats'] = total_legal

    return row

#As with legality, transform row entries of colour identity as lists and convert to multi-column booleans.
def card_process_color(row):

    color_list = ast.literal_eval(row['colorIdentity'])
    total_color = 0

    for key in colors:
        if key in color_list:
            row[key] = True
            total_color += 1
        else:
            row[key] = False

    row['numColors'] = total_color

    return row

#Take a list of card type strings and concatenate them.
def card_combine_types(row, key):

    type_list = ast.literal_eval(row[key])

    type_combined = ""

    for type_name in type_list:
        type_combined += type_name

    if not type_combined:
        type_combined = "None"

    return type_combined

#Release year can be specified as a complete date in the file, but we only want the year.
def set_release_year(row):

    date_str = row['releaseDate']

    if len(date_str) >= 4:
        return date_str[:4]

    return ""

#Simply inject price data into a row.
def card_process_price_info(row, price_info):

    row['usd'] = price_info[row['scryfallId']]['usd']
    row['eur'] = price_info[row['scryfallId']]['eur']

    return row

#Augment a row from the main cards dataset with set and rarity information.
def card_process_set_info(row, set_info, rarity_info):

    set_list = ast.literal_eval(row['printings'])
    year_list = []
    rarity_list = []

    set_combined = ""

    #Find all sets the card was included in.
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

    #Used to double-check validity of entries.
    '''
    if len(rarity_list) > 0 and min(rarity_list) != max(rarity_list):
        print("Rarity mismatch on card ", row.index)
    '''

    return row
