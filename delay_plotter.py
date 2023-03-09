import json
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from statistics import mean, median
import seaborn as sns

with open("18106_7-MEWA") as file_handler:
    data = json.load(file_handler)
# departure_delays = [[stop_data['departure_delay'] for stop_data in schedule['info'][:-1]] for schedule in data['schedules']]
stops = [stop_data['station_name'] for stop_data in data['schedules'][0]['info'][:-1]]
# for day_delay in departure_delays:
#     if(len(stops)==len(day_delay)):
#         plt.plot(stops, day_delay, '-')
# plt.xticks(rotation=90)
# plt.show()
sns.set_theme()
sequential_colors = sns.color_palette("rocket", 7)
sns.set_palette(sequential_colors)
plt.subplots_adjust(bottom=0.2)

week = [[] for _ in range(7)]
for schedule in data['schedules']:
    schedule_data = [stop_data['departure_delay'] for stop_data in schedule['info'][:-1]]
    if None not in schedule_data:
        week[datetime.weekday(datetime.strptime(schedule['schedule_date'], '%Y-%m-%d'))].append(schedule_data)
print([x for x in zip(*week[0])])
week_delays = [[mean(x) for x in zip(*week_day)] for week_day in week]
print(week_delays)
days = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
for i, day in zip(days, week_delays):
    plt.plot(stops, day, label=i)
plt.xticks(rotation=60)
plt.xlabel("Stacje", fontweight="bold")
plt.ylabel("Wielkość opóźnienia (min)", fontweight="bold")
plt.title("Średnie opóżnienia pociągu IC Mewa w podziale na dni tygodnia", fontweight="bold")
plt.legend()

plt.show()

