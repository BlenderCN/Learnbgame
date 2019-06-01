def peak(minimum, width, base, peak):
    return {
        'peak': {
            'peak_min': minimum,
            'peak_width': width,
            'base_value': base,
            'peak_value': peak
        }
    }
    
def blackbody(temp, gain):
    return {
        'blackbody': {
            'temperature': temp,
            'gain': gain,
        }
    }

def rgb(rgb, gamma=[1.0], gain=[1.0]):        # TODO: verify correct gamma value
    return {
        'rgb': {
            'rgb': rgb,
            'gamma': gamma,
            'gain': gain
        }
    }
    
def uniform(value):
    return {
        'uniform': {
            'value': value
        }
    }

def regular_tabulated(start, end, values=[]):
    num_values = len(values)
    
    return {
        'regular_tabulated': {
            'start_wavelength': start,
            'end_wavelength': end,
            'num_values': [num_values],
            'values': values
        }
    }