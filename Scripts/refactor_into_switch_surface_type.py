if __name__ != '__main__':
    print(f'error: {__file__} should not be imported, aborting script')
    exit(1)

import tkinter
from functools import reduce
from tkinter.messagebox import showinfo, showerror

from thefuzz import fuzz
from waapi import WaapiClient, CannotConnectToWaapiException
from waapi_helpers import *

from helpers import *

tk = tkinter.Tk()
tk.withdraw()

SURFACE_TYPE_SWITCH_GROUP_NAME = 'Surface_Type'


def get_switches_for_group_surface_type(wclient):
    sw_name_to_guid = dict()
    for gr_guid, gr_name in walk_wproj(wclient, '\\Switches', ['id', 'name'], 'SwitchGroup'):
        if gr_name == SURFACE_TYPE_SWITCH_GROUP_NAME:
            for sw_guid, sw_name in walk_wproj(
                    wclient, gr_guid, ['id', 'name'], 'Switch'):
                sw_name_to_guid[sw_name] = sw_guid
            break
    return sw_name_to_guid


def infer_obj_assignments(selected_guids, switches):
    obj_assignments = []
    for obj_guid, obj_name in zip(selected_guids, obj_names):
        scores = [(fuzz.partial_ratio(obj_name, sw_name), sw_name, sw_guid)
                  for sw_name, sw_guid in switches.items()]
        max_score = reduce(lambda a, b: a if (a[0] > b[0]) else b, scores)
        sw_guid = max_score[2]
        obj_assignments.append((obj_guid, sw_guid))
    return obj_assignments


try:
    selected_guids = get_selected_guids_list()

    if len(selected_guids) == 0:
        showinfo('Info', 'No objects were selected')
        exit(0)

    with WaapiClient() as client:
        obj_names = [get_name_of_guid(client, guid)
                     for guid in selected_guids]
        if None in obj_names:
            raise RuntimeError('Could not get names of all selected objects')

        switches = get_switches_for_group_surface_type(client)
        if len(switches) == 0:
            raise RuntimeError("Could not find switches for group 'Surface_Type'")
        parent_obj = get_parent_guid(client, selected_guids[0])
        if parent_obj is None:
            raise RuntimeError(f'{selected_guids[0]} has no parent')

        begin_undo_group(client)

        switch_obj = create_objects(client, parent_obj, 'RENAME_ME', 'SwitchContainer')[0]
        if switch_obj is not None:
            set_reference(client, switch_obj, 'SwitchGroupOrStateGroup',
                          f'SwitchGroup:{SURFACE_TYPE_SWITCH_GROUP_NAME}')
        else:
            # roll back changes if the script failed in the middle of operation
            end_undo_group(client, 'Refactor Into Surface_Type Switch')
            perform_undo(client)
            raise RuntimeError('Could not create switch container under ' +
                               str(get_name_of_guid(client, parent_obj)))

        # reparent selected objects
        for guid in selected_guids:
            res = move_object(client, guid, switch_obj)
            if res is None:
                end_undo_group(client, 'Refactor Into Surface_Type Switch')
                perform_undo(client)
                raise RuntimeError(
                    f'Could not move object {guid} to parent {switch_obj}. '
                    'All changes have been reverted.')

        obj_assignments = infer_obj_assignments(selected_guids, switches)

        for obj_guid, sw_guid in obj_assignments:
            client.call('ak.wwise.core.switchContainer.addAssignment',
                        {'child': obj_guid, 'stateOrSwitch': sw_guid})

        end_undo_group(client, 'Refactor Into Surface_Type Switch')

except CannotConnectToWaapiException:
    showerror('Error', 'Could not establish the WAAPI connection. Is the Wwise Authoring Tool running?')
except RuntimeError as e:
    showerror('Error', f'{e}')
except Exception as e:
    import traceback

    showerror('Error', f'{e}\n\n{traceback.format_exc()}')
finally:
    tk.destroy()
