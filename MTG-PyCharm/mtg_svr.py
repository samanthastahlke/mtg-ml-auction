from sklearn.svm import SVR

def make_svr(train_data, train_labels):

    print("Creating and fitting SVM regressor...")
    svr = SVR(kernel='rbf', gamma='scale', C=1000.00, max_iter=100000)
    svr.fit(train_data, train_labels)

    return svr
