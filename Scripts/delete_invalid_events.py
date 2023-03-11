if __name__ != '__main__':
    print(f'error: {__file__} should not be imported, aborting script')
    exit(1)

import tkinter
from tkinter.messagebox import showinfo, showerror, askyesno
from waapi import WaapiClient, CannotConnectToWaapiException
from waapi_helpers import *

tk = tkinter.Tk()
tk.withdraw()

try:
    action_types_to_check = {1, 2, 7, 9, 34, 37, 41}
    events_to_delete = []

    with WaapiClient() as client:
        num_obj_visited = 0
        for event_guid, in walk_wproj(client, '\\Events', properties=['id'], types=['Event']):
            print(f'Visited: {num_obj_visited}, To delete: {len(events_to_delete)}', end='\r')
            num_valid_actions = 0
            for action_id, action_type, target in walk_wproj(client, event_guid,
                                                             properties=['id', 'ActionType', 'Target'],
                                                             types=['Action']):
                if action_type in action_types_to_check:
                    if does_object_exist(client, target['id']):
                        num_valid_actions += 1
                else:
                    num_valid_actions += 1

            if num_valid_actions == 0:
                events_to_delete.append(event_guid)

        num_events_to_delete = len(events_to_delete)
        if num_events_to_delete > 0 \
                and askyesno('Confirm',
                             f'{num_events_to_delete} events are going to be deleted. Proceed?'):
            begin_undo_group(client)
            for event_guid in events_to_delete:
                delete_object(client, event_guid)
            end_undo_group(client, 'Delete Invalid Events')  # capitalized as per Wwise convention
            showinfo('Success', f'{len(events_to_delete)} were deleted')

except CannotConnectToWaapiException:
    showerror('Error', 'Could not establish the WAAPI connection. Is the Wwise Authoring Tool running?')
except RuntimeError as e:
    showerror('Error', f'{e}')
except Exception as e:
    import traceback

    showerror('Error', f'{e}\n\n{traceback.format_exc()}')
finally:
    tk.destroy()
