if __name__ != '__main__':
    print(f'error: {__file__} should not be imported, aborting script')
    exit(1)

import tkinter
from tkinter.messagebox import showinfo, showerror
from waapi import WaapiClient, CannotConnectToWaapiException
from waapi_helpers import *
from helpers import *

import pandas as pd
from pprint import pprint 

tk = tkinter.Tk()
tk.withdraw()

types = 'Event'

# Read Excel file and create a dataframe with what is inside
dfEvents = pd.read_excel("C:/Users/enzog/Desktop/WAAPI_Scripts/Workflow_CSV_Tags/Sound List.xlsx", sheet_name="Event List")

# Print Excel result
# print(dfEvents.head())

# Use Excel sheet 'Event' column to list events names to create in Wwise
eventsToCreateInWwise = dfEvents["Event Name"].tolist()

# Print list result
# print(eventsToCreateInWwise)

try:

    with WaapiClient() as client:
        # NOTE: client will automatically disconnect at the end of the scope
        
        # List events name already existing in Wwise
        alreadyExistingEvents = [eventName[0] for eventName in walk_wproj(client,
                                        start_guids_or_paths='\\Events',
                                        properties=['name'],
                                        types=['Event'])]
 
        # Compare names of events to create with already existing events in Wwise  
        for eventToBeCreated in eventsToCreateInWwise:
            if eventToBeCreated in alreadyExistingEvents:

                #Print in a dedicated window interface
                pprint("Events already exists, will merge:" + eventToBeCreated)

        # Create events in Wwise from names in eventsToCreateInWwise list
        for eventToBeCreated in eventsToCreateInWwise:
            client.call("ak.wwise.core.object.create", {
                    'parent': "\\Events\\Default Work Unit",
                    'type': 'Folder',
                    'name': 'WAAPI',
                    'onNameConflict': 'merge',
                    'children': [
                        {
                            'type': 'Event',
                            'name': eventToBeCreated
                        }
                    ]
                }
            )
        
        # Print in a dedicated window interface
        pprint("Events has been created inside WAAPI folder in Default Work Unit.")          

except CannotConnectToWaapiException:
    showerror('Error', 'Could not establish the WAAPI connection. Is the Wwise Authoring Tool running?')
except RuntimeError as e:
    showerror('Error', f'{e}')
except Exception as e:
    import traceback

    showerror('Error', f'{e}\n\n{traceback.format_exc()}')
finally:
    tk.destroy()