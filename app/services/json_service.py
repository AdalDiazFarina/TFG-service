import json

def load_data(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
    except FileNotFoundError as e:
        print(f"Error al cargar el fichero: {e}")
        data = []
    except json.JSONDecodeError as e:
        print(f"Error al parsear el JSON: {e}")
        data = []
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        data = []
    return data

def save_data(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def create_object(name, description, model):
    return {'name': name, 'description': description, 'model': model}

def create_operation(start, end, price, total, profit, period):
    return {'start': start, 'end': end, 'price': price, 'total': total, 'profit': profit, 'period': period}

def add_operation_to_json(start, end, price, total, profit, period, filename):
    data = load_data(filename)
    new_object = create_operation(start, end, price, total, profit, period)
    data.append(new_object)
    save_data(data, filename)

def object_exists(new_object, data):
    for obj in data:
        if obj['name'] == new_object['name']:
            return True
    return False

def add_object_to_json(name, description, model, filename):
    data = load_data(filename)
    new_object = create_object(name, description, model)
    if not object_exists(new_object, data):
        data.append(new_object)
        save_data(data, filename)
    else:
        print("The object already exists in the JSON file.")

def update_json_values(new_values, filename):
    data = load_data(filename)
    if data:
        for key, value in new_values.items():
            if key in data[0]:
                data[0][key] = value
            else:
                print(f"The key '{key}' does not exist in the JSON data.")
        save_data(data, filename)
    else:
        print("Could not load any data from the JSON file.")