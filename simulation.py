import crossover_find
from datetime import datetime, timedelta
import line_on_map
import json
import railway_line_data
import train_by_stations
import traffic_plotter


def run_simulation(day, line_number):
    # with open('myline.json') as fp:
    #     line_points = json.load(fp)['features'][0]['geometry']['coordinates'][1]

    with open('line213.json') as fp:
        line_points = json.load(fp)['features'][0]['geometry']['coordinates']

    # line_points1 = line_points[0]
    # line_points2 = line_points[1]
    # line_points2.reverse()

    # slice_index = line_points1.index([16.8184173,  52.6377305])
    # line_points1 = line_points1[:slice_index+1]
    # line_points = line_points1 + line_points2

    for point in line_points:
        point.reverse()

    line_position_mapping = line_on_map.return_line_positions_mapping(line_points, 62027)
    print(line_position_mapping.keys())

    simulation = dict()
    train_position_function = crossover_find.assign_position_functions_to_trains()
    trains_time_scope = crossover_find.get_time_on_line()
    simulation_start = datetime(2020, 8, 8, 0, 0)
    current_time = simulation_start
    train_on_route = []
    step=1

    for i in range(86_400):
        print(i)
        current_time += timedelta(seconds=step)
        if current_time.second % 30 == 0:
            for train in trains_time_scope.keys():
                start_time = trains_time_scope[train]['start']
                end_time = trains_time_scope[train]['end']
                if current_time == start_time:
                    train_on_route.append(train)
                    simulation[train] = {'line_position': [train_position_function[train](datetime.timestamp(current_time))],
                                        'coordinates': [line_position_mapping[int(train_position_function[train](datetime.timestamp(current_time))*1000)]],
                                        'name': train, 'start_time': (current_time-simulation_start).total_seconds()}
                if current_time == end_time:
                    try:
                        simulation[train]['coordinates'].append(line_position_mapping[int(train_position_function[train](datetime.timestamp(current_time))*1000)])
                        train_on_route.remove(train)
                    except Exception:
                        pass
        for train in train_on_route:
            simulation[train]['coordinates'].append(line_position_mapping[int(train_position_function[train](datetime.timestamp(current_time))*1000)])
            simulation[train]['line_position'].append(train_position_function[train](datetime.timestamp(current_time)))

    print(simulation)
    with open('simulation213.json', 'w') as fp:
        json.dump(simulation, fp, indent=4)

run_simulation('', '')


# line_data = railway_line_data.get_posts_on_line('213')
# posts_on_line = line_data.keys()
# trains_on_line = train_by_stations.get_trains_on_line(posts_on_line)
# trains_full_data = train_by_stations.extract_all_trains_data(trains_on_line)
# selected_date_begin = datetime.strptime('2020-08-08', '%Y-%m-%d')
# selected_date_end = selected_date_begin + timedelta(days=1, hours=0)
# schedule_time_points = traffic_plotter.prepare_data(trains_full_data, line_data, '2020-08-08')[0]

# train_position_dict = dict()
# for train in schedule_time_points.keys():
#     train_position_dict[train] = [{'x': x[0], 'y': x[1]} for x in schedule_time_points[train]]

# with open('chart213.json', 'w') as fp:
#     json.dump(train_position_dict, fp, indent=4, default=str)