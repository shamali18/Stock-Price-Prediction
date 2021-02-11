# -*- coding: utf-8 -*-
"""Proj-pred.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Z5uZFNOHzuNhk8UzBh2MRFc0GqD4cAXx
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np

#Libraries for plotting graphs
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('whitegrid')
plt.style.use("fivethirtyeight")
# %matplotlib inline

# Library for fetching stock data from Yahoo
from pandas_datareader.data import DataReader

# Library for time stamps
from datetime import datetime

# Analyzing the airlines stock
# Abbreviations used for airlines
# UAL : United Airlines Holdings, Inc.
# DAL : Delta Air Lines, Inc.
# ALK : Alaska Air Group, Inc.
# LUV : Southwest Airlines Co.
airlines = ['UAL', 'DAL', 'ALK', 'LUV']

# Setting up start date and end date for fetching each stock data
end = datetime.now()
start='2012-01-01'

#start = datetime(end.year - 1, end.month, end.day)

# Setting a for loop to get the datasets for all the four stocks.
# Setting each DataFrame name with the actual stock abbreviations.
for stock in airlines:   
    globals()[stock] = DataReader(stock, 'yahoo', start, end)

DAL

# Combining all the four stock dataframes into one, airlines_df dataframe
# We have done this to perform Exploratory Data Analysis on our datasets

airline_list = [UAL, DAL, ALK, LUV]
airline_name = ["United", "Delta", "Alaska", "Southwest"]

for airline, air_name in zip(airline_list, airline_name):
    airline["airline_name"] = air_name
    
airlines_df = pd.concat(airline_list, axis=0)

# Let's have a look at our combined dataframe. 
airlines_df

# Having a look at our dataframe
airlines_df.info()

#Checking for null values in the data
airlines_df.isnull().sum()

# Library for checking missing values
!pip install missingno

# Checking missing values in our combined airlines dataframe
import missingno as msno
msno.matrix(airlines_df)

# Plotting the historical closing price for all the four stocks.

plt.figure(figsize=(12, 8))
plt.subplots_adjust(top=1.25, bottom=1.2)

for i, airline in enumerate(airline_list, 1):
    plt.subplot(2, 2, i)
    airline['Close'].plot(color='indigo')
    plt.ylabel('Close')
    plt.xlabel(None)
    plt.title(f"{airlines[i - 1]}")

# Now let's plot the total volume of stock being traded each day
plt.figure(figsize=(12, 8))
plt.subplots_adjust(top=1.25, bottom=1.2)

for i, airline in enumerate(airline_list, 1):
    plt.subplot(2, 2, i)
    airline['Volume'].plot()
    plt.ylabel('Volume')
    plt.xlabel(None)
    plt.title(f"{airlines[i - 1]}")

# Fetch all closing prices of each stock in a new dataframe
close_df = DataReader(airlines, 'yahoo', start, end)['Close']
# View the new dataframe close_df
close_df.tail()

# Find the daily change in all the stocks
# Use the pct_change() function to find the daily percentage change
air_pct_change = close_df.pct_change()
air_pct_change.tail()

sns.pairplot(air_pct_change, 
                 kind='reg',
                 plot_kws={'line_kws':{'color':'#B51657'}, 
                           'scatter_kws': {'alpha': 0.5, 
                                           'color': '#B51657'}}, diag_kws= {'color': '#B51657'})

# Correlation plot of daily percentage change
sns.heatmap(air_pct_change.corr(), annot=True, cmap='rocket')

# Correlation plot of closing prices
sns.heatmap(close_df.corr(), annot=True, cmap='rocket')

"""<h1><strong>LSTM</h1>

<h3><strong>Predicting stock prices for UAL</h3>
"""

# Get the stock prices for United Airlines (UAL) from 01-01-2012 to today
ual_df = DataReader('UAL', data_source='yahoo', start='2012-01-01', end=datetime.now())
# View the generated dataframe
ual_df

# View the closing price history of UAL
plt.figure(figsize=(16,8))
plt.title('United Airlines Close Price History')
plt.plot(ual_df['Close'], color='navy')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)
plt.show()

# Creating a new dataframe containing the close column of the UAL stocks
data = ual_df.filter(['Close'])
# Converting the UAL dataframe closing stocks to a numpy array
ual_dataset = data.values
# Getting the number of rows to train the model
training_data_len = int(np.ceil( len(ual_dataset) * .8 ))
# Viewing the length of the DAL training dataset
training_data_len

# Scaling the data
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(ual_dataset)
# Viewing the scaled data
scaled_data

# Creating the scaled training data set for UAL
train_data = scaled_data[0:int(training_data_len), :]
# Splitting the data into x_train and y_train data sets for UAL
x_train = []
y_train = []

for i in range(60, len(train_data)):
    x_train.append(train_data[i-60:i, 0])
    y_train.append(train_data[i, 0])
    if i<= 61:
        print(x_train)
        print(y_train)
        print()
        
# Convert the x_train and y_train to numpy arrays 
x_train, y_train = np.array(x_train), np.array(y_train)

#Reshape the data
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

from keras.models import Sequential
from keras.layers import Dense, LSTM

# Buliding the LSTM model
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape= (x_train.shape[1], 1)))
model.add(LSTM(50, return_sequences= False))
model.add(Dense(25))
model.add(Dense(1))

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(x_train, y_train, batch_size=1, epochs=1)

# Creating the testing data set for UAL
test_data = scaled_data[training_data_len - 60: , :]
# Creating the data sets x_test and y_test for UAL
x_test = []
y_test = ual_dataset[training_data_len:, :]
for i in range(60, len(test_data)):
    x_test.append(test_data[i-60:i, 0])
    
# Convert the data to a numpy array
x_test = np.array(x_test)

# Reshape the data
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1 ))

# Get predicted price values from the model 
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

# Get the root mean squared error (RMSE)
rmse = np.sqrt(np.mean(((predictions - y_test) ** 2)))

# Viewing the RMSE
rmse

# Plot the data
train = data[:training_data_len]
ual_valid = data[training_data_len:]
ual_valid['Predictions'] = predictions
# Visualize the data
plt.figure(figsize=(16,8))
plt.title('LSTM Model prediction for United Airines')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)
plt.plot(train['Close'], color='navy')
plt.plot(ual_valid[['Close', 'Predictions']])
plt.legend(['Train', 'Val', 'Predictions'], loc='lower right')
plt.show()

# View the closing and predicted closing prices
ual_valid

"""<h3><strong>Predicting the stock prices for DAL</h3>"""

# Get the stock prices for Delta Airlines (DAL) from 01-01-2012 to today
dal_df = DataReader('DAL', data_source='yahoo', start='2012-01-01', end=datetime.now())
# View the generated dataframe
dal_df

# View the 
plt.figure(figsize=(16,8))
plt.title('Delta Airlines Close Price History')
plt.plot(dal_df['Close'], color='darkolivegreen')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)
plt.show()

# Creating a new dataframe containing the close column of the DAL stocks
data = dal_df.filter(['Close'])
# Converting the DAL dataframe closing stocks to a numpy array
dal_dataset = data.values
# Getting the number of rows to train the model
training_data_len = int(np.ceil( len(dal_dataset) * .8 ))
# Viewing the length of the DAL training dataset
training_data_len

# Scaling the data
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(dal_dataset)
# Viewing teh scaled data
scaled_data

# Creating the scaled training data set for DAL
train_data = scaled_data[0:int(training_data_len), :]
# Splitting the data into x_train and y_train data sets for DAL
x_train = []
y_train = []

for i in range(60, len(train_data)):
    x_train.append(train_data[i-60:i, 0])
    y_train.append(train_data[i, 0])
    if i<= 61:
        print(x_train)
        print(y_train)
        print()
        
# Convert the x_train and y_train to numpy arrays 
x_train, y_train = np.array(x_train), np.array(y_train)

#Reshape the data
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

from keras.models import Sequential
from keras.layers import Dense, LSTM

# Buliding the LSTM model
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape= (x_train.shape[1], 1)))
model.add(LSTM(50, return_sequences= False))
model.add(Dense(25))
model.add(Dense(1))

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(x_train, y_train, batch_size=1, epochs=1)

# Creating the testing data set for DAL
test_data = scaled_data[training_data_len - 60: , :]
# Creating the data sets x_test and y_test for DAL
x_test = []
y_test = dal_dataset[training_data_len:, :]
for i in range(60, len(test_data)):
    x_test.append(test_data[i-60:i, 0])
    
# Convert the data to a numpy array
x_test = np.array(x_test)

# Reshape the data
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1 ))

# Get predicted price values from the model 
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

# Get the root mean squared error (RMSE)
rmse = np.sqrt(np.mean(((predictions - y_test) ** 2)))

# Viewing the RMSE
rmse

# Plot the data
train = data[:training_data_len]
dal_valid = data[training_data_len:]
dal_valid['Predictions'] = predictions
# Visualize the data
plt.figure(figsize=(16,8))
plt.title('LSTM Model prediction for Delta Airines')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)
plt.plot(train['Close'], color='darkolivegreen')
plt.plot(dal_valid[['Close', 'Predictions']])
plt.legend(['Train', 'Val', 'Predictions'], loc='lower right')
plt.show()

# View the closing and predicted closing prices
dal_valid

"""<h3><strong>Predicting the stock prices for ALK</h3>"""

# Get the stock prices for Alaska Airlines (ALK) from 01-01-2012 to today
alk_df = DataReader('ALK', data_source='yahoo', start='2012-01-01', end=datetime.now())
# View the generated dataframe
alk_df

# View the closing price history of DAL
plt.figure(figsize=(16,8))
plt.title('Alaska Airlines Close Price History')
plt.plot(alk_df['Close'], color='darkslategray')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)
plt.show()

# Creating a new dataframe containing the close column of the ALK stocks
data = alk_df.filter(['Close'])
# Converting the ALK dataframe closing stocks to a numpy array
alk_dataset = data.values
# Getting the number of rows to train the model
training_data_len = int(np.ceil( len(alk_dataset) * .8 ))
# Viewing the length of the ALK training dataset
training_data_len

# Scaling the data
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(alk_dataset)
# Viewing teh scaled data
scaled_data

# Creating the scaled training data set for ALK
train_data = scaled_data[0:int(training_data_len), :]
# Splitting the data into x_train and y_train data sets for ALK
x_train = []
y_train = []

for i in range(60, len(train_data)):
    x_train.append(train_data[i-60:i, 0])
    y_train.append(train_data[i, 0])
    if i<= 61:
        print(x_train)
        print(y_train)
        print()
        
# Convert the x_train and y_train to numpy arrays 
x_train, y_train = np.array(x_train), np.array(y_train)

#Reshape the data
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

from keras.models import Sequential
from keras.layers import Dense, LSTM

# Buliding the LSTM model
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape= (x_train.shape[1], 1)))
model.add(LSTM(50, return_sequences= False))
model.add(Dense(25))
model.add(Dense(1))

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(x_train, y_train, batch_size=1, epochs=1)

# Creating the testing data set for ALK
test_data = scaled_data[training_data_len - 60: , :]
# Creating the data sets x_test and y_test for ALK
x_test = []
y_test = alk_dataset[training_data_len:, :]
for i in range(60, len(test_data)):
    x_test.append(test_data[i-60:i, 0])
    
# Convert the data to a numpy array
x_test = np.array(x_test)

# Reshape the data
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1 ))

# Get predicted price values from the model 
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

# Get the root mean squared error (RMSE)
rmse = np.sqrt(np.mean(((predictions - y_test) ** 2)))

# Viewing the RMSE
rmse

# Plot the data
train = data[:training_data_len]
alk_valid = data[training_data_len:]
alk_valid['Predictions'] = predictions
# Visualize the data
plt.figure(figsize=(16,8))
plt.title('LSTM Model prediction for Alaska Airines')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)
plt.plot(train['Close'], color='darkslategray')
plt.plot(alk_valid[['Close', 'Predictions']])
plt.legend(['Train', 'Val', 'Predictions'], loc='lower right')
plt.show()

# View the closing and predicted closing prices
alk_valid

"""<h3><strong>Predicting the stock prices for LUV<h3>"""

# Get the stock prices for Southwest Airlines (DAL) from 01-01-2012 to today
luv_df = DataReader('LUV', data_source='yahoo', start='2012-01-01', end=datetime.now())
# View the generated dataframe
luv_df

# View the closing price history of LUV
plt.figure(figsize=(16,8))
plt.title('Southwest Airlines Close Price History')
plt.plot(luv_df['Close'], color='darkorange')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)
plt.show()

# Creating a new dataframe containing the close column of the LUV stocks
data = luv_df.filter(['Close'])
# Converting the LUV dataframe closing stocks to a numpy array
luv_dataset = data.values
# Getting the number of rows to train the model
training_data_len = int(np.ceil( len(luv_dataset) * .8 ))
# Viewing the length of the DAL training dataset
training_data_len

# Scaling the data
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(luv_dataset)
# Viewing the scaled data
scaled_data

# Creating the scaled training data set for LUV
train_data = scaled_data[0:int(training_data_len), :]
# Splitting the data into x_train and y_train data sets for LUV
x_train = []
y_train = []

for i in range(60, len(train_data)):
    x_train.append(train_data[i-60:i, 0])
    y_train.append(train_data[i, 0])
    if i<= 61:
        print(x_train)
        print(y_train)
        print()
        
# Convert the x_train and y_train to numpy arrays 
x_train, y_train = np.array(x_train), np.array(y_train)

#Reshape the data
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

from keras.models import Sequential
from keras.layers import Dense, LSTM

# Buliding the LSTM model
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape= (x_train.shape[1], 1)))
model.add(LSTM(50, return_sequences= False))
model.add(Dense(25))
model.add(Dense(1))

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(x_train, y_train, batch_size=1, epochs=1)

# Creating the testing data set for LUV
test_data = scaled_data[training_data_len - 60: , :]
# Creating the data sets x_test and y_test for LUV
x_test = []
y_test = luv_dataset[training_data_len:, :]
for i in range(60, len(test_data)):
    x_test.append(test_data[i-60:i, 0])
    
# Convert the data to a numpy array
x_test = np.array(x_test)

# Reshape the data
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1 ))

# Get predicted price values from the model 
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

# Get the root mean squared error (RMSE)
rmse = np.sqrt(np.mean(((predictions - y_test) ** 2)))

# Viewing the RMSE
rmse

# Plot the data
train = data[:training_data_len]
luv_valid = data[training_data_len:]
luv_valid['Predictions'] = predictions
# Visualize the data
plt.figure(figsize=(16,8))
plt.title('LSTM Model prediction for Southwest Airines')
plt.xlabel('Date', fontsize=18)
plt.ylabel('Close Price USD ($)', fontsize=18)
plt.plot(train['Close'], color='darkorange')
plt.plot(dal_valid[['Close', 'Predictions']])
plt.legend(['Train', 'Val', 'Predictions'], loc='lower right')
plt.show()

# View the closing and predicted closing prices
luv_valid

