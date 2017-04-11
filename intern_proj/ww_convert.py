import datetime
import math


@outputSchema("ww_output:chararray")
def get_ww(date_time_local):

    temp = date_time_local[:19]

    input_date = datetime.datetime.strptime(temp, "%Y-%m-%d %H:%M:%S")
    reference_date = datetime.datetime.strptime("2016-12-29 19:00:00", "%Y-%m-%d %H:%M:%S")

    sec_diff = input_date - reference_date
    total_seconds = sec_diff.seconds + sec_diff.days * 24 * 60 * 60

    week_diff = int(math.floor(total_seconds / (7 * 24 * 60 * 60)))
    week_num = int((week_diff % 52)) + 1
    year_num = 2017 + int(math.floor(week_diff / 52))

    ww_str = []
    ww_str.append(str(year_num))
    ww_str.append(str(week_num).zfill(2))

    ww_output = "".join(ww_str)
    return ww_output
