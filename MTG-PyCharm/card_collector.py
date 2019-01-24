import pandas as pd
import os
import card_csv_ops as cops
import time
import requests

datapath = os.path.abspath(os.path.join(os.getcwd(), os.pardir, "data\\"))

#Raw data from a JSON file containing the complete list of cards.
datapath_json = os.path.abspath(os.path.join(datapath, "cards-raw-mtgjson.json"))
datapath_csv = os.path.abspath(os.path.join(datapath, "cards-raw-all.csv"))
datapath_csv_clean = os.path.abspath(os.path.join(datapath, "cards-processed.csv"))
datapath_csv_prices = os.path.abspath(os.path.join(datapath, "cards-prices.csv"))
datapath_csv_complete = os.path.abspath(os.path.join(datapath, "cards-complete-priced.csv"))

def convert_raw_data():
    print("Converting JSON card data to CSV...")
    print("Parsing JSON...")
    with open(datapath_json, 'r', encoding='utf8') as json:
        json_raw = pd.read_json(json)

    print("Constructing dataframe...")
    json_df = pd.DataFrame(json_raw)

    print("Transposing dataframe...")
    json_df = json_df.T
    print(json_df)

    print("Exporting to CSV...")
    json_df.to_csv(datapath_csv)

    print("Completed data conversion from JSON to CSV.")

def cleanup_csv():
    print("Cleaning up card data...")
    print("Parsing CSV...")
    csv_df = pd.read_csv(datapath_csv, index_col=0)

    legalities = ['1v1', 'brawl', 'commander', 'duel', 'frontier', 'future', 'legacy', 'modern', 'pauper', 'penny', 'standard', 'vintage']

    print("Fixing legality attributes...")
    for gametype in legalities:
        csv_df[gametype] = csv_df.apply(cops.card_legality, args=(gametype,), axis=1)

    colors = ['B', 'G', 'R', 'U', 'W']

    print("Fixing color attributes...")
    for color in colors:
        csv_df[color] = csv_df.apply(cops.card_color, args=(color,), axis=1)

    print("Dropping unused attributes...")
    csv_df = csv_df.drop(['colorIdentity',
                          'colorIndicator',
                          'colors',
                          'faceConvertedManaCost',
                          'foreignData',
                          'legalities',
                          'life',
                          'loyalty',
                          'rulings',
                          'text'], axis=1)

    print("Saving CSV...")
    csv_df.to_csv(datapath_csv_clean)

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

fetch_prices()