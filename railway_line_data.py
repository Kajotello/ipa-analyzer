import pandas as pd
pd.options.mode.chained_assignment = None


class Post:
    def __init__(self, name, position, type, next_post=None, prev_post=None,
                 next_section=None, prev_section=None) -> None:
        self.name = name
        self.position = position
        self.type = type
        self.next_post = next_post
        self.prev_post = prev_post
        self._next_section = next_section
        self._prev_section = prev_section

    def __str__(self) -> str:
        return f'{self.type} {self.name} - {self.position} km'

    def __gt__(self, other):
        return self.position > other.position

    def set_next_section(self, new_next_section):
        self._next_section = new_next_section

    def set_prev_section(self, new_prev_section):
        self._prev_section = new_prev_section


class LineBlock:
    def __init__(self, status) -> None:
        self.status = status



class LineSection:
    def __init__(self, n_of_tracks, section_speed_data) -> None:
        self.n_of_tracks = n_of_tracks
        self.is_with_ABS = False
        self._speed_data = sorted(section_speed_data)
        if n_of_tracks == 2:
            for speed_segement in self._speed_data:
                if not speed_segement.max_speed_even:
                    raise Exception('Even direction speed data compulsory for two tracks')

    def get_section_speed_stats(self, direction):
        speed_stats = dict()
        if direction == 'odd' or direction == 'even' and self.n_of_tracks == 1:
            for speed_segment in self._speed_data:
                speed_stats[speed_segment.max_spped_odd] = \
                    speed_stats.get(speed_segment.max_spped_odd, 0) + speed_segment.get_segment_length()
            return speed_stats
        elif direction == 'even':
            for speed_segment in self._speed_data:
                speed_stats[speed_segment.max_spped_even] = \
                    speed_stats.get(speed_segment.max_spped_even, 0) + speed_segment.get_segment_length()
            return speed_stats
        else:
            raise Exception('Invalid value for direction property')

    def get_section_full_data(self, direction):
        section_data = list()
        if direction == 'odd' or direction == 'even' and self.n_of_tracks == 1:
            for speed_segemnt in self._speed_data:
                if section_data and section_data[-1][1] == speed_segemnt.max_speed_odd:
                    section_data[-1][0] += speed_segemnt.get_segment_length()
                else:
                    section_data.append((speed_segemnt.get_segment_length(), speed_segemnt.max_speed_odd))
        elif direction == 'even':
            for speed_segemnt in self._speed_data:
                if section_data and section_data[-1][1] == speed_segemnt.max_speed_even:
                    section_data[-1][0] += speed_segemnt.get_segment_length()
                else:
                    section_data.append((speed_segemnt.get_segment_length(), speed_segemnt.max_speed_even))
        else:
            raise Exception('Invalid value for direction property')

    def get_section_begin(self):
        return self._speed_data[0].position_begin

    def get_section_end(self):
        return self._speed_data[-1].position_end


class LineSpeedSegment:
    def __init__(self, position_begin, position_end, max_speed_odd, max_speed_even=None) -> None:
        if position_begin > position_end:
            raise Exception("Position of the begin couldn't be greater than position of the end")
        self.max_speed_odd = max_speed_odd
        self.max_speed_even = max_speed_even
        self.position_begin = position_begin
        self.position_end = position_end

    def get_segment_length(self):
        return self.position_end - self.position_begin

    def __gt__(self, other):
        return self.position_begin > other.position_begin

    def __str__(self) -> str:
        return f'{self.position_begin} - {self.position_end}, vmax={self.max_speed_odd}/{self.max_speed_even} [km/h]'


def get_all_lines_data(filename):
    df = pd.read_excel(filename, 'Załącznik 2.6 dane')
    df.columns = df.iloc[0]
    df['Nr linii'] = df['Nr linii'].str.strip()
    return df.iloc[2:, :5]


def get_posts_on_line(line_number):
    all_lines_df = get_all_lines_data('posts.xlsx')
    selected_line_df = all_lines_df.loc[all_lines_df['Nr linii'] == line_number]

    # to change in future, not exactly correct
    selected_line_df = selected_line_df.replace(['Poznań POD'], value='Poznań Główny')
    return dict(zip(selected_line_df['Nazwa punktu'], zip(selected_line_df['Km osi'], selected_line_df['Wyróżnik'])))


def get_line_data(line_number):
    all_lines_df = get_all_lines_data('posts.xlsx')
    selected_line_df = all_lines_df.loc[all_lines_df['Nr linii'] == line_number]
    return selected_line_df.sort_values('Km osi')


def get_posts_on_line_2(line_number):
    selected_line_df = get_line_data(line_number)
    return [Post(*list(post_data.values())) for post_data in selected_line_df.loc[:, ['Nazwa punktu', 'Km osi', 'Wyróżnik']].to_dict(orient='records')]


def get_full_speed_data(filename):
    df = pd.read_excel(filename, 'Zalącznik 2.1P dane')
    df.columns = df.iloc[0]
    return df.iloc[2:]


def get_line_speed_data(line_number):
    line_speed_df = get_full_speed_data('line_speed.xlsx')
    line_speed_df['Nr linii'] = line_speed_df['Nr linii'].str.strip()
    selected_line_df = line_speed_df.loc[line_speed_df['Nr linii'] == line_number]
    return selected_line_df


# def get_full_line_data(line_number):
#     speed_data = get_line_speed_data(line_number)


post_data = get_posts_on_line_2('202')
post_df = get_line_data('202')
speed_df = get_line_speed_data('202')
curr_post = post_data[0]
is_previous_two_tracks = False
for post1, post2 in zip(post_data, post_data[1:]):
    post1.next_post = post2
    post2.prev_post = post1
    sections_between_posts = speed_df.loc[(speed_df['Km końca'] >= post1.position) & (speed_df['Km pocz. '] <= post2.position)]
    section_speed_data = list()
    if 'P' in sections_between_posts['Tor'].values:
        n_of_tracks = 1
        if ((post1.type not in ['ST', 'PODG'] and not is_previous_two_tracks) or
            (post1.type in ['ST', 'PODG'] and (min(sections_between_posts.loc[sections_between_posts['Tor'] == 'P', 'Km końca'].max(), post2.position)-post1.position)/(post2.position-post1.position) < 0.15) or
              (post2.type in ['ST', 'PODG'] and (post2.position - max(sections_between_posts.loc[sections_between_posts['Tor'] == 'P', 'Km pocz. '].min(), post1.position))/(post2.position-post1.position) < 0.15)):
            is_previous_two_tracks = False
            sections_between_posts.loc[sections_between_posts["Km pocz. "] < post1.position, 'Km pocz. '] = post1.position
            sections_between_posts.loc[sections_between_posts["Km końca"] > post2.position, 'Km końca'] = post2.position
            odd_direction_sections = sections_between_posts.loc[sections_between_posts['Tor'] == 'N', ['Km pocz. ', 'Km końca', 'Maks. prędkość [km/h]']].sort_values('Km pocz. ').to_dict(orient='records')
            odd_direction_sections = {section['Km pocz. ']: tuple(section.values()) for section in odd_direction_sections}
            sections_breaking_points = set()
            previous_max_spped = None
            for section in sorted(list(odd_direction_sections.values())):
                if previous_max_spped and section[2] == previous_max_spped:
                    sections_breaking_points.remove(section[0])
                    sections_breaking_points.add(section[1])
                else:
                    sections_breaking_points.add(section[0])
                    sections_breaking_points.add(section[1])
                    previous_max_spped = section[2]
            sections_breaking_points = sorted(sections_breaking_points)
            for section_begin, section_end in zip(sections_breaking_points, sections_breaking_points[1:]):
                max_speed_odd = odd_direction_sections[section_begin][2]
                line_segment = LineSpeedSegment(section_begin, section_end, max_speed_odd)
                section_speed_data.append(line_segment)
        else:
            n_of_tracks = 2
            is_previous_two_tracks = True
            if sections_between_posts.loc[sections_between_posts['Tor'] == 'N', "Km pocz. "].min() > post1.position:
                value_to_replace = sections_between_posts.loc[sections_between_posts['Tor'] == 'N', "Km pocz. "].min()
                sections_between_posts.loc[(sections_between_posts['Tor'] == 'N') &(sections_between_posts['Km pocz. '] == value_to_replace), 'Km pocz. '] = post1.position

            if sections_between_posts.loc[sections_between_posts['Tor'] == 'P', "Km pocz. "].min() > post1.position:
                value_to_replace = sections_between_posts.loc[sections_between_posts['Tor'] == 'P', "Km pocz. "].min()
                sections_between_posts.loc[(sections_between_posts['Tor'] == 'P') &(sections_between_posts['Km pocz. '] == value_to_replace), 'Km pocz. '] = post1.position

            if sections_between_posts["Km końca"].max() < post2.position:
                sections_between_posts.loc[sections_between_posts["Km końca"].max(), 'Km końca'] = post2.position

            sections_between_posts.loc[sections_between_posts["Km pocz. "] < post1.position, 'Km pocz. '] = post1.position
            sections_between_posts.loc[sections_between_posts["Km końca"] > post2.position, 'Km końca'] = post2.position
            odd_direction_sections = sections_between_posts.loc[sections_between_posts['Tor'] == 'N', ['Km pocz. ', 'Km końca', 'Maks. prędkość [km/h]']].sort_values('Km pocz. ').to_dict(orient='records')
            odd_direction_sections = {section['Km pocz. ']: tuple(section.values()) for section in odd_direction_sections}
            even_direction_sections = sections_between_posts.loc[sections_between_posts['Tor'] == 'P', ['Km pocz. ', 'Km końca', 'Maks. prędkość [km/h]']].sort_values('Km pocz. ').to_dict(orient='records')
            even_direction_sections = {section['Km pocz. ']: tuple(section.values()) for section in even_direction_sections}
            print(odd_direction_sections, even_direction_sections)
            sections_breaking_points_1 = set()
            sections_breaking_points_2 = set()
            previous_max_spped = None
            for section in sorted(list(odd_direction_sections.values())):
                if previous_max_spped and section[2] == previous_max_spped:
                    if section[1] in sections_breaking_points_1:
                        sections_breaking_points_1.remove(section[0])
                    sections_breaking_points_1.add(section[1])
                else:
                    sections_breaking_points_1.add(section[0])
                    sections_breaking_points_1.add(section[1])
                    previous_max_spped = section[2]
            previous_max_spped = None
            for section in sorted(list(even_direction_sections.values())):
                if previous_max_spped and section[2] == previous_max_spped:
                    if section[0] in sections_breaking_points_2:
                        sections_breaking_points_2.remove(section[0])
                    sections_breaking_points_2.add(section[1])
                else:
                    sections_breaking_points_2.add(section[0])
                    sections_breaking_points_2.add(section[1])
                    previous_max_spped = section[2]
            print(sections_breaking_points_1, sections_breaking_points_2)
            sections_breaking_points = sections_breaking_points_1.union(sections_breaking_points_2)
            sections_breaking_points = sorted(sections_breaking_points)
            previous_max_spped_odd = None
            previous_max_spped_even = None
            for section_begin, section_end in zip(sections_breaking_points, sections_breaking_points[1:]):
                max_speed_odd = odd_direction_sections.get(section_begin, ('','',previous_max_spped_odd))[2]    # tuple to chnage - really ugly
                max_speed_even = even_direction_sections.get(section_begin, ('','',previous_max_spped_even))[2]
                line_segment = LineSpeedSegment(section_begin, section_end, max_speed_odd, max_speed_even)
                section_speed_data.append(line_segment)
                previous_max_spped_odd = max_speed_odd
                previous_max_spped_even = max_speed_even
    else:
        n_of_tracks = 1
        is_previous_two_tracks = False
        sections_between_posts.loc[sections_between_posts["Km pocz. "] < post1.position, 'Km pocz. '] = post1.position
        sections_between_posts.loc[sections_between_posts["Km końca"] > post2.position, 'Km końca'] = post2.position
        odd_direction_sections = sections_between_posts.loc[sections_between_posts['Tor'] == 'N', ['Km pocz. ', 'Km końca', 'Maks. prędkość [km/h]']].sort_values('Km pocz. ').to_dict(orient='records')
        odd_direction_sections = {section['Km pocz. ']: tuple(section.values()) for section in odd_direction_sections}
        sections_breaking_points = set()
        previous_max_spped = None
        for section in sorted(list(odd_direction_sections.values())):
            if previous_max_spped and section[2] == previous_max_spped:
                sections_breaking_points.remove(section[0])
                sections_breaking_points.add(section[1])
            else:
                sections_breaking_points.add(section[0])
                sections_breaking_points.add(section[1])
                previous_max_spped = section[2]
        sections_breaking_points = sorted(sections_breaking_points)
        for section_begin, section_end in zip(sections_breaking_points, sections_breaking_points[1:]):
            max_speed_odd = odd_direction_sections[section_begin][2]
            line_segment = LineSpeedSegment(section_begin, section_end, max_speed_odd)
            section_speed_data.append(line_segment)
    line_section = LineSection(n_of_tracks, section_speed_data)
    post1._next_section = line_section
    post2._prev_section = line_section


while(curr_post):
    print(curr_post)
    if curr_post._next_section:
        print(f'Liczna torów: {curr_post._next_section.n_of_tracks}')
        for segment in curr_post._next_section._speed_data:
            print(segment)
    print('\n')
    curr_post = curr_post.next_post


