import functools
import datetime
#usage of decorator to assign time stamp for attributes.
def log_action(action: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"[{datetime.datetime.now()}] ACTION: {action}")
            return func(*args, **kwargs)
        return wrapper
    return decorator
