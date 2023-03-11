import sys


def get_selected_guid():
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        return None


def get_selected_guids_list():
    return sys.argv[1:]  # returns empty list on invalid range
