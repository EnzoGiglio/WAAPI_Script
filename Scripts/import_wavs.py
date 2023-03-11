if __name__ != '__main__':
    print(f'error: {__file__} should not be imported, aborting script')
    exit(1)

import os
import io
import tkinter
from glob import glob
from tkinter.messagebox import showinfo, showerror, askyesno
from tkinter.filedialog import askdirectory
from typing import List, Optional, Tuple, Set, Dict
from waapi import WaapiClient, CannotConnectToWaapiException
from waapi_helpers import *
from helpers import *
from wav_importer import *

tk = tkinter.Tk()
tk.withdraw()


def get_template_and_slot_names(client: WaapiClient, template_guid: str) -> Tuple[ImportTemplate, Set[str]]:
    sel_notes, = get_object(client, template_guid, 'notes')
    import_tpl = ImportTemplate.from_notes(sel_notes)
    if not import_tpl.is_valid():
        raise RuntimeError('Selected object does not appear to be an Import_Template')
    slot_names = set()
    for notes, in walk_wproj(client, template_guid, 'notes'):
        import_slot = ImportSlot.from_notes(notes)
        if import_slot.is_valid():
            slot_names.add(import_slot.name)
    if len(slot_names) == 0:
        raise RuntimeError('Selected import template does not appear to have any import slots')
    return import_tpl, slot_names


def scan_wav_file_names(wav_files: List[str], import_tpl: ImportTemplate) -> Dict[str, Dict[str, List[str]]]:
    objects_to_import = dict()  # object name → (slot name → wav list)
    for file_name in wav_files:
        wav = ImportedWav.from_filename(file_name)
        if wav.is_valid() and \
                wav.template_name == import_tpl.name and \
                wav.slot_name in slot_names:
            if wav.obj_name not in objects_to_import:
                objects_to_import[wav.obj_name] = dict()
            slots_dict = objects_to_import.get(wav.obj_name, dict())
            if wav.slot_name not in slots_dict:
                slots_dict[wav.slot_name] = []
            wavs_array = slots_dict.get(wav.slot_name, [])
            wavs_array.append(file_name)
    return objects_to_import


def find_slot_guids(client: WaapiClient, obj_guid: str) -> Dict[str, List[str]]:
    slot_guids = dict()
    for guid, notes, in walk_wproj(client, obj_guid, ['id', 'notes']):
        import_slot = ImportSlot.from_notes(notes)
        if import_slot.is_valid():
            if import_slot.name not in slot_guids:
                slot_guids[import_slot.name] = []
            guids = slot_guids.get(import_slot.name, [])
            guids.append(guid)
    return slot_guids


##########################################
try:
    template_guid = get_selected_guid()
    if template_guid is None:
        raise RuntimeError('Nothing was selected')

    with WaapiClient() as client:
        import_tpl, slot_names = get_template_and_slot_names(client, template_guid)
        wav_dir = askdirectory(title='Please, select a folder with Wave files to import')
        wav_files = [w for w in glob(os.path.join(wav_dir, '*.wav'))]
        objects_to_import = scan_wav_file_names(wav_files, import_tpl)

        if len(objects_to_import) > 0:
            sb = io.StringIO()
            sb.write('The following files were found. Proceed to import them?\n')
            for obj_name, obj_slots in objects_to_import.items():
                sb.write(f'\n{obj_name}\n')
                for slot_name, slot_wavs in obj_slots.items():
                    sb.write(f'{slot_name}: {len(slot_wavs)} file(s)\n')
            if not askyesno('Confirm', sb.getvalue()):
                exit(0)
        else:
            raise RuntimeError('Could not find any Wave files that match the current template naming scheme')

        # ------------------------------------------
        begin_undo_group(client)
        try:
            parent_guid = get_parent_guid(client, template_guid)
            for obj_name, obj_slots in objects_to_import.items():
                obj_guid = copy_object(client, template_guid, parent_guid,
                                       on_name_conflict='rename')
                if obj_guid is None:
                    raise RuntimeError('Could not copy a template object')

                obj_name_formatted = f'{import_tpl.name}_{obj_name}'
                rename_res = client.call('ak.wwise.core.object.setName', {
                    'object': obj_guid,
                    'value': obj_name_formatted
                })
                if rename_res is None:
                    raise RuntimeError(f'The object with name {obj_name_formatted} already exists')

                client.call('ak.wwise.core.object.setNotes', {
                    'object': obj_guid,
                    'value': ImportedHierarchy(template_guid).to_notes()
                })

                slot_guids = find_slot_guids(client, obj_guid)
                assert len(slot_guids) > 0

                for slot_name, slot_wavs in obj_slots.items():
                    for guid in slot_guids[slot_name]:
                        import_audio(client, guid, slot_wavs)

        except Exception:
            end_undo_group(client, 'Import Wave Files')
            perform_undo(client)
            raise
        end_undo_group(client, 'Import Wave Files')

##########################################
except CannotConnectToWaapiException:
    showerror('Error', 'Could not establish the WAAPI connection. Is the Wwise Authoring Tool running?')
except RuntimeError as e:
    showerror('Error', f'{e}')
except Exception as e:
    import traceback

    showerror('Error', f'{e}\n\n{traceback.format_exc()}')
finally:
    tk.destroy()
