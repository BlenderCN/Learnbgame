import json
import os

component_data = None

def get_component_info():
    """
    Get component info for realxtend.
    """
    global component_data
    if component_data:
        return component_data
    b2rex_path = os.path.dirname(os.path.dirname(__file__))
    b2rex_path = os.path.dirname(b2rex_path)

    info_f = open(os.path.join(b2rex_path, 'rex_com.json'))
    info_text = info_f.read()
    info_f.close()

    info = json.loads(info_text)
    component_data = info['Components']
    return component_data

