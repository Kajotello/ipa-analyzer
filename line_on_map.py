import json
import geopy.distance


def return_line_positions_mapping(line_map_data, line_length):
    line_position_mapping = dict()
    line_position = -1
    line_position_calculated = -600
    step = 1
    cursor = 1
    prev_point = line_map_data[0]
    next_point = line_map_data[cursor]
    distance_between_points = geopy.distance.distance(prev_point, next_point).m

    while line_position < line_length:
        line_position += step

        while line_position > line_position_calculated:
            prev_point = next_point
            cursor += 1
            if len(line_map_data) == cursor:
                print(cursor, len(line_map_data), line_position, line_length)
                break
            else:
                next_point = line_map_data[cursor]
                distance_between_points = geopy.distance.distance(prev_point, next_point).m
                line_position_calculated += distance_between_points
        lat_difference = next_point[0] - prev_point[0]
        lon_differnce = next_point[1] - prev_point[1]
        difference = line_position_calculated-line_position
        line_position_mapping[line_position] = [next_point[0] - lat_difference*(difference/distance_between_points), next_point[1] - lon_differnce*(difference/distance_between_points)]

    return line_position_mapping


if __name__ == '__main__':

    with open('line271.json') as fp:
        line_points = json.load(fp)['features'][0]['geometry']['coordinates'][0]

    print(line_points)
    print(len(line_points))
    slice_index = line_points.index([16.9107529, 52.4007412])
    line_points = line_points[:slice_index]
    print(len(line_points))

    # line_points1 = line_points[0]
    # line_points2 = line_points[1]
    # line_points2.reverse()

    # slice_index = line_points1.index([16.8184173,  52.6377305])
    # line_points1 = line_points1[:slice_index+1]
    # line_points = line_points1 + line_points2

    for point in line_points:
        point.reverse()


    line_position_mapping = return_line_positions_mapping(line_points, 163700)
    print(line_position_mapping[100000])
