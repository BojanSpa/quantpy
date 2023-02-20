import numpy as np
import pandas as pd
from datetime import datetime

rate = 0.05
sigma = 0.5


def generateSampleData(fromDate, rows, columns, freq = '1min'):
    rows = int(rows)
    columns = int(columns)
    index = pd.date_range(fromDate, periods = rows, freq = freq)
    delta = (index[1] - index[0]) / pd.Timedelta(value = '365D')
    columnNames = ['Column%d' % i for i in range(columns)]
    raw = np.exp(
        np.cumsum(
            (rate - 0.5 * sigma ** 2) * delta + sigma * np.sqrt(delta) * 
            np.random.standard_normal((rows, columns)), 
            axis = 0
        )
    )
    raw = raw / raw[0] * 100
    return pd.DataFrame(raw, index = index, columns = columnNames)


if __name__ == '__main__':
    fromDate = datetime(2020, 1, 1)
    rows = 5
    columns = 3
    freq = 'D'
    dataFrame = generateSampleData(fromDate, rows, columns, freq)
    print(dataFrame)
    