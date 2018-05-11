from sklearn import preprocessing
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.externals import joblib

df = pd.read_csv('/Users/jared/Dev/Tim/data/EUR_USD_very_long.csv')
num_days = 5

temp = df.copy()

# X = df.drop(['datetime'], 1)
X = np.array(df.drop(['datetime'], 1))
# X = df[['close']]
# X = preprocessing.scale(X)

X = X[:-num_days]

y = np.array(df[['close']].shift(-num_days))
y = y[:-num_days]

test_size = int(len(y) * .1)  # 10% data for test set

X_test = X[-test_size:]
y_test = y[-test_size:]
X = X[:-test_size]
y = y[:-test_size]

valid_size = int(len(y) * .3)  # 30% data for valid set

X_valid = X[-valid_size:]
y_valid = y[-valid_size:]
X_train = X[:-valid_size]
y_train = y[:-valid_size]

clf = LinearRegression()

clf.fit(X_train, y_train.ravel())

y_pred = clf.predict(X_valid)

score = clf.score(X_valid, y_valid)
error = mean_squared_error(y_valid, y_pred)

print('Error: {0}, Score: {1}'.format(error, score))

joblib.dump(clf, 'linear_regressesor.pkl')


# Plot outputs
plt.scatter(X_valid[:, 0], y_valid,  color='black')
plt.plot(X_valid[:, 0], y_pred, color='blue', linewidth=3)

plt.xticks(())
plt.yticks(())

plt.show()
