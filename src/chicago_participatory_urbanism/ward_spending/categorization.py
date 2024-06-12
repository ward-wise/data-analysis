STANDARD_CATEGORY = {
    "pedestrian": "Pedestrian Infrastructure",
    "bump outs": "Pedestrian Infrastructure",
    "guardrail" : "Pedestrian Infrastructure",
    "bicycle": "Bicycle Infrastructure",
    "bike": "Bicycle Infrastructure",
    "neighborhood greenway": "Bicycle Infrastructure",
    "light": "Lighting",
    "street resurfacing": "Street Resurfacing",
    "street speed hump replacement": "Street Resurfacing",
    "curb & gutter": "Street Resurfacing",
    "alley": "Alleys",
    "miscellaneous cdot projects": "Misc. CDOT",
    "mural": "Beautification",
    "public art": "Beautification",
    "tree planting": "Beautification",
    "school" : "Education",
    "arts program" : "Education",
    "library" : "Education",
    "cps" : "Education",
    "turn arrow": "Street Redesign",
    "street speed hump menu": "Street Redesign",
    "pavement markings": "Street Redesign",
    "traffic circle": "Street Redesign",
    "cul-de-sac": "Street Redesign",
    "diagonal parking": "Street Redesign",
    "sidewalk": "Sidewalk Repair",
    "pod camera": "Police Cameras",
    "ptz camera": "Police Cameras",
    "oemc camera project": "Police Cameras",
    "lpr": "Police Cameras",
    "fly dumping camera": "Police Cameras",
    "park": "Parks",
    "playground": "Parks",
    "garden": "Parks",
    "viaduct": "Viaducts",
}

def get_menu_category(item):
    item = item.lower()
    if ("pedestrian" in item 
        or "bump outs" in item
        or "state law stop" in item
        or "guardrail" in item
        or "bollard" in item):
        return "Pedestrian Infrastructure"
    elif ("bicycle" in item
          or "bike" in item
          or "neighborhood greenway" in item):
        return "Bicycle Infrastructure"
    elif "light" in item:
        return "Lighting"
    #"resurfac" is used because it will pick up resurface or resurfacing.
    elif("resurfac" in item and "street" in item 
         or "street" in item and "speed" in item and "hump" in item
         or "curb" in item and "gutter" in item):
        return "Street Resurfacing"
    elif "alley" in item:
        return "Alleys"
    elif "miscellaneous" in item and "cdot" in item:
        return "Misc. CDOT"
    elif ("mural" in item
          or "public art" in item
          or "tree planting" in item):
        return "Beautification"
    elif ("turn arrow" in item 
          or "street speed hump menu" in item 
          or "pavement markings" in item 
          or "traffic circle" in item 
          or "cul-de-sac" in item
          or "diagonal parking" in item):
        return "Street Redesign"
    elif ("school" in item
          or "cps" in item
          or "library" in item
          or "elementary" in item
          or "art" in item and "program" in item):
        return "Education"
    elif ("traffic" in item
          or "speed" in item
          or  "bus" in item and "pad" in item):
        return "Traffic Infrastructure"
    elif "sidewalk" in item:
        return "Sidewalk Repair"
    elif ("pod" in item and "camera" in item
          or "lpr" in item
          or "dumping" in item and "camera" in item
          or "ptz" in item and "camera" in item
          or "oemc" in item and "camera" in item
          or "high definition" in item and "camera" in item):
        return "Police Cameras"
    elif ("park" in item
          or "playground" in item
          or "garden" in item):
        return "Parks"
    elif ("viaduct" in item):
        return "Viaducts"
    else:
        return "Misc."
