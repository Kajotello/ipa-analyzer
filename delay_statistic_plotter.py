    # for train in trains_full_data.keys():
    #     df = trains_full_data[train]['arrival_delay']
    #     df.loc[df.index.intersection(station_names)].T.boxplot()
    #     plt.xticks(rotation=60)
    #     plt.xlabel('Stacja zatrzymania')
    #     plt.ylabel('Wielkość opóźnienia (min)')
    #     plt.title(f'Opóźnienia pociągu {train} w podziale na stacje')
    #     plt.savefig(f'{train}.png')
    #     plt.clf()
