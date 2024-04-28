from datetime import datetime

import arcticdb as adb
import numpy as np
import pandas as pd

NUM_COLUMNS=10
NUM_ROWS=100_000

df = pd.DataFrame(np.random.randint(0,100,size=(NUM_ROWS, NUM_COLUMNS)), 
                  columns=[f"COL_{i}" for i in range(NUM_COLUMNS)], 
                  index=pd.date_range('2000', periods=NUM_ROWS, freq='h'))

ac = adb.Arctic("lmdb:///Leon/SideProject/quant")
# ac.create_library('travel_data')
print(ac.list_libraries())

lib = ac['travel_data']
# lib.write("my_data", df)
data = lib.read("my_data", date_range=(datetime(2000, 1, 3, 0, 0), datetime(2000, 1, 4, 15, 0)))
a = data.data
print(data.data)