import json
from consts import DATASET_PATH
import pandas as pd
import matplotlib.pyplot as plt
import railway_scrapper as rs
from datetime import datetime, timedelta
import math


def is_station_on_route(route_data, station_name):
    for station in route_data['stations']:
        if station_name == station:
            return True
    return False


def is_all_staions_on_route(route_data, station_names):
    for station_name in station_names:
        if not is_station_on_route(route_data, station_name):
            return False
    return True


def is_any_station_on_route(route_data, station_names):
    for station_name in station_names:
        if is_station_on_route(route_data, station_name):
            return True
    return False


def find_trains_with_stations(routes, stations):
    result_train_names = list()
    for route in routes:
        if is_all_staions_on_route(route, stations):
            result_train_names.append(route['train_name'])
    return result_train_names


def get_dataset():
    with open(f'{DATASET_PATH}/trains') as file_handler:
        return json.load(file_handler)


def read_train_data(train_name):
    with open(f'{DATASET_PATH}/train/{train_name}') as file_handler:
        return json.load(file_handler)


def main():
    station_names_to_search = ['Poznań Główny', 'Piła Główna']
    routes = get_dataset()['trains']
    result_trains = find_trains_with_stations(routes, station_names_to_search)
    result_trains = [train.replace('/', '_') for train in result_trains]
    trains_full_data = dict()
    for train in result_trains:
        train_data = read_train_data(train)
        train_info = dict()
        arrival_times_series = dict()
        departure_times_series = dict()
        arrival_delay_series = dict()
        departure_delay_series = dict()
        for schedule in train_data['schedules']:
            arrival_time = {
                station['station_name'].replace('Wlkp.', 'Wielkopolskie').replace(' WP2', '').replace(' Osobowy', '').replace('k. ', 'k/'):
                station['arrival_time'] for station in schedule['info']}
            departure_time = {
                station['station_name'].replace('Wlkp.', 'Wielkopolskie').replace(' WP2', '').replace(' Osobowy', '').replace('k. ', 'k/'):
                station['departure_time'] for station in schedule['info']}
            arrival_delay = {
                station['station_name'].replace('Wlkp.', 'Wielkopolskie').replace(' WP2', '').replace(' Osobowy', '').replace('k. ', 'k/'):
                station['arrival_delay'] for station in schedule['info']}
            departure_delay = {
                station['station_name'].replace('Wlkp.', 'Wielkopolskie').replace(' WP2', '').replace(' Osobowy', '').replace('k. ', 'k/'):
                station['departure_delay'] for station in schedule['info']}

            arrival_times_series[schedule['schedule_date']] = pd.Series(arrival_time)
            departure_times_series[schedule['schedule_date']] = pd.Series(departure_time)
            arrival_delay_series[schedule['schedule_date']] = pd.Series(arrival_delay)
            departure_delay_series[schedule['schedule_date']] = pd.Series(departure_delay)

        train_info['arrival_times'] = pd.concat(arrival_times_series, axis=1)
        train_info['departure_times'] = pd.concat(departure_times_series, axis=1)
        train_info['arrival_delay'] = pd.concat(arrival_delay_series, axis=1)
        train_info['departure_delay'] = pd.concat(departure_delay_series, axis=1)
        trains_full_data[train] = train_info



    railway_data = rs.scrap_line_data('354')
    station_names = list(railway_data.keys())

    # for train in trains_full_data.keys():
    #     df = trains_full_data[train]['arrival_delay']
    #     df.loc[df.index.intersection(station_names)].T.boxplot()
    #     plt.xticks(rotation=60)
    #     plt.xlabel('Stacja zatrzymania')
    #     plt.ylabel('Wielkość opóźnienia (min)')
    #     plt.title(f'Opóźnienia pociągu {train} w podziale na stacje')
    #     plt.savefig(f'{train}.png')
    #     plt.clf()



    selected_date = '2020-01-02'
    selected_date_begin = datetime.strptime(selected_date, '%Y-%m-%d')
    selected_date_end = selected_date_begin + timedelta(days=1, hours=0)

    times_list = list()
    for train_data in trains_full_data.values():
        train_list = list()
        if selected_date in train_data['arrival_times'].columns:
            train_list.append(train_data['arrival_times'][selected_date])
            train_list.append(train_data['departure_times'][selected_date])
            train_list.append(train_data['arrival_delay'][selected_date])
            train_list.append(train_data['departure_delay'][selected_date])
            times_list.append(train_list)

    for time in times_list:
        time_position_data = list()
        time_position_data_delay = list()
        is_enough_delay = False
        for item in time[0].items():
            if railway_data.get(item[0]) and item[1] and not item[1] != item[1]:
                schedule_arrival_date = datetime.fromisoformat(item[1])
                actual_arrival_date = schedule_arrival_date + timedelta(minutes=time[2].loc[item[0]])
                time_position_data.append((schedule_arrival_date, railway_data.get(item[0])[0][1]))
                time_position_data_delay.append((actual_arrival_date, railway_data.get(item[0])[0][1]))
                if time[2].loc[item[0]] > 0:
                    is_enough_delay=True
        for item in time[1].items():
            if railway_data.get(item[0]) and item[1] and not item[1] != item[1]:
                schedule_departure_date = datetime.fromisoformat(item[1])
                actual_departure_time = schedule_departure_date + timedelta(minutes=time[3].loc[item[0]])
                time_position_data.append((schedule_departure_date, railway_data.get(item[0])[0][1]))
                time_position_data_delay.append((actual_departure_time, railway_data.get(item[0])[0][1]))
                if time[3].loc[item[0]] > 0:
                    is_enough_delay=True
        time_position_data = sorted(time_position_data)
        time_position_data_delay = sorted(time_position_data_delay)
        plt.plot(*zip(*time_position_data), alpha = 0.5)
        if is_enough_delay:
            plt.plot(*zip(*time_position_data_delay), linestyle='dashed')

    for point_name in railway_data.keys():
        point = railway_data[point_name]
        # to change -
        if isinstance(point[0][1], float):
            plt.axhline(y=point[0][1], color='b', linestyle='-', alpha=0.2)
            if point[0][0] == 'stacja' or point[0][0] == 'stacja węzłowa':
                plt.text(selected_date_begin, point[0][1], point_name, alpha=0.5, fontsize=8.0, fontweight='bold')
            else:
                plt.text(selected_date_begin, point[0][1], point_name, alpha=0.5, fontsize=8.0)
        plt.xlim(left=selected_date_begin, right=selected_date_end)
    plt.show()


if __name__ == "__main__":
    main()




    # for time in times_list:
    #     time_position_data = list()
    #     time_position_data_delay = list()
    #     for item in time[0].items():
    #         if railway_data.get(item[0]) and item[1]:
    #             arrival_date = datetime.fromisoformat(item[1]
    #             time_position_data.append(, railway_data.get(item[0])[0][1]))
    #             time_position_data_delay.append((datetime.fromisoformat()))
    #     for item in time[1].items():
    #         if railway_data.get(item[0]) and item[1]:
    #             time_position_data.append((datetime.fromisoformat(item[1]), railway_data.get(item[0])[0][1]))
    #     time_position_data = sorted(time_position_data)
    #     plt.plot(*zip(*time_position_data))