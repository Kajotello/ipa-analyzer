import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import train_by_stations as tbs
import railway_line_data as rld
import consts
from collections import defaultdict


def plot_traffic_graph(line_number, date, is_with_delay):
    line_data = rld.get_posts_on_line(line_number)
    posts_on_line = line_data.keys()
    trains_on_line = tbs.get_trains_on_line(posts_on_line)
    trains_full_data = tbs.extract_all_trains_data(trains_on_line)
    selected_date_begin = datetime.strptime(date, '%Y-%m-%d')
    selected_date_end = selected_date_begin + timedelta(days=1, hours=0)

    plot_posts(line_data, selected_date_begin)
    scheduled_time_position_data, real_time_position_data = prepare_data(trains_full_data, line_data, date)

    if is_with_delay:
        for train_name in real_time_position_data.keys():
            train_position = real_time_position_data[train_name]
            plt.plot(*zip(*train_position), color='black')
        for train_name in scheduled_time_position_data.keys():
            train_positions = scheduled_time_position_data[train_name]
            plt.plot(*zip(*train_positions), alpha=0.5, linestyle='dashed', color='black')
    else:
        for train_name in scheduled_time_position_data.keys():
            train_position = scheduled_time_position_data[train_name]
            plt.plot(*zip(*train_position), color='black')
    plt.xlim(left=selected_date_begin, right=selected_date_end)
    plt.title(f'Wykres ruchu pociągów na linii kolejowej nr {line_number}')
    plt.xlabel(f'Data i godzina')
    plt.ylabel('Pożenie (km. linii)')


def prepare_data(trains_full_data, line_data, date):
    scheduled_time_point_dict = defaultdict(list)
    real_time_point_dict = defaultdict(list)

    for train_name in trains_full_data.keys():
        train = trains_full_data[train_name]
        # TODO rewrite to check this condition only once
        if date in train[consts.ATTRIBUTES[0]].columns:
            scheduled_time_point_dict[train_name] = get_time_position_points(train, line_data, date, 'schedule')
            real_time_point_dict[train_name] = get_time_position_points(train, line_data, date, 'real')

    return (scheduled_time_point_dict, real_time_point_dict)


def get_time_position_points(train_data, line_data, date, type='schedule'):
    train_time_position_points = list()
    if date in train_data[consts.ATTRIBUTES[0]].columns:
        for schedule_attribute, delay_attribute in zip(consts.ATTRIBUTES[0::2], consts.ATTRIBUTES[1::2]):
            train_time_points = [*zip(train_data[schedule_attribute][date], train_data[delay_attribute][date],
                                      train_data[schedule_attribute].index)]
            train_time_position_points += [(datetime.fromisoformat(train_tp[0]), line_data.get(train_tp[2])[0]) if type=='schedule'
                                           else (datetime.fromisoformat(train_tp[0])+timedelta(minutes=train_tp[1]), line_data.get(train_tp[2])[0])
                                           for train_tp in train_time_points
                                           if line_data.get(train_tp[2]) and
                                           train_tp[0] and train_tp[0] == train_tp[0]]
        return sorted(train_time_position_points)
    else:
        return None


def plot_posts(line_data, selected_date_begin):
    for post_name in line_data.keys():
        post = line_data[post_name]
        plt.axhline(y=post[0], color='b', linestyle='-', alpha=0.2)
        if post[1] == 'ST':
            plt.text(selected_date_begin, post[0], post_name, alpha=0.5, fontsize=8.0, fontweight='bold')
        else:
            plt.text(selected_date_begin, post[0], post_name, alpha=0.5, fontsize=8.0)


def main():
    plot_traffic_graph('271', '2020-11-11', False)
    plt.show()


if __name__ == '__main__':
    main()
