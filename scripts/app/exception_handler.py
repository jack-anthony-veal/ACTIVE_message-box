import sys

import gc


def print_exception(error):
    print("---EXCEPTION---")
    try: sys.print_exception(error)
    except Exception: print(error)
    print("---------------")
    gc.collect()

def short_error_message(error):
    text = str(error)

    if text == "":
        text = error.__class__.__name__

    return text[:24]

