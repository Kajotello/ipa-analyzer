import train_by_stations as tbs
import railway_line_data as rld
import traffic_plotter as tp
import pandas as pd
from datetime import datetime, timedelta
from scipy.optimize import bisect, brentq, brenth, ridder, toms748
import numpy as np
from functools import partial
import warnings
from tqdm import tqdm
from itertools import combinations


def is_train_in_operation_on_date(train_name, date):
    train_data = list(tbs.extract_all_trains_data([train_name]).values())[0]
    return date in train_data['arrival_time'].columns


def find_intersection_of_interpolate_plot(fun1, fun2, bound_min, bound_max):
    print('OPTIMIZER RUNNING')
    return bisect(lambda x: fun1(timestamp=x)-fun2(timestamp=x), bound_min, bound_max, xtol=5)


def get_train_timetable(train_name, posts_on_line, date):
    train_full_data = list(tbs.extract_all_trains_data([train_name]).values())[0]
    timetable = pd.DataFrame()
    delay = pd.DataFrame()

    timetable['arrival'] = train_full_data['arrival_time'].loc[[post for post in posts_on_line if post in train_full_data['arrival_time'].index], [date]]
    timetable['departure'] = train_full_data['departure_time'].loc[[post for post in posts_on_line if post in train_full_data['departure_time'].index], [date]]
    timetable = timetable.applymap(lambda x: datetime.fromisoformat(x), na_action='ignore')

    delay['arrival'] = train_full_data['arrival_delay'].loc[[post for post in posts_on_line if post in train_full_data['arrival_delay'].index], [date]]
    delay['departure'] = train_full_data['departure_delay'].loc[[post for post in posts_on_line if post in train_full_data['departure_delay'].index], [date]]
    delay = delay.applymap(lambda x: timedelta(minutes=x), na_action='ignore')

    # print(delay)
    # print(timetable+delay)
    my_time = datetime(2020,11,11,7,4,15)
    # print(timetable.iloc[(timetable['arrival']-my_time).abs().argsort()[:2]])
    # print(timetable.loc[timetable['arrival'] >= my_time, :])

    # print(timetable['departure'].min(numeric_only=False, skipna=True))
    return timetable


def interpolate_train_position(train_name, posts_on_line, date, timestamp):
    trains_full_data = tbs.extract_all_trains_data([train_name])
    time_position_points = tp.get_time_position_points(trains_full_data[train_name], posts_on_line, date)

    if time_position_points:
        xp = [datetime.timestamp(tp[0]) for tp in time_position_points]
        fp = [tp[1] for tp in time_position_points]
        return np.interp(timestamp, xp, fp)
    else:
        return None


def assign_position_functions_to_trains():
    posts_on_line = rld.get_posts_on_line('354')
    trains_on_line = tbs.get_trains_on_line(posts_on_line.keys())
    trains_function = {train_name: partial(interpolate_train_position, train_name=train_name, posts_on_line=posts_on_line, date='2020-11-11')
                        for train_name in trains_on_line
                        if is_train_in_operation_on_date(train_name, '2020-11-11')}
    return trains_function





posts_on_line = rld.get_posts_on_line('354')
trains_on_line = tbs.get_trains_on_line(posts_on_line.keys())
get_train_timetable('87206 PKM5', posts_on_line.keys(), '2020-11-11')
interpolate_train_position('87206 PKM5', posts_on_line,'2020-11-11', datetime(2020,11,11, 8, 30).timestamp())
trains_function = assign_position_functions_to_trains()

warnings.filterwarnings("ignore")
intersection_list = list()
train_pairs = combinations(trains_function.keys(), 2)
time_on_route_dict = {train_name: {'start': get_train_timetable(train_name, posts_on_line, '2020-11-11')['departure'].min(),
                                   'end': get_train_timetable(train_name, posts_on_line, '2020-11-11')['arrival'].max()}
                      for train_name in trains_function.keys()}
train_pairs = [train_pair for train_pair in train_pairs]
for train1, train2 in tqdm(train_pairs):
    if train1 != train2:
        train1_departure = time_on_route_dict[train1]['start']
        train1_arrival = time_on_route_dict[train1]['end']
        train2_departure = time_on_route_dict[train2]['start']
        train2_arrival = time_on_route_dict[train2]['end']

        if not (train1_arrival < train2_departure or train2_arrival < train1_departure):
            bound_min = datetime.timestamp(max(train1_departure, train2_departure))
            bound_max = datetime.timestamp(min(train1_arrival, train2_arrival))
            if np.sign(trains_function[train1](timestamp=bound_min)-trains_function[train2](timestamp=bound_min)) != np.sign(trains_function[train1](timestamp=bound_max)-trains_function[train2](timestamp=bound_max)):
                intersection_time = find_intersection_of_interpolate_plot(trains_function[train1], trains_function[train2], bound_min, bound_max)
                intersection_position = trains_function[train1](timestamp=intersection_time)
                intersection_list.append((train1, train2, intersection_position, intersection_time))
print(intersection_list)
print(len(intersection_list))






# def get_train_position(train_name, datetime):
#     pass


# def get_all_trains_on_line_positions(line_number, datetime) -> Dict:
#     pass


# def get_all_trains_on_line_positions_with_simulation(line_number, datetime) -> Dict:
#     pass


# def find_trains_to_begin(line_number, datetime):
#     pass


# def is_train_ended_on_line(train_number, line_number, datetime):
#     pass


# def is_train_during_stop(train_name, datetime):
#     pass


# def get_train_relative_position(train_name, datetime):
#     pass


# def is_train_to_depart(train_name, datetime):
#     pass


# def assign_time_position_function(train_name, time_start, time_end, position_start, positon_end):
#     pass


# def simulate(simulation_begin_time, simulation_end_time, line_number, time_step=timedelta(seconds=1)):
#     line_full_data = ...
#     simulation_temporary_history = dict()
#     simulation_history = dict()
#     simulation_time = simulation_begin_time
#     # dictionary with time-postion functions for trains as values
#     trains_on_route = get_all_trains_on_line_positions(line_number, simulation_begin_time)
#     for train_name in trains_on_route.keys():
#         if is_train_during_stop(train_name):
#             pass
#         else:
#             prev_stop_position, next_stop_position = get_train_relative_position(train_name, datetime)

#     while simulation_time < simulation_end_time:
#         for train_name in trains_on_route.keys():
#             if is_train_during_stop(train_name):
#                 pass
#             else:
#                 prev_stop_position, next_stop_position = get_train_relative_position(train_name, datetime)

#         simulation_time += time_step


# posts_on_line = rld.get_posts_on_line('354').keys()
# get_train_on_line_time('87206 PKM5', posts_on_line, '2020-11-11')
# #print(tbs.get_trains_on_line(posts_on_line))