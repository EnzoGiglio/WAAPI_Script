if __name__ != '__main__':
    print(f'error: {__file__} should not be imported, aborting script')
    exit(1)

import tkinter
from tkinter.messagebox import showinfo, showerror
from waapi import WaapiClient, CannotConnectToWaapiException
from waapi_helpers import *
from helpers import *

tk = tkinter.Tk()
tk.withdraw()

try:
    with WaapiClient() as client:
        num_reset_faders = 0
        selected_guid = get_selected_guid()

        for obj_id, obj_type, obj_notes in walk_wproj(client, selected_guid,
                                                      properties=['id', 'type', 'notes']):
            if '@ignore' in obj_notes:
                continue

            prop_name = 'Volume'
            if obj_type == 'Bus' or obj_type == 'AuxBus':
                prop_name = 'BusVolume'

            cur_volume = get_property_value(client, obj_id, prop_name)
            if cur_volume is not None and cur_volume != 0:
                set_property_value(client, obj_id, prop_name, 0)
                num_reset_faders += 1

        showinfo('Info', f'{num_reset_faders} faders were reset')

except CannotConnectToWaapiException:
    showerror('Error', 'Could not establish the WAAPI connection. Is the Wwise Authoring Tool running?')
except RuntimeError as e:
    showerror('Error', f'{e}')
except Exception as e:
    import traceback

    showerror('Error', f'{e}\n\n{traceback.format_exc()}')
finally:
    tk.destroy()
