'''updates all the paths and folders with the current code'''
import os
'''access the wnvironment variable'''

try:
    riggingToolRoot=os.environ['RIGGING_TOOL_ROOT']
except:
    print("rigging tool not configured")
else:
    import sys
    print riggingToolRoot
    path = riggingToolRoot+ "/Modules"

    if not path in sys.path:
        sys.path.append(path)

    import System.blueprint_UI as blueprint_UI
    reload(blueprint_UI)
    UI=blueprint_UI.Blueprint_UI()
