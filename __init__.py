import json
import json
import traceback
from swagger_2 import Swagger2Parser
def read_json(path):
    #'vocabulary.json'
    with open(path) as data_file:
        data = json.load(data_file)
    return data


def init_by_file(path_to_file):

    try:
        data_swagger = read_json(path_to_file)
        data_swagger['swagger']
        Swagger2Parser(data_swagger)
    except KeyError:
        traceback.print_exc()
    except FileNotFoundError:
        print('файл не найден')
    except IOError:
        print('проблемы при чтении файла')


if __name__ == '__main__':
    init_by_file('swagger.json')
