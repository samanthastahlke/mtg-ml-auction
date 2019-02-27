import card_data_ops as cops
import os
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
test_data_unscaled = test_data.copy()
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


def model_forest(vary_parameters=False, graph=False):
    import mtg_trees

    default_estimators = 50
    default_depth = 12

    forest = mtg_trees.make_forest(train_data, train_labels,
                                   n_estimators=default_estimators,
                                   max_depth=default_depth)

    forest_train_pred = forest.predict(train_data)
    forest_test_pred = forest.predict(test_data)

    mse_forest_train = mean_squared_error(train_labels, forest_train_pred)
    mse_forest_test = mean_squared_error(test_labels, forest_test_pred)

    print("Forest MSE (train): ", mse_forest_train)
    print("Forest MSE (test): ", mse_forest_test)

    export_datapath = os.path.join(os.getcwd(), "forest-results\\")
    estimator_datapath = os.path.join(export_datapath, "vary_n_estimators.csv")
    depth_datapath = os.path.join(export_datapath, "vary_max_depth.csv")

    depths = [4, 6, 8, 10, 12, 14, 16]
    estimator_counts = [1, 2, 5, 10, 20, 50, 100, 200]

    if vary_parameters:

        num_trials = 5

        if not os.path.exists(export_datapath):
            os.mkdir(export_datapath)

        # Varying the number of estimators.
        print("Running trials to vary number of estimators...")

        df_estimator_counts = pd.DataFrame(columns=['n_estimators', 'max_depth', 'mse'])

        for count in estimator_counts:

            sum_mse = 0
            sum_mse_train = 0

            for i in range(0, num_trials):
                temp_forest = mtg_trees.make_forest(train_data, train_labels,
                                                    n_estimators=count,
                                                    max_depth=default_depth)

                sum_mse += mean_squared_error(test_labels, temp_forest.predict(test_data))
                sum_mse_train += mean_squared_error(train_labels, temp_forest.predict(train_data))

            avg_mse = sum_mse / float(num_trials)
            avg_mse_train = sum_mse_train / float(num_trials)
            df_estimator_counts = df_estimator_counts.append({'n_estimators' : count,
                                                              'max_depth' : default_depth,
                                                              'mse' : avg_mse,
                                                              'mse_train' : avg_mse_train},
                                                             ignore_index=True)

        df_estimator_counts.to_csv(estimator_datapath)
        print("Wrote estimator variances to file.")

        # Varying the maximum depth.
        print("Running trials to vary maximum tree depth...")

        df_depth = pd.DataFrame(columns=['n_estimators', 'max_depth', 'mse'])

        for depth in depths:

            sum_mse = 0
            sum_mse_train = 0

            for i in range(0, num_trials):
                temp_forest = mtg_trees.make_forest(train_data, train_labels,
                                                    n_estimators=default_estimators,
                                                    max_depth=depth)

                sum_mse += mean_squared_error(test_labels, temp_forest.predict(test_data))
                sum_mse_train += mean_squared_error(train_labels, temp_forest.predict(train_data))

            avg_mse = sum_mse / float(num_trials)
            avg_mse_train = sum_mse_train / float(num_trials)

            df_depth = df_depth.append({'n_estimators' : default_estimators,
                                        'max_depth' : depth,
                                        'mse' : avg_mse,
                                        'mse_train' : avg_mse_train},
                                       ignore_index=True)

        df_depth.to_csv(depth_datapath)
        print("Wrote depth variances to file.")

    if graph:
        import matplotlib.pyplot as plt

        print("Plotting forest model charts...")

        #Most relevant feature (for plotting predictions).
        max_feature = None
        max_importance = 0
        feature_index = 0

        for feature in train_data.columns:

            if forest.feature_importances_[feature_index] > max_importance:
                max_feature = feature
                max_importance = forest.feature_importances_[feature_index]

            feature_index += 1

        #Base performance on testing data.
        plt.Figure()
        plt.title("Base Performance of Random Forest Regressor on Test Set")
        plt.plot(test_data_unscaled[max_feature], test_labels, 'k.', markersize=10, label='Ground Truth')
        plt.plot(test_data_unscaled[max_feature], forest_test_pred, 'r.', markersize=5, label='Prediction')
        plt.xlabel("Feature with highest importance (" + max_feature + ")")
        plt.ylabel("Card Price (USD)")
        plt.legend(loc='upper right')
        plt.savefig(os.path.join(export_datapath, "base_performance.png"))
        plt.clf()

        #Varying number of estimators.
        df_estimator_counts = pd.read_csv(estimator_datapath)
        opt_estimators = df_estimator_counts.iloc[df_estimator_counts['mse'].idxmin()]

        plt.Figure()
        plt.title("Effect of Number of Estimators on Model Performance")
        plt.plot(df_estimator_counts['n_estimators'], df_estimator_counts['mse_train'], 'b', label='Training Set Error')
        plt.plot(df_estimator_counts['n_estimators'], df_estimator_counts['mse'], 'k', label='Test Set Error')
        plt.plot(opt_estimators['n_estimators'], opt_estimators['mse'], 'g.', markersize=20)
        plt.xlabel("Number of Estimators")
        plt.ylabel("Average MSE")
        plt.xscale("log")
        plt.xticks(estimator_counts, labels=estimator_counts)
        plt.legend(loc='upper right')
        plt.savefig(os.path.join(export_datapath, "n_estimators.png"))
        plt.clf()

        #Varying depth.
        df_depth = pd.read_csv(depth_datapath)
        opt_depth = df_depth.iloc[df_depth['mse'].idxmin()]

        plt.Figure()
        plt.title("Effect of Maximal Tree Depth on Model Performance")
        plt.plot(df_depth['max_depth'], df_depth['mse_train'], 'b', label='Training Set Error')
        plt.plot(df_depth['max_depth'], df_depth['mse'], 'k', label='Test Set Error')
        plt.plot(opt_depth['max_depth'], opt_depth['mse'], 'g.', markersize=20)
        plt.xlabel("Maximal Depth")
        plt.ylabel("Average MSE")
        plt.xticks(depths, labels=depths)
        plt.legend(loc='upper right')
        plt.savefig(os.path.join(export_datapath, "max_depth.png"))
        plt.clf()

        #Sample tree.
        from sklearn.tree import export_graphviz
        export_graphviz(forest.estimators_[0],
                        out_file=os.path.join(export_datapath, "sample_tree.dot"),
                        feature_names=train_data.columns.values,
                        rounded=True,
                        filled=True)

        print("Plotted forest model charts.")

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
model_forest()
model_svr()
model_dnn()
