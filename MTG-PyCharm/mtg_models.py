import card_data_ops as cops
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error

print("Loading and splitting dataset...")
card_data = pd.read_csv(cops.datapath_prepped)

#Split into training and testing.
train, test = train_test_split(card_data, test_size=0.05, random_state=42)
train_data = train.drop([cops.attr_label], axis=1)
train_labels = train[cops.attr_label]
test_data = test.drop([cops.attr_label], axis=1)
test_labels = test[cops.attr_label]

#Scale the dataset.
print("Scaling dataset...")
scaler = StandardScaler()
scaler.fit(train_data[cops.attr_to_scale])

train_data[cops.attr_to_scale] = scaler.transform(train_data[cops.attr_to_scale])
test_data[cops.attr_to_scale] = scaler.transform(test_data[cops.attr_to_scale])

def model_tree():
    import mtg_trees

    tree = mtg_trees.make_tree(train_data, train_labels)

    mse_tree_train = mean_squared_error(train_labels, tree.predict(train_data))
    mse_tree_test = mean_squared_error(test_labels, tree.predict(test_data))

    print("Tree MSE (train): ", mse_tree_train)
    print("Tree MSE (test): ", mse_tree_test)


def model_forest():
    import mtg_trees

    forest = mtg_trees.make_forest(train_data, train_labels)

    mse_forest_train = mean_squared_error(train_labels, forest.predict(train_data))
    mse_forest_test = mean_squared_error(test_labels, forest.predict(test_data))

    print("Forest MSE (train): ", mse_forest_train)
    print("Forest MSE (test): ", mse_forest_test)

def model_svr():
    import mtg_svr

    svr = mtg_svr.make_svr(train_data, train_labels)

    mse_svr_train = mean_squared_error(train_labels, svr.predict(train_data))
    mse_svr_test = mean_squared_error(test_labels, svr.predict(test_data))

    print("SVR MSE (train): ", mse_svr_train)
    print("SVR MSE (test): ", mse_svr_test)

def model_dnn():
    import mtg_nn

    dnn = mtg_nn.make_dnn(train_data, train_labels)

    mse_nn_train = mean_squared_error(train_labels, mtg_nn.pred_dnn(dnn, train_data))
    mse_nn_test = mean_squared_error(test_labels, mtg_nn.pred_dnn(dnn, test_data))

    print("NN MSE (train): ", mse_nn_train)
    print("NN MSE (test): ", mse_nn_test)

#model_tree()
#model_forest()
model_svr()
#model_dnn()
