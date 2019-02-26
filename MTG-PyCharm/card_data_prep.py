import os
import pandas as pd

datapath = os.path.abspath(os.path.join(os.getcwd(), os.pardir, "data\\"))
datapath_import = os.path.abspath(os.path.join(datapath, "cards-complete-priced.csv"))
datapath_explore = os.path.abspath(os.path.join(datapath, "cards-prepped-exploration.csv"))
datapath_explore_no_outliers = os.path.abspath(os.path.join(datapath, "cards-exploration-no-outliers.csv"))
datapath_prepped = os.path.abspath(os.path.join(datapath, "cards-prepped.csv"))
card_df = pd.read_csv(datapath_import)

outlier_threshold = 50

#Excluded attributes. This list will change depending on how data processing is modified.
attr_drop = ['eur',
             'setCombined',
             'power',
             'printings',
             'scryfallId',
             'toughness',
             'type',
             'completesubtype',
             'uuid']

#Drop card names.
card_df = card_df.drop(card_df.columns[0], axis=1)
card_df = card_df.drop(attr_drop, axis=1)

#Remove entries with missing data (primarily only for missing US price data -
#we don't want to try imputing these as we don't know much about the underlying
#distribution).
card_df = card_df.dropna()

print("Writing exploratory CSV...")
card_df.to_csv(datapath_explore, index=False)

#Drop extreme outliers on pricing.
num_cards_total = len(card_df.index)
card_df = card_df[card_df['usd'] < outlier_threshold]
num_outliers = num_cards_total - len(card_df.index)
print("Excluded ", num_outliers, " outliers with value over $", outlier_threshold)

print("Writing outlier-dropped CSV...")
card_df.to_csv(datapath_explore_no_outliers, index=False)

print("Fixing categorical and boolean attributes...")
#Simplify some categorical attributes where few cards have 'special' values.
card_df['layout'] = ['Special' if layout != 'normal' else 'None' for layout in card_df['layout']]
#card_df['completesupertype'] = ['Special' if supertype != 'None' else 'None' for supertype in card_df['completesupertype']]

#Convert boolean values to integer flags.
for dtype_key in card_df.dtypes.index:
    if card_df.dtypes[dtype_key] == bool:
        card_df[dtype_key] = card_df[dtype_key].astype(int)

#Convert categorical attributes to indices.
attr_cat = {'layout' : 'layout',
            'completetype' : 'type',
            'completesupertype' : 'supertype',
            'rarity' : 'rarity'}

card_df = pd.get_dummies(card_df, prefix=attr_cat)

print("Writing prepped CSV...")
card_df.to_csv(datapath_prepped, index=False)