from datetime import datetime

import pandas as pd
import arcticdb as adb

class ArcticDBOperator:
    pass


def get_data():
    df = pd.read_csv(r'C:\Users\l8432\Downloads\BTCUSDT-1m-2024-04-05\BTCUSDT-1m-2024-04-05.csv')
    return df


def format_data(data):
    start_timestamp_ms = data.iloc[0]['open_time']
    start_timestamp_sec = start_timestamp_ms / 1000
    start_time = pd.to_datetime(start_timestamp_sec, unit='s')
    end_timestamp_ms= data.iloc[-1]['open_time']
    end_timestamp_ms = end_timestamp_ms / 1000
    end_time = pd.to_datetime(end_timestamp_ms, unit='s')
    data = data.set_index(pd.date_range(start=start_time, end=end_time, freq='min'))
    return data


def write_database(formated_data, lib_name, data_name):
    ac = adb.Arctic("lmdb:///Leon/SideProject/quant")
    print(ac.list_libraries())

    lib = ac[lib_name]
    lib.write(data_name, formated_data)



if __name__ == '__main__':
    lib_path = "lmdb:///Leon/SideProject/quant"
    lib_name = 'travel_data'


    # data = get_data()
    # formated_data = format_data(data)
    # write_database(formated_data, lib_name, data_name='BTCUSDT')

    ac = adb.Arctic(lib_path)
    lib = ac[lib_name]
    data = lib.read('BTCUSDT')
    data2 = lib.read("BTCUSDT", date_range=(datetime(2024, 4, 5, 1, 16), datetime(2024, 4, 5, 2, 17)))
    print(data2.data)