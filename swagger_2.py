import sys
from swagger_parser import InterfeceSwaggerParser
import json
import os
# from pprint import pprint


class Swagger2Parser(InterfeceSwaggerParser):
    PATH_TO_DIR = os.getcwd()
    TITLE_MAIN_DIR = '/tests'

    @staticmethod
    def _read_json(path):
        with open(path) as data_file:
            data = json.load(data_file)
        return data

    @staticmethod
    def _stop_parse():
        print('в файле нет неободимых данных для построения тестов')

    @staticmethod
    def ensure_dir(directory):
        try:
            os.stat(directory)
        except FileNotFoundError:
            # traceback.print_exc()
            os.mkdir(directory)

    @staticmethod
    def parse_schema(data, models):
        # print(4)

        def parse_data(name):
            res = []
            for p in models[name]['properties'].keys():
                if models[name]['properties'][p].get('type', False):
                    tmp = {
                        'name': p,
                        'type': models[name]['properties'][p]['type']
                    }
                    if tmp['type'] == 'array':
                        if models[name]['properties'][p]['items'].get('$ref', False):
                            tmp['items'] = parse_data(models[name]['properties'][p]['items']['$ref'].split('/')[-1])
                        else:
                            tmp['items'] = models[name]['properties'][p]['items']

                    if models[name]['properties'][p].get('enum'):
                        tmp['enum'] = models[name]['properties'][p]['enum']
                    if models[name]['properties'][p].get('example'):
                        tmp['example'] = models[name]['properties'][p].get('example')
                else:
                    tmp = {
                        'name': p,
                        'type': parse_data(models[name]['properties'][p]['$ref'].split('/')[-1])
                    }
                res.append(tmp)
            return res

        if data.get('$ref', False):
            return parse_data(data['$ref'].split('/')[-1])

        else:
            return {}

    def __init__(self,
                 dict_swagger=None,
                 path_to_swagger=None):

        if not dict_swagger and not path_to_swagger:
            print('нет необходимых аргументов для выполнения запроса')
            sys.exit(0)
        if dict_swagger:
            super(Swagger2Parser, self).__init__(dict_swagger)
        else:
            try:
                super(Swagger2Parser, self).__init__(Swagger2Parser._read_json(dict_swagger))
            except FileNotFoundError:
                print('не вышло прочитать файл')
                sys.exit(0)
        self.base_url = ''
        self.parse()

    def parse(self):
        try:
            self.base_url = self.dict_swagger['host'] + self.dict_swagger['basePath']
            # print(self.base_url)
        except KeyError:
            Swagger2Parser._stop_parse()
        self.__generate_structures_by_tags()

    def __generate_structures_by_tags(self):

        def get_data_for_body(data,
                              models_):
            res = []
            for d in data['parameters']:
                if d['in'] == 'body':
                    tmp = {
                        'is_required': d.get('required'),
                        'data': Swagger2Parser.parse_schema(d['schema'],
                                                            models_)
                    }
                    res.append(tmp)
            return res

        def get_data_for_(data,
                          type_):
            # print(1)
            res = []
            for d in data['parameters']:
                if d['in'] == type_:
                    res.append({
                        'name': d['name'],
                        'is_required': d.get('required', False),
                        'type': d.get('type', 'string'),
                        'pattern': d.get('pattern', None),
                        'value': ''
                    })
            if type_ == 'header':
                if data.get('consumes', False):
                    res.append({
                        'name': 'accept',
                        'value': data['consumes'][0],
                        'type': 'string'
                    })
                if data.get('produces', False):
                    res.append({
                        'name': 'Content-Type',
                        'value': data['produces'][0],
                        'type': 'string'
                    })

        def get_data_responses(data,
                               model_):
            answer = {}
            for p_ in data.keys():
                tmp = {
                    'description': data[p_]['description'],
                }
                if data[p_].get('schema', False):
                    tmp['schema'] = Swagger2Parser.parse_schema(data[p_]['schema'],
                                                                model_)
                answer[p_] = tmp
            return answer

        def parse_tags(self_):
            self_.list_tags = [tag_['name'] for tag_ in self_.dict_swagger['tags']]

        parse_tags(self)
        Swagger2Parser.ensure_dir('{}/{}'.format(self.PATH_TO_DIR,self.TITLE_MAIN_DIR))
        for tag in self.list_tags:
            Swagger2Parser.ensure_dir('{}/{}/{}'.format(self.PATH_TO_DIR,
                                                        self.TITLE_MAIN_DIR,
                                                        tag))
        paths = self.dict_swagger['paths']
        models = self.dict_swagger['definitions']
        ans = []

        for p in paths.keys():
            for method in paths[p].keys():
                result_ = {
                    'url': p,
                    'method': method,
                    'tags': paths[p][method]['tags'],
                    'operationId': paths[p][method]['operationId'],
                    'header': get_data_for_(paths[p][method],
                                            'header'),
                    'body': get_data_for_body(paths[p][method],
                                              models),
                    'query': get_data_for_(paths[p][method],
                                           'query'),
                    'path': get_data_for_(paths[p][method],
                                          'path'),
                    'file': get_data_for_(paths[p][method],
                                          'file'),
                    'responses': get_data_responses(paths[p][method]['responses'],
                                                    models)
                }
                for r in result_['tags']:
                    with open(self.PATH_TO_DIR
                                      + '/'
                                      + self.TITLE_MAIN_DIR
                                      + '/'
                                      + r
                                      + '/'
                                      + result_['operationId']
                                      + '.json', 'w') as file:
                        # file.write(result_)
                        json.dump(result_, file)








