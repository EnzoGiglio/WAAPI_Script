if __name__ != '__main__':
    print(f'error: {__file__} should not be imported, aborting script')
    exit(1)

import tkinter
from tkinter.messagebox import showinfo, showerror
from waapi import WaapiClient, CannotConnectToWaapiException
from waapi_helpers import *
from helpers import *

# add your imports here

tk = tkinter.Tk()
tk.withdraw()

try:
    with WaapiClient() as client:
        # replace this block with your stuff
        guid = get_guid_of_path(client, '\\Actor-Mixer Hierarchy')
        showinfo('Info!', f'Actor-Mixer Hierarchy GUID is {guid}!')

except CannotConnectToWaapiException:
    showerror('Error', 'Could not establish the WAAPI connection. Is the Wwise Authoring Tool running?')
except RuntimeError as e:
    showerror('Error', f'{e}')
except Exception as e:
    import traceback

    showerror('Error', f'{e}\n\n{traceback.format_exc()}')
finally:
    tk.destroy()
