import card_csv_ops as cops
import os
import pandas as pd
import pickle
import requests
import time

datapath = os.path.abspath(os.path.join(os.getcwd(), os.pardir, "data\\"))

#Raw data from a JSON file containing the complete list of cards.
datapath_json = os.path.abspath(os.path.join(datapath, "cards-raw-mtgjson.json"))
datapath_json_sets = os.path.abspath(os.path.join(datapath, "sets-raw-mtgjson.json"))
datapath_csv = os.path.abspath(os.path.join(datapath, "cards-raw-all.csv"))
datapath_csv_sets = os.path.abspath(os.path.join(datapath, "sets-raw-all.csv"))
datapath_csv_clean = os.path.abspath(os.path.join(datapath, "cards-processed.csv"))
datapath_csv_clean_sets = os.path.abspath(os.path.join(datapath, "sets-processed.csv"))
datapath_csv_prices = os.path.abspath(os.path.join(datapath, "cards-prices.csv"))
datapath_csv_complete = os.path.abspath(os.path.join(datapath, "cards-complete-priced.csv"))
datapath_rarity = os.path.abspath(os.path.join(datapath, "cards-rarity.pickle"))

def convert_raw_data(json_filepath, csv_filepath, column_drop=[]):
    print("Converting JSON data to CSV...")
    print("Parsing JSON...")
    with open(json_filepath, 'r', encoding='utf8') as json_file:
        json_raw = pd.read_json(json_file)

    print("Constructing dataframe...")
    json_df = pd.DataFrame(json_raw)
    json_df = json_df.T

    print("Dropping unused columns...")
    json_df = json_df.drop(column_drop, axis=1)

    print(json_df)

    print("Exporting to CSV...")
    json_df.to_csv(csv_filepath)

    print("Completed data conversion from JSON to CSV.")

def build_rarity_dict():
    print("Fetching card rarity data...")
    rarity_dict = {}

    print("Parsing JSON...")
    with open(datapath_json_sets, 'r', encoding='utf8') as json_file:
        json_raw = pd.read_json(json_file)

    print("Constructing dataframe...")
    json_df = pd.DataFrame(json_raw)
    json_df = json_df.T

    set_count = 0
    num_sets = len(json_df.index)

    print("Extracting rarity data...")
    for set_index in json_df.index:

        if set_count % 100 == 0:
            print("Processing set " + str(set_count) + " of " + str(num_sets) + "...")

        rarity_dict[set_index] = {}
        set_list = json_df.loc[set_index]['cards']

        for card in set_list:
            rarity_dict[set_index][card['uuid']] = card['rarity']

        set_count += 1

    with open(datapath_rarity, 'wb') as pickle_file:
        pickle.dump(rarity_dict, pickle_file)

def cleanup_cards_csv():
    print("Cleaning up card data...")
    print("Parsing CSV...")
    csv_df = pd.read_csv(datapath_csv, index_col=0)

    print("Fixing legality attributes...")
    csv_df = csv_df.apply(cops.card_process_legality, axis=1)

    print("Fixing color attributes...")
    csv_df = csv_df.apply(cops.card_process_color, axis=1)

    typesets = ['types', 'subtypes', 'supertypes']

    print("Fixing card types...")
    for typeset in typesets:
        combined_col_name = 'complete' + typeset[:-1]
        csv_df[combined_col_name] = csv_df.apply(cops.card_combine_types, args=(typeset,), axis=1)

    csv_df['isReserved'] = csv_df['isReserved'] == True
    csv_df['isAlternative'] = csv_df['isAlternative'] == True
    csv_df['starter'] = csv_df['starter'] == True

    print("Dropping unused attributes...")
    csv_df = csv_df.drop(['colorIdentity',
                          'colorIndicator',
                          'colors',
                          'faceConvertedManaCost',
                          'frameEffect',
                          'foreignData',
                          'hand',
                          'legalities',
                          'life',
                          'loyalty',
                          'manaCost',
                          'name',
                          'names',
                          'rulings',
                          'side',
                          'subtypes',
                          'supertypes',
                          'text',
                          'tcgplayerProductId',
                          'tcgplayerPurchaseUrl',
                          'types'], axis=1)

    print("Saving CSV...")
    csv_df.to_csv(datapath_csv_clean)

def cleanup_sets_csv():
    print("Cleaning up set data...")
    print("Parsing CSV...")
    csv_df = pd.read_csv(datapath_csv_sets, index_col=0)

    print("Fixing release year...")
    csv_df['releaseYear'] = csv_df.apply(cops.set_release_year, axis=1)

    print("Dropping unused attributes...")
    csv_df = csv_df.drop(['block',
                          'boosterV3',
                          'code',
                          'codeV3',
                          'isFoilOnly',
                          'isOnlineOnly',
                          'meta',
                          'mtgoCode',
                          'releaseDate',
                          'tcgplayerGroupId'], axis=1)

    print("Saving CSV...")
    csv_df.to_csv(datapath_csv_clean_sets)

def fetch_prices():
    print("Fetching price data from Scryfall...")
    print("Parsing CSV...")
    csv_df = pd.read_csv(datapath_csv_clean, index_col=0)
    num_cards = len(csv_df.index)

    prices_df = csv_df[['scryfallId']].copy()
    prices_df['name'] = csv_df.index
    prices_df['usd'] = pd.Series(index=prices_df.index)
    prices_df['eur'] = pd.Series(index=prices_df.index)

    usd_col = prices_df.columns.get_loc('usd')
    eur_col = prices_df.columns.get_loc('eur')

    scryfall_base = "https://api.scryfall.com/cards/"
    us_card_prices_found = 0

    for i in range(0, num_cards):

        if(i % 1000 == 0):
            print("Processing card " + str(i) + " of " + str(num_cards))

        try_counter = 0
        fetched = False

        while try_counter < 10:
            req = requests.get(scryfall_base + prices_df.iloc[i]['scryfallId'])
            fetched = req.ok

            if fetched:
                card_json = req.json()

                if 'usd' in card_json:
                    prices_df.iloc[i, usd_col] = card_json['usd']
                    us_card_prices_found += 1
                if 'eur' in card_json:
                    prices_df.iloc[i, eur_col] = card_json['eur']

                break

            try_counter += 1

        if not fetched:
            print("Seems Scryfall is down. Stopping at index " + str(i))
            break

        time.sleep(0.1)

    print("Found " + str(us_card_prices_found) + " of " + str(num_cards) + " with US pricing data.")
    print("Saving CSV...")
    prices_df.to_csv(datapath_csv_prices)

def complete_cards_csv():
    print("Completing card data...")
    print("Loading data...")
    csv_df = pd.read_csv(datapath_csv_clean, index_col=0)
    csv_df_sets = pd.read_csv(datapath_csv_clean_sets, index_col=0)
    csv_prices = pd.read_csv(datapath_csv_prices, index_col=0)

    with open(datapath_rarity, 'rb') as pickle_file:
        rarity_info = pickle.load(pickle_file)

    print("Building price lookup...")
    prices_dict = {}

    for index in csv_prices.index:
        prices_dict[csv_prices.loc[index]['scryfallId']] = {}
        prices_dict[csv_prices.loc[index]['scryfallId']]['usd'] = csv_prices.loc[index]['usd']
        prices_dict[csv_prices.loc[index]['scryfallId']]['eur'] = csv_prices.loc[index]['eur']

    print("Fixing price data...")
    csv_df = csv_df.apply(cops.card_process_price_info, args=(prices_dict,), axis=1)

    print("Fixing set data...")
    csv_df = csv_df.apply(cops.card_process_set_info, args=(csv_df_sets,rarity_info), axis=1)

    print("Excluding cards with missing rarity info...")
    csv_df = csv_df[csv_df['rarity'] != 'UNKNOWN']

    print("Saving CSV...")
    csv_df.to_csv(datapath_csv_complete)

#To read in and reformat data for cards.
#convert_raw_data(datapath_json, datapath_csv)

#To read in and reformat data for card sets.
#convert_raw_data(datapath_json_sets, datapath_csv_sets, ['cards', 'tokens'])

#To reformat data and clean columns from the raw card data.
#cleanup_cards_csv()

#To reformat data and clean columns from the raw set data.
#cleanup_sets_csv()

#To fetch pricing data for all cards from the Scryfall API.
#fetch_prices()

#To fetch and save rarity data for cards from set data.
#build_rarity_dict()

#To fill in the card data with pricing, rarity, and set data.
complete_cards_csv()