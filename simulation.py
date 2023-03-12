import train_by_stations as tbs
import railway_line_data as rld
import pandas as pd
from datetime import datetime, timedelta


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

    print(timetable)
    # print(delay)
    # print(timetable+delay)
    my_time = datetime(2020,11,11,7,4,15)
    print(timetable.iloc[(timetable['arrival']-my_time).abs().argsort()[:2]])
    print(timetable.loc[timetable['arrival'] >= my_time, :])

    print(timetable['departure'].min(numeric_only=False, skipna=True))


def get_train_position(train_name, datetime):
    pass


def get_all_trains_on_line_positions(line_number, datetime):
    pass


def simulate(simulation_begin_time, simulation_end_time, time_step, line_number):
    line_full_data = line_number
    simulation_time = simulation_begin_time
    while simulation_time < simulation_end_time:
        pass
        simulation_time += time_step


posts_on_line = rld.get_posts_on_line('354').keys()
get_train_on_line_time('87206 PKM5', posts_on_line, '2020-11-11')
#print(tbs.get_trains_on_line(posts_on_line))