
def load_config():
    pass


def seconds_to_time_string(seconds):
    if seconds < 60:
        return f'{int(seconds)}s'
    elif seconds < 3600:
        minutes = seconds / 60
        return f'{int(minutes)}m'
    else:
        hours = seconds / 3600
        return f'{int(hours)}h'