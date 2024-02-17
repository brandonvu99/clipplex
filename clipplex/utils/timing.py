from datetime import datetime, timedelta


def milli_to_string(millisec: int) -> str:
    time = str(timedelta(milliseconds=millisec))
    if len(time.split(":")[0]) < 2:
        time = f"0{time}"
    return time.split(".")[0]


def add_time(current_time: str, time_to_add: int) -> str:
    time_obj = datetime.strptime(current_time, "%H:%M:%S")
    time_obj_with_time_added = time_obj + timedelta(seconds=time_to_add)
    return time_obj_with_time_added.strftime("%H:%M:%S")


def _pad_time(time) -> str:
    if len(str(time)) < 2:
        time = f"0{time}"
    return time


def calculate_clip_time(start, end) -> int:
    start = start.split(":")
    start_total_sec = (int(start[0]) * 3600) + (int(start[1]) * 60) + (int(start[2]))
    end = end.split(":")
    end_total_sec = (int(end[0]) * 3600) + (int(end[1]) * 60) + (int(end[2]))
    total_second = end_total_sec - start_total_sec
    return total_second
