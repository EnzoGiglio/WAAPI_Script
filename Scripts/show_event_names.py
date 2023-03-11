if __name__ != '__main__':
    print(f'error: {__file__} should not be imported, aborting script')
    exit(1)

import tkinter
from tkinter.messagebox import showerror, showinfo
from waapi import WaapiClient, CannotConnectToWaapiException
from waapi_helpers import *

tk = tkinter.Tk()
tk.withdraw()

try:
    events = []
    with WaapiClient() as client:
        for guid, name in walk_wproj(client,
                                     start_guids_or_paths='\\Events',
                                     properties=['id', 'name'],
                                     types=['Event']):
            events.append(name)
    showinfo('Event names', '\n'.join(events))

except CannotConnectToWaapiException:
    showerror('Error', 'Could not establish the WAAPI connection. Is the Wwise Authoring Tool running?')
except RuntimeError as e:
    showerror('Error', f'{e}')
except Exception as e:
    import traceback

    showerror('Error', f'{e}\n\n{traceback.format_exc()}')
finally:
    tk.destroy()
