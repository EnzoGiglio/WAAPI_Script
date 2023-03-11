import shutil

if __name__ != '__main__':
    print(f'error: {__file__} should not be imported, aborting script')
    exit(1)

import tkinter
from tkinter.messagebox import showinfo, showerror, showwarning, askyesno
from waapi import WaapiClient, CannotConnectToWaapiException
from waapi_helpers import *
from helpers import *
from xml.etree import ElementTree

from glob import glob


def normalize_path(path):
    return os.path.normpath(os.path.realpath(path))


def find_originals_dir(client) -> str:
    wproj_dir = os.path.join(os.path.dirname(default_wu_path), '..')
    wproj_file = None

    for wproj in glob(os.path.join(wproj_dir, '*.wproj')):
        wproj_file = normalize_path(wproj)
        break

    if wproj_file is None:
        raise RuntimeError('Could not find a .wproj file')

    originals_rel_path = 'Originals'

    tree = ElementTree.parse(wproj_file)
    root = tree.getroot()
    for entry in root.iter('MiscSettingEntry'):
        if entry.get('Name') == 'Originals':
            originals_rel_path = normalize_path(os.path.join(wproj_dir, entry.text.strip()))

    return normalize_path(os.path.join(wproj_dir, originals_rel_path))


def scan_origs_dir(origs_dir) -> set:
    wavs = set()
    # for subdir in ['bkk']:
    #     for wav in glob(os.path.join(orig_dir, subdir, '**', '*.wav')):
    #         wavs.add(normalize_path(wav))
    return wavs


tk = tkinter.Tk()
tk.withdraw()

try:
    with WaapiClient() as client:
        default_wu_path, = get_object(client, '\\Actor-Mixer Hierarchy\\Default Work Unit', 'filePath')
        origs_dir = find_originals_dir(default_wu_path)

        wavs_in_origs = set()
        wavs_in_wproj = set()

        for subdir in 'SFX', 'Voices':
            for wav_path in glob(os.path.join(origs_dir, subdir, '**', '*.wav'),
                                 recursive=True):
                wavs_in_origs.add(normalize_path(wav_path))

        for guid, wav_path in walk_wproj(
                client,
                start_guids_or_paths=['\\Actor-Mixer Hierarchy', '\\Interactive Music Hierarchy'],
                properties=['id', 'originalWavFilePath'],
                types=['AudioFileSource']
        ):
            wavs_in_wproj.add(normalize_path(wav_path))

        wavs_to_remove = wavs_in_origs.difference(wavs_in_wproj)
        files_left = len(wavs_to_remove)

        if files_left > 0 and askyesno(
                'Confirm', f'You are about to delete {files_left} files. Proceed?'):
            for wav_path in wavs_to_remove:
                try:
                    os.remove(wav_path)
                    files_left -= 1
                except PermissionError:
                    pass

            if files_left == 0:
                showinfo('Success',
                         f'{len(wavs_to_remove)} files were deleted')
            else:
                showwarning('Warning',
                            f'{files_left} files could not have been deleted. '
                            f'Are they open in some apps?')

except CannotConnectToWaapiException:
    showerror('Error', 'Could not establish the WAAPI connection. Is the Wwise Authoring Tool running?')
except RuntimeError as e:
    showerror('Error', f'{e}')
except Exception as e:
    import traceback

    showerror('Error', f'{e}\n\n{traceback.format_exc()}')
finally:
    tk.destroy()
