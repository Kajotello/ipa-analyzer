import numpy as np
import pandas as pd
import railway_line_data
import matplotlib.pyplot as plt

posts_on_line = railway_line_data.get_posts_on_line('354')

def translate(x):
    if pd.notnull(x):
        return posts_on_line[x]

stations_on_line = railway_line_data.get_line_stations_name('354')
stations_on_line = np.char.replace(stations_on_line.astype('str'), 'Poznań POD', 'Poznań Główny')


df = pd.read_csv('2019_2020_354.csv', index_col=[0, 1], header=[0, 1])
df = df.astype('Int64', errors='ignore')
df = df.reindex(stations_on_line, axis=0, level=0)

my_indexes1 = (df.loc['Piła Główna', 'arrival_time'].mask(df.swaplevel().loc['departure_time'].idxmin().apply(translate) > df.swaplevel().loc['arrival_time'].idxmax().apply(translate)).dropna(how='all').unstack().index.values)
my_indexes2 = (df.loc['Piła Główna', 'arrival_time'].mask(df.swaplevel().loc['departure_time'].idxmin().apply(translate) < df.swaplevel().loc['arrival_time'].idxmax().apply(translate)).dropna(how='all').unstack().index.values)

df1 = df[my_indexes1]
df2 = df[my_indexes2]



df1 = df1.reindex(stations_on_line, axis=0, level=0)
#print(df1.loc[((slice(None)), ['arrival_time', 'departure_time']), :])
travel_times1 = df1.loc[((slice(None)), ['arrival_time', 'departure_time']), :].diff()
travel_times1 = travel_times1.apply(np.abs)
print(travel_times1)

df2.index = df2.index.set_levels(['departure_delay', 'departure_time', 'arrival_delay', 'arrival_time'], level=1)
df2 = df2.reindex(stations_on_line, axis=0, level=0)
df2 = df2.reindex(['arrival_time', 'departure_time'], axis=0, level=1)
print(df2)

#print(df2.loc[((slice(None)), ['arrival_time', 'departure_time']), :])
travel_times2 = df2.loc[((slice(None)), ['arrival_time', 'departure_time']), :].diff()
travel_times2 = travel_times2.apply(np.abs)
print(travel_times2)


travel_times = pd.concat([travel_times1, travel_times2], axis=1)
print(travel_times)

idx = pd.IndexSlice
sliced_df = travel_times.loc['Chodzież', 'departure_time']
# print(sliced_df)
sliced_df.hist()
# print(df[]['Złotniki Grzybowe'])
# print(df['87330', '2019-12-20']['Złotniki'])
# print(travel_times['87330'])
# print(sliced_df[sliced_df>180])

plt.show()
