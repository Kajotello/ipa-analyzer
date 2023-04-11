import json
import consts
import pandas as pd
import railway_line_data
import numpy as np
from datetime import datetime


def is_all_stations_on_route(route_data, stations_names):
    for station_name in stations_names:
        if station_name not in route_data['stations']:
            return False
    return True


def is_at_least_two_successive_stations_on_route(route_data, stations_names):
    was_last_station_on_route = False
    for route_station in route_data['stations']:
        if route_station in stations_names:
            if was_last_station_on_route:
                return True
            else:
                was_last_station_on_route = True
        else:
            was_last_station_on_route = False
    return False


def find_trains_with_all_stations(routes, stations):
    result_train_names = list()
    for route in routes:
        if is_all_stations_on_route(route, stations):
            result_train_names.append(route['train_name'])
    return result_train_names


def find_trains_with_at_least_two_successive_stations(routes, stations):
    result_train_names = list()
    for route in routes:
        if is_at_least_two_successive_stations_on_route(route, stations):
            result_train_names.append(route['train_name'])
    return result_train_names


def get_dataset(year):
    year = year % 100
    with open(f'{consts.DATASET_PATH}/ipa_{year-1}_{year}/ipa_{year-1}_{year}/api/trains') as file_handler:
        return json.load(file_handler)


def read_train_data(train_name, year):
    year = year % 100
    with open(f'{consts.DATASET_PATH}/ipa_{year-1}_{year}/ipa_{year-1}_{year}/api/train/{train_name}') as file_handler:
        return json.load(file_handler)


def get_trains_on_line(line_number, year):
    stations_on_line = railway_line_data.get_line_stations_name(line_number)
    routes = get_dataset(year)['trains']
    result_trains = find_trains_with_at_least_two_successive_stations(routes, stations_on_line)
    return [train.replace('/', '_') for train in result_trains]


def is_regional_train(train, all_lines_df):
    train_stop_stations = [station['station_name'] for station in read_train_data(train, 2020)['schedules'][0]['info']]
    train_station_data = railway_line_data.get_stations_data_by_name(train_stop_stations, all_lines_df)
    stop_points_type = train_station_data.groupby('Wyróżnik').count().to_dict(orient='dict')['Nr linii']
    if stop_points_type['ST']/sum(stop_points_type.values()) < 0.85:
        return True
    else:
        return False


stations_on_line = railway_line_data.get_line_stations_name('354')
stations_on_line = np.char.replace(stations_on_line.astype('str'), 'Poznań POD', 'Poznań Główny')
trains_on_line = get_trains_on_line('354', 2020)
train_type_list = list()
trains_data = list()
indexes = list()
for train in trains_on_line:
    for schedule in read_train_data(train, 2020)['schedules']:
        schedule = schedule['info']
        date = datetime.fromisoformat(schedule[0]['departure_time']).date()
        if train == '3802_3 MALCZEWSKI' and date == datetime(2020, 9, 22):
            continue
        if train == '87740 KOTWICA' and date == datetime(2020, 1, 19):
            continue
        train_df = pd.DataFrame(schedule)
        train_df['arrival_time'] = train_df['arrival_time'].apply(lambda x: datetime.timestamp(datetime.fromisoformat(x)) if pd.notnull(x) else x).astype('Int64')
        train_df['departure_time'] = train_df['departure_time'].apply(lambda x: datetime.timestamp(datetime.fromisoformat(x)) if pd.notnull(x) else x).astype('Int64')
        train_df['arrival_delay'] = train_df['arrival_delay'].astype('Int64')
        train_df['departure_delay'] = train_df['departure_delay'].astype('Int64')
        train_df = train_df[train_df['station_name'].isin(stations_on_line)].set_index('station_name')
        train_df = train_df.stack()
        train_df = train_df.to_frame()
        train_df.columns = [[train], [date]]
        trains_data.append(train_df)

# df = pd.DataFrame(trains_data)
df = pd.DataFrame()
for train in trains_data:

    try:
        df = pd.concat([df, train], axis=1)
    except Exception:
        print(df, train)

df.index.names = ['station_name', 'attribute']
df.columns = df.columns.rename("train", level=0)
df.columns = df.columns.rename("date", level=1)
stations_on_line = stations_on_line.tolist()
df = df.reindex(stations_on_line, axis=0, level=0)
print(df)
df.to_csv('2019_2020_354.csv')





def extract_schedule_data(schedule, result_data_series):
    for attribute in consts.ATTRIBUTES:
        schedule_data = {
            station['station_name'].replace('Wlkp.', 'Wielkopolskie')
                                   .replace(' WP2', '')
                                   .replace(' Osobowy', '')
                                   .replace('k. ', 'koło ')
                                   .replace('k/', 'koło ')
                                   .replace('Kuj.', 'Kujawski'):
            station[attribute] for station in schedule['info']}
        result_data_series[attribute][schedule['schedule_date']] = pd.Series(schedule_data)


def extract_train_data(train_name, trains_full_data):
    train_data = read_train_data(train_name)
    schedules_data_series = {attribute: dict() for attribute in consts.ATTRIBUTES}
    for schedule in train_data['schedules']:
        extract_schedule_data(schedule, schedules_data_series)
    for attribute in consts.ATTRIBUTES:
        schedules_data_series[attribute] = pd.concat(schedules_data_series[attribute], axis=1)
    trains_full_data[train_name] = schedules_data_series


def extract_all_trains_data(trains_names):
    trains_full_data = dict()
    for train_name in trains_names:
        extract_train_data(train_name, trains_full_data)
    return trains_full_data
