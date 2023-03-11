if __name__ != '__main__':
    print(f'error: {__file__} should not be imported, aborting script')
    exit(1)

import pyperclip
from helpers import get_selected_guids_list

guids = get_selected_guids_list()
pyperclip.copy(' '.join(guids))
