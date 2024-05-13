#Extracts all the matching keys and shows the path in a nested dictionary format (Especially helpful while traversing through watson discovery) and shares the paths in the form of list
def find_path(dictionary, key, path=None):
    if path is None:
        path = []
    all_paths = []
    for k, v in dictionary.items():
        current_path = path + [k]
        if k == key:
            all_paths.append(current_path)
        if isinstance(v, dict):
            nested_paths = find_path(v, key, current_path)
            all_paths.extend(nested_paths)
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    nested_paths = find_path(item, key, current_path + [i])
                    all_paths.extend(nested_paths)
    return all_paths


#Providing the value of the key for dictionary. Each path obtained from above must be pased to get the value
'''
For example:
ls = find_path(nested_dict, 'subsubsubkey12')
The result is

[['key2', 'subkey3', 'subsubkey6', 'subsubsubkey12']]

Since the nested dictionary has only 1 match, we use

get_value_by_path(nested_dict, find_path(nested_dict, 'subsubsubkey12')[0])
'''


def get_value_by_path(dictionary, path):
    try:
        current = dictionary
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
                current = current[key]
            else:
                raise KeyError(f"Invalid key or index {key} in path")
        return current
    except (KeyError, IndexError, TypeError):
        # Handle exceptions if the path is not valid
        return None