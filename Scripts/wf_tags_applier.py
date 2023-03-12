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

    with WaapiClient() as client:

        # Récuère tout les objets spécifiés dans l'Actor-Mixer Hierarchy et les stocke dans la liste amhObjects 
        
        amhObjects = []
        for guid, name in walk_wproj(client,
                                     start_guids_or_paths='\\Actor-Mixer Hierarchy',
                                     properties=['id', 'name', 'notes'],
                                     types=['ActorMixer', 'RandomSequenceContainer', 'SwitchContainer', 'BlendContainer']):
            amhObjects.append([guid, name])

        # Récuère tout les objets spécifiés dans l'Interactive Music Hierarchy et les stocke dans la liste imhObjects 

        imhObjects = []
        for guid, name in walk_wproj(client,
                                     start_guids_or_paths='\\Interactive Music Hierarchy',
                                     properties=['id', 'name', 'notes'],
                                     types=['MusicSwitchContainer', 'MusicPlaylistContainer', 'MusicSegment', 'MusicTrack']):
            imhObjects.append([guid, name])        

        # Récupère le nom de tout les fichiers CSV présents dans le dossier Workflow et les stocke dans la liste csvFilesTitles

        csvFilesTitles = []
        for filename in csvFiles:
            title = os.path.basename(filename)
            csvFilesTitles.append(title)



# 2. Analyser les noms contenus dans les titres des fichiers CSV



# 3. Comparer les listes pour trouver des matchs

#       Si Tags dans les notes matchent un titre de fichier CSV alors :


   
# 4. Lire le contenu des fichiers CSV matchés et appliquer leur liste de paramètres au sein des containers matchés

# SETTINGS : 

#       Color
#       Inclusion  
#       Streaming Enabled
#       Prefetch Lengh
#       Conversion (Shareset)
#       Loudness Normalization
#       Make-up Gain
#       Center %
#       Speaker panning
#       Listener relative routing enabled
#       3D Spatialization
#       Attenuation (Shareset)  
#       3D Position
#       Hold listener orientation
#       Hold emitter position and orientation
#       Playback limit enabled
#       Ignore parent playback limit       
#       Limit sound instances to
#       Limitation scope
#       When limit is reached
#       When priority is equal
#       Virtual voice behavior
#       On return to physical voice
#       Playback priority
#       Use priority distance factor
#       Offset at max distance
#       Play type 
#       Avoid repeating last x played (Equation : nmbr de container enfant - 2)

#           Si certains paramètres sont laissés vide dans le CSV, ignorer le paramètre en question

#           Si un tag dans les notes contient  "#" (tag parent) alors appliquer la liste de paramètres du CSV correspondant à ce container ainsi qu'à tout les containers enfants dans sa hiérarchie

#           Si un tag dans les notes contient "." (tag enfant) alors ne rien faire (. = container enfant d'un parent donc paramètres déjà appliqués par le parent)

#           Si un tag dans les notes ne contient rien avant son nom (tag unique) alors n'appliquer les paramètres qu'à ce container



# 5. Check si tag parent et tag unique se répètent le long d'une hiérarchie (pour éviter d'appliquer les paramètres plusieurs fois)

#       Si un tag unique est présent dans un container enfant au sein de la hiérarchie d'un tag parent alors print un message : "Erreur tag doublon au sein de la hiérarchie et indiquer dans quel container" puis le supprimer

#       Si un tag unique est présent dans un container parent d'un container contenant un tag parent alors convertir le tag unique en tag parent et les tags sous jacents en tags enfant



# 6. Logique si tags enlevés des containers:

#       Si pas de tag parent plus haut dans la hiérarchie :
#           Remettre les containers concernés avec leur paramètres par défauts 

#       Si tag inhérités de parents plus haut dans la hiérarchie :
#           Utiliser ces tags pour paramétrer les containers concernés

#       Si les tags enlevés étaient des tags parents, enlever tout les tags enfants des notes



# 7. OVERRIDES :

#       Si lors de l'analyse des notes les tags suivants sont trouvés : 

# TAGS Locaux (juste le container visé):

#       EXC : N'appliquer aucun des paramètres du CSV à cet objet
#       !INC : override inclusion settings
#       !STR : override streaming settings
#       !CON : override conversion settings
#       !POS : override positionning settings
#       !PBL : override playback limiting settings
#       !PLT : override Play type settings

# TAGS Globaux (le container + la hiérarchie descendante après ce container):

#       #EXC : N'appliquer aucun des paramètres du CSV à cet objet
#       #!INC : override inclusion settings
#       #!STR : override streaming settings
#       #!CON : override conversion settings
#       #!POS : override positionning settings
#       #!PBL : override playback limiting settings
#       #!PLT : override Play type settings

except CannotConnectToWaapiException:
    showerror('Error', 'Could not establish the WAAPI connection. Is the Wwise Authoring Tool running?')
except RuntimeError as e:
    showerror('Error', f'{e}')
except Exception as e:
    import traceback

    showerror('Error', f'{e}\n\n{traceback.format_exc()}')
finally:
    tk.destroy()
