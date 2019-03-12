'''
mtg_nn.py
(c) Samantha Stahlke 2019
Small utility script for setting up DNNs.
'''

import tensorflow as tf

#Initial model creation.
def make_dnn(train_data, train_labels):

    print("Setting up DNN...")
    print("Building feature columns...")
    feature_columns = []

    for col in train_data.columns:
        feature_columns.append(tf.feature_column.numeric_column(col))

    print("Creating DNN...")
    dnn = tf.estimator.DNNRegressor(
        feature_columns=feature_columns,
        hidden_units=[64, 32, 16],
        optimizer=tf.train.AdamOptimizer(1e-3),
        activation_fn=tf.nn.elu,
        dropout=0.5,
        batch_norm=True
    )

    print("Creating input functions...")
    train_input_fn = tf.estimator.inputs.pandas_input_fn(
        x=train_data,
        y=train_labels,
        batch_size=50,
        shuffle=True
    )

    print("Training DNN...")
    dnn.train(input_fn=train_input_fn, steps=1000)

    return dnn

#Validation.
def eval_dnn(dnn, test_data, test_labels):

    test_input_fn = tf.estimator.inputs.pandas_input_fn(
        x=test_data,
        y=test_labels,
        num_epochs=1,
        shuffle=False
    )

    print("Evaluating DNN...")
    return dnn.evaluate(input_fn=test_input_fn)

#Getting raw predictions.
def pred_dnn(dnn, data):

    input_fn = tf.estimator.inputs.pandas_input_fn(
        x=data,
        y=None,
        num_epochs=1,
        shuffle=False
    )

    result = list(dnn.predict(input_fn=input_fn))
    predictions = []

    for pred in result:
        predictions.append(pred['predictions'][0])

    return predictions


