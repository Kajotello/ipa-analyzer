import train_by_stations as tbs
import railway_line_data as rld
import consts


def get_train_on_line_time(train_name, posts_on_line, date):
    train_full_data = tbs.extract_all_trains_data(train_name)



posts_on_line = rld.get_posts_on_line('354').keys()