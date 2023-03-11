if __name__ != '__main__':
    print(f'error: {__file__} should not be imported, aborting script')
    exit(1)

import configparser
import tkinter
from tkinter.messagebox import askyesno, showerror, showinfo
from waapi import WaapiClient, CannotConnectToWaapiException
from waapi_helpers import *
from helpers import *

# add your imports here

tk = tkinter.Tk()
tk.withdraw()

try:
    with WaapiClient() as client:
        dwu_notes = get_property_value(
            client, '\\Actor-Mixer Hierarchy\\Default Work Unit', 'notes')
        if dwu_notes is None:
            raise RuntimeError('Could not fetch notes from Default Work Unit')

        config = configparser.ConfigParser()
        config.read_string(dwu_notes)
        if 'Enable_Streaming_For_SFX' not in config:
            raise RuntimeError('Could not find [Enable_Streaming_For_SFX] config section')

        stream_config = config['Enable_Streaming_For_SFX']

        objects_to_modify = []
        for guid, name, max_dur_src in walk_wproj(client, '\\Actor-Mixer Hierarchy',
                                                  ['id', 'name', 'maxDurationSource'], 'Sound'):
            if max_dur_src is None:
                continue
            # trimmedDuration is in seconds, not milliseconds
            is_long_sound = max_dur_src['trimmedDuration'] > stream_config.getfloat('If_Longer_Than')
            if is_long_sound:
                objects_to_modify.append(guid)

        if len(objects_to_modify) > 0 and \
                askyesno('Confirm',
                         f'The tool is about to modify properties of {len(objects_to_modify)} objects. Proceed?'):
            begin_undo_group(client)
            for guid in objects_to_modify:
                set_property_value(client, guid, 'IsStreamingEnabled', True)
                set_property_value(client, guid, 'IsNonCachable', True)  # stream_config.getboolean('Non_Cachable'))
                set_property_value(client, guid, 'IsZeroLantency', stream_config.getboolean('Zero_Latency'))
                set_property_value(client, guid, 'PreFetchLength', stream_config.getint('Prefetch_Length_Ms'))
            end_undo_group(client, 'Bulk Set SFX Streaming')
            showinfo('Success', f'{len(objects_to_modify)} objects were updated')
        else:
            showinfo('Success', f'No changes have been made')

except CannotConnectToWaapiException:
    showerror('Error', 'Could not establish the WAAPI connection. Is the Wwise Authoring Tool running?')
except RuntimeError as e:
    showerror('Error', f'{e}')
except Exception as e:
    import traceback

    showerror('Error', f'{e}\n\n{traceback.format_exc()}')
finally:
    tk.destroy()
