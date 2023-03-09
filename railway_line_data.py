import pandas as pd


def get_all_lines_data(filename):
    return pd.read_excel(filename, 'Załącznik 2.6 dane')


def get_posts_on_line(line_number):
    all_lines_df = get_all_lines_data('posts.xlsx')
    all_lines_df.columns = all_lines_df.iloc[0]
    all_lines_df = all_lines_df.iloc[3:, :5]
    all_lines_df['Nr linii'] = all_lines_df['Nr linii'].str.strip()
    selected_line_df = all_lines_df.loc[all_lines_df['Nr linii'] == line_number]

    # to change in future, not exactly correct
    selected_line_df = selected_line_df.replace(['Poznań POD'], value='Poznań Główny')
    return dict(zip(selected_line_df['Nazwa punktu'], zip(selected_line_df['Km osi'], selected_line_df['Wyróżnik'])))
