import pandas as pd
import numpy as np
import glob

if __name__ == "__main__":



    # for filename in glob.glob("data/PrecisLoc/Scenario_1/**/ground*"):
    #     print(filename)


    # x0 = "11:05:07:87"
    # x = "11:06:37:24"
    # x1 = "11:6:37:24"
    # "1 min 29 sec 370 ms"
    # hours_init, min_init, sec_init, ms_init = x0.split(':')
    # hours_end, min_end, sec_end, ms_end = x.split(':')
    # # The data is taken each 10 ms, so for the ms we must multiply by 10
    # time_init = int(hours_init) * 60 * 60 * 1000 + int(min_init) * 60 * 1000 + int(sec_init)  * 1000 + int(ms_init) * 10
    # time_end = int(hours_end) * 60 * 60 * 1000 + int(min_end) * 60 * 1000 + int(sec_end)  * 1000 + int(ms_end) * 10
    # milisec_range = time_end - time_init
    # print(milisec_range)
    # print(hours_init, min_init, sec_init, ms_init)
    # print(hours_end, min_end, sec_end, ms_end )
    # print(x1 == x)

    # t_current = pd.date_range("11:05:07.87", "11:06:37.24", freq="10L")

    # test = t_current.map(lambda t: str(t).split(" ")[1][:-4].replace(".", ":"))

    # print(test)

    # df = pd.DataFrame(np.nan, index=test, columns=['ax',
    #                                                                'ay',
    #                                                                'az',
    #                                                                'a_total' ,
    #                                                                'gx',
    #                                                                'gy',
    #                                                                'gz',
    #                                                                'g_total',
    #                                                                'mx',
    #                                                                'my',
    #                                                                'mz',
    #                                                                'm_total'])

    # print(df)

    data = {'a': [ 1, np.NaN, 3, np.NaN], 'b': [4, 5, 6, 7]}
    df = pd.DataFrame(data=data)
    df['x'] = df['a'] + df['b']
    df.loc[:, 'a'].interpolate(inplace=True)
    print(df)