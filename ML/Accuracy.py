import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


data=pd.read_csv("data/clean_data.csv")

print(data.isnull().sum())


features=data.drop(["aqi"],axis=1)
target = data["aqi"]

x_train,x_test,y_train,y_test = train_test_split(features.values,target)

print(x_test)
print(y_test)

model = LinearRegression()
model.fit(x_train,y_train)

train_score = model.score(x_train,y_train)
test_score = model.score(x_test,y_test)

print("Training score is ",train_score*100)
print("Testing score is ",test_score*100)

