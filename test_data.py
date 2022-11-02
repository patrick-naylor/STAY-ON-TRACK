# Written by Patrick Naylor
# Add date data

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
from scipy.optimize import curve_fit
import random
import sqlite3


def main():
    x = np.arange(500) * ((2 * math.pi) / 49) * (500 / (365 / 12))
    r = (np.random.random_sample(500) / 2) + 0.75
    Day = (np.sin(x * r) + 1) / 2

    p = np.arange(0, 0.05, 0.0001)

    y = []
    means = []
    for i in list(np.arange(0, 0.05, 0.0001)):
        rtest = (np.random.random_sample(500) * (2 * i)) + (1 - i)
        vartest = (np.sin(x * r * rtest) + 1) / 2
        y.append(np.corrcoef(Day, vartest)[0, 1])

    def func(x, a, b, c):
        return a * np.exp(-b * x) + c

    popt, pcov = curve_fit(func, p, y, [20, 2130, 0.1], maxfev=10000)
    # print(popt)
    # plt.plot(p, y)

    y_fit = func(p, *popt)
    coeffs = [0.8, 0.6, 0.6, 0.4, 0.3, 0.2]
    coeffs_x = []
    for c in coeffs:
        diff_array = np.absolute(y_fit - c)
        coeffs_x.append(p[np.argmin(diff_array)])
    # print(coeffs_x)

    data_arrays = []
    me_data_arrays = []
    scalars = []
    for c_x in coeffs_x:
        scalar = random.randint(0, 10000)
        scalars.append(scalar)
        r1 = (np.random.random_sample(500) * (2 * c_x)) + (1 - c_x)
        var = (np.sin(x * r * r1) + 1) / 2
        # print(np.corrcoef(Day, var)[0,1])
        me_data_arrays.append(var)
        data_arrays.append(var * scalar)
    dates = np.arange("2020-01", "2021-05-15", dtype="datetime64[D]")
    dates_pd = pd.to_datetime(dates)
    dates_str = dates_pd.strftime("%m-%d-%Y")

    # print(np.mean(np.array(data_arrays), axis=0))
    df = pd.DataFrame(
        {
            "Date": dates_str,
            "Me": np.mean(np.array(me_data_arrays), axis=0),
            "Day": Day,
            "Var1": data_arrays[0],
            "Var2": data_arrays[1],
            "Var3": data_arrays[2],
            "Var4": data_arrays[3],
            "Var5": data_arrays[4],
            "Var6": data_arrays[5],
        }
    )
    print(scalars)
    conn = sqlite3.connect("sample_data.db")
    df.to_sql("log", conn, if_exists="replace", index=False)

    df_var = pd.DataFrame(
        {
            "Variable": ["Var1", "Var2", "Var3", "Var4", "Var5", "Var6"],
            "GoalType": [
                "Process Goal",
                "Process Goal",
                "Process Goal",
                "Process Goal",
                "Process Goal",
                "Process Goal",
            ],
            "Goal": (np.array(scalars) / 2),
            "ListOrder": np.arange(1, 7),
        }
    )
    df_var.to_sql("variables", conn, if_exists="replace", index=False)
    conn.close()


if __name__ == "__main__":
    main()
