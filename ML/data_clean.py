import pandas as pd

data=pd.read_csv('data/air_quality_readings.csv')
data=data.drop(['id','aqi_category','created_at'], axis=1)
data=data[['pm1','pm25','pm10','temperature','humidity','gas_resistance','aqi']]
print(data)
df=pd.DataFrame(data)
df.to_csv('clean_data.csv')
print('success')
