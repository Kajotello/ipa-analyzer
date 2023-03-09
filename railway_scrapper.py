import mechanize
from bs4 import BeautifulSoup


def scrap_line_data(line_number):
    br = mechanize.Browser()
    response = br.open(f'https://semaforek.kolej.org.pl/wiki/index.php?title={line_number}')
    soup = BeautifulSoup(response, 'html.parser')
    data = list()
    table = soup.find('table', attrs={'class': 'wikitable', 'style': "text-align:center"})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    rowspan = 1
    point_data = list()
    for row in rows:
        cells = row.find_all('td')
        for cell in cells:
            if cell.get("rowspan"):
                rowspan = int(cell.get("rowspan"))
        point_data.append([cell.text.strip() for cell in cells if cell.text.strip()])
        if rowspan > 1:
            rowspan -= 1
        else:
            data.append(point_data)
            point_data = list()

    crude_data = [point for point in data if point][1:-19]
    data = dict()
    for point in crude_data:
        if len(point) == 1 and 'Ekspozytura' not in point[0][0] and 'wiadukt' not in point[0][0] and 'Zakład Linii' not in point[0][0] and 'ex' not in point[0][0]:
            if data.get(point[0][0]):
                data[point[0][0]].append((point[0][1], float(point[0][2].replace(',', '.'))))
            else:
                data[point[0][0]] = [(point[0][1], float(point[0][2].replace(',', '.')))]
        elif len(point) > 1 and 'ex' not in point[0][0]:
            data[point[0][0]] = point

    #tymczasowa proteza
    data['Poznań Główny'] = [('stacja węzłowa', -2.502)]
    data['Piła Główna'] = [('stacja węzłowa', 92.538)]

    return data
