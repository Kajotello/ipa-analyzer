import json
import consts
import pandas as pd


def is_all_staions_on_route(route_data, stations_names):
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
        if is_all_staions_on_route(route, stations):
            result_train_names.append(route['train_name'])
    return result_train_names


def find_trains_with_at_least_two_successive_stations(routes, stations):
    result_train_names = list()
    for route in routes:
        if is_at_least_two_successive_stations_on_route(route, stations):
            result_train_names.append(route['train_name'])
    return result_train_names


def get_dataset():
    with open(f'{consts.DATASET_PATH}/trains') as file_handler:
        return json.load(file_handler)


def read_train_data(train_name):
    with open(f'{consts.DATASET_PATH}/train/{train_name}') as file_handler:
        return json.load(file_handler)


def get_trains_on_line(stations_on_line):
    routes = get_dataset()['trains']
    result_trains = find_trains_with_at_least_two_successive_stations(routes, stations_on_line)
    return [train.replace('/', '_') for train in result_trains]


def extract_schedule_data(schedule, result_data_series):
    for attribute in consts.ATTRIBUTES:

        schedule_data = {
            station['station_name'].replace('Wlkp.', 'Wielkopolskie')
                                   .replace(' WP2', '')
                                   .replace(' Osobowy', '')
                                   .replace('k. ', 'k/'):
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
