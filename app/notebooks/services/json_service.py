import json

def load_data(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []
    return data

def save_data(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def create_object(name, description):
    return {'name': name, 'description': description}

def object_exists(new_object, data):
    for obj in data:
        if obj['name'] == new_object['name']:
            return True
    return False

def add_object_to_json(name, description, filename):
    data = load_data(filename)
    new_object = create_object(name, description)
    if not object_exists(new_object, data):
        data.append(new_object)
        save_data(data, filename)
    else:
        print("El objeto ya existe en el archivo JSON.")
