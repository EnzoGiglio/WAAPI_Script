if __name__ != '__main__':
    print(f'error: {__file__} should not be imported, aborting script')
    exit(1)

import tkinter
from tkinter.messagebox import showinfo, showerror
from waapi import WaapiClient, CannotConnectToWaapiException
from waapi_helpers import *
from helpers import *

import glob
csvFiles = glob.glob('C:/Users/enzog/Desktop/WAAPI_Scripts/Workflow_CSV_Tags/*.csv')

tk = tkinter.Tk()
tk.withdraw()


try:

# Récuère tout les objets spécifiés dans l'Actor-Mixer Hierarchy et les stocke dans la liste amhObjects 

    with WaapiClient() as client:
        
        amhObjects = []
        for guid, name in walk_wproj(client,
                                     start_guids_or_paths='\\Actor-Mixer Hierarchy',
                                     properties=['id', 'name'],
                                     types=['ActorMixer', 'RandomSequenceContainer', 'SwitchContainer', 'BlendContainer']):
            amhObjects.append([guid, name])

# Récuère tout les objets spécifiés dans l'Interactive Music Hierarchy et les stocke dans la liste imhObjects 

        imhObjects = []
        for guid, name in walk_wproj(client,
                                     start_guids_or_paths='\\Interactive Music Hierarchy',
                                     properties=['id', 'name'],
                                     types=['MusicSwitchContainer', 'MusicPlaylistContainer', 'MusicSegment', 'MusicTrack']):
            imhObjects.append([guid, name])

# Récupère le nom de tout les fichiers CSV présents dans le dossier Workflow et les stocke dans la liste csvFilesTitles

    csvFilesTitles = []
    for filename in csvFiles:
        title = os.path.basename(filename)
        csvFilesTitles.append(title)

# Recherche de match entre les noms contenus dans amhObjects et csvFilesTitles et les stocke dans la liste foundObjects
    
    foundObjects = []
    for guid, name in amhObjects:
        for filename in csvFilesTitles:
            if name in filename:
                print("Matchs found: " + name)
                foundObjects.append((guid, name)) ### PB ne trouve pas 2D dans FOL_2D ###

# Quand match trouvé, reporte les noms des csvFilesTitles dans les notes des objets wwise correspondant

    for guid, name in foundObjects:
        client.call("ak.wwise.core.object.setNotes", {
                'object': guid,
                'value': "[toto]"
                })  
        print('cestok')

    
except CannotConnectToWaapiException:
    showerror('Error', 'Could not establish the WAAPI connection. Is the Wwise Authoring Tool running?')
except RuntimeError as e:
    showerror('Error', f'{e}')
except Exception as e:
    import traceback

    showerror('Error', f'{e}\n\n{traceback.format_exc()}')
finally:
    tk.destroy()
