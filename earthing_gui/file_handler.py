import json
from .draw_objects import Rod, Strip, Mesh, Plate

def save_to_json(filepath, objects, parameters):
    data = {
        "parameters": parameters,
        "elements": []
    }

    for obj in objects:
        element_data = {
            "type": obj.__class__.__name__,
            "properties": obj.get_properties()
        }
        # Add specific data that might not be in get_properties but needed for reconstruction
        if isinstance(obj, Strip):
            element_data["points"] = obj.points

        data["elements"].append(element_data)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False

def load_from_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        parameters = data.get("parameters", {})
        objects = []

        for el in data.get("elements", []):
            el_type = el.get("type")
            props = el.get("properties", {})

            obj = None
            if el_type == "Rod":
                # Create with dummy coords, then set properties
                obj = Rod()
            elif el_type == "Strip":
                points = el.get("points", [])
                # Convert list of lists to list of tuples if needed
                points = [tuple(p) for p in points]
                # Default profile to flat if not specified (legacy support)
                profile = props.get("profile_type", "flat")
                obj = Strip(points=points)
                # Note: profile_type will be set by set_property loop below
            elif el_type == "Mesh":
                obj = Mesh()
            elif el_type == "Plate":
                obj = Plate()

            if obj:
                # Apply properties
                for k, v in props.items():
                    obj.set_property(k, v)
                objects.append(obj)

        return objects, parameters
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None, None
