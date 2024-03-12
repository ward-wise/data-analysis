STANDARD_CATEGORY = {
    "pedestrian": "Pedestrian Infrastructure",
    "bump outs": "Pedestrian Infrastructure",
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
    "turn arrow": "Street Redesign",
    "street speed hump menu": "Street Redesign",
    "pavement markings": "Street Redesign",
    "traffic circle": "Street Redesign",
    "cul-de-sac": "Street Redesign",
    "diagnol parking": "Street Redesign",
    "sidewalk": "Sidewalk Repair",
    "pod camera": "Police Cameras",
    "park": "Parks",
    "playground": "Parks",
    "garden": "Parks",
    "viaduct": "Viaducts",
}


def get_menu_category(item):
    item = item.lower()
    if "pedestrian" in item or "bump outs" in item:
        return "Pedestrian Infrastructure"
    elif "bicycle" in item or "bike" in item or "neighborhood greenway" in item:
        return "Bicycle Infrastructure"
    elif "light" in item:
        return "Lighting"
    elif (
        "street resurfacing" in item
        or "street speed hump replacement" in item
        or "curb & gutter" in item
    ):
        return "Street Resurfacing"
    elif "alley" in item:
        return "Alleys"
    elif "miscellaneous cdot projects" in item:
        return "Misc. CDOT"
    elif "mural" in item or "public art" in item or "tree planting" in item:
        return "Beautification"
    elif (
        "turn arrow" in item
        or "street speed hump menu" in item
        or "pavement markings" in item
        or "traffic circle" in item
        or "cul-de-sac" in item
        or "diagnol parking" in item
    ):
        return "Street Redesign"
    elif "sidewalk" in item:
        return "Sidewalk Repair"
    elif "pod camera" in item:
        return "Police Cameras"
    elif "park" in item or "playground" in item or "garden" in item:
        return "Parks"
    elif "viaduct" in item:
        return "Viaducts"
    else:
        return "Misc."
