'''
mtg_trees.py
(c) Samantha Stahlke 2019
Small utility script for setting up trees/random forests.
'''


from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor

def make_tree(train_data, train_labels, max_depth=12):

    print("Creating and fitting decision tree regressor...")
    tree = DecisionTreeRegressor(max_depth=max_depth)
    tree.fit(train_data, train_labels)

    return tree

def make_forest(train_data, train_labels, n_estimators=200, max_depth=8):

    print("Creating and fitting random forest regressor...")
    forest = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth)
    forest.fit(train_data, train_labels)

    return forest
