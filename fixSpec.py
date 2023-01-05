#!/usr/bin/env python3

import yaml
from yaml.loader import FullLoader
import copy
from collections import OrderedDict

INFILE = "openapi.yaml"
OUTFILE = "openapi.fixed.yaml"

def setup_yaml():
    """ https://stackoverflow.com/a/8661021 """
    def represent_dict_order(self, data): return self.represent_mapping(
        'tag:yaml.org,2002:map', data.items())
    yaml.add_representer(OrderedDict, represent_dict_order)

setup_yaml()

def fixNumInt(di):
    if isinstance(di, dict):
        for k, v in di.items():
            if k == "format" and v == "integer":
                di["type"] = "integer"
                di["format"] = "int32"
            fixNumInt(v)
    elif isinstance(di, list):
        for v in di:
            fixNumInt(v)

def fixPrevious(di):
    print("prev")
    if isinstance(di, dict):
        for k, v in di.items():
            print(k, v)
            if k == "previous":
                di[k]["nullable"] = True
                return
            fixPrevious(v)
    elif isinstance(di, list):
        for v in di:
            fixPrevious(v)


def fixExplode(di):
    if isinstance(di, dict):
        if 'explode' in di:
            if 'items' in di['schema']:
                pass
            else:
                del di['explode']
                #ic("NOT OK", di)
            return
        for k, v in di.items():
            fixExplode(v)
    elif isinstance(di, list):
        for v in di:
            fixExplode(v)


def findSchemas(di):
    ret = set()

    def walk(di):
        if isinstance(di, dict):
            for k, v in di.items():
                walk(v)
        elif isinstance(di, list):
            for v in di:
                walk(v)
        else:
            if (type(di) == str) and ("/schemas/" in di):
                ret.add(di.split("/")[-1])
    walk(di)
    return ret


def loadYaml(fn):
    with open(fn) as f:
        return yaml.load(f, Loader=FullLoader)


# what tags I want to keep
WANT = ["Projects", "Devices"]

# what paths I want to keep
PATHS = [
    '/projects',
    '/projects/{id}',
    '/projects/{id}/devices',
    '/devices/{id}',
]


originalSpec = loadYaml(INFILE)
fixedSpec = copy.deepcopy(originalSpec)

tags = []
paths = OrderedDict()
schemas = OrderedDict()

for t in originalSpec['tags']:
    if t['name'] in WANT:
        tags.append(t)

for path in originalSpec['paths']:
    if path in PATHS:
        paths[path] = originalSpec['paths'][path]

neededSchemas = findSchemas(paths)
for s in neededSchemas:
    schemas[s] = originalSpec['components']['schemas'][s]

neededSchemas = set()
newSchemasDiscovered = True

while newSchemasDiscovered:
    newSchemasDiscovered = False
    newSchemas = findSchemas(schemas)
    addSchemas = newSchemas - neededSchemas
    neededSchemas = neededSchemas.union(newSchemas)
    newSchemasDiscovered = len(addSchemas) > 0

    for s in addSchemas:
        if s in neededSchemas:
            schemas[s] = originalSpec['components']['schemas'][s]

fixedSpec['info']['description'] = "desc"
del fixedSpec['x-tagGroups']
fixedSpec['components']['schemas'] = schemas
fixedSpec['components']['requestBodies'] = {}
fixedSpec['tags'] = tags
fixedSpec['paths'] = paths

# fixing schema
fixSchemas = ["DeviceCreateInput"]
removeProperties = ["always_pxe", "hardware_reservation_id"]
for s in fixSchemas:
    for p in removeProperties:
        if p in fixedSpec['components']['schemas'][s]['properties']:
            del fixedSpec['components']['schemas'][s]['properties'][p]['default']

fixNumInt(fixedSpec)
fixExplode(fixedSpec)
#fixPrevious(fixedSpec)

with open(OUTFILE, 'w') as f:
    originalSpec = yaml.dump(
        fixedSpec, f, sort_keys=False, default_flow_style=False)

print(INFILE, "was fixed into", OUTFILE)
