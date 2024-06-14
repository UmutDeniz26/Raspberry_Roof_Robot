import json
import time

def get_distance(output_path):
    with open(output_path, 'r') as file:
        data = file.readlines()
        try:
            return str_to_json(data[-1])
        except:
            time.sleep(0.2)
            try:
                return str_to_json(data[-1])
            except:
                return {'error': 'No data found'}
def get_max_distance(output_path):
    try:
        objects = get_distance(output_path)['Objects']
    except:
        return 0
    if len(objects) == 0:
        return 0
    return max(objects, key=lambda x: x['D'])['D']


def str_to_json(data):
    return json.loads(data)

output_path = 'Modules/Distance_Sensor/VL53L3CX_rasppi/vl53l3cx_ranging_output.txt'

if __name__ == '__main__':
    print(get_distance(output_path))
    print(get_max_distance(output_path))