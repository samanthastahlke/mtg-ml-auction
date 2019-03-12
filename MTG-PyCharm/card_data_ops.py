'''
card_data_ops.py
(c) Samantha Stahlke 2019
Small utility script for dataset info (used for data prep and training).
'''

import os

datapath = os.path.abspath(os.path.join(os.getcwd(), os.pardir, "data\\"))
datapath_prepped = os.path.abspath(os.path.join(datapath, "cards-prepped.csv"))

attr_to_scale = ['convertedManaCost',
                 'numPrintings',
                 'firstPrinting',
                 'lastPrinting',
                 'numColors',
                 'numLegalFormats']

attr_label = 'usd'