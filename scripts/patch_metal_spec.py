#!/usr/bin/env python3

import yaml
from yaml.loader import FullLoader
import copy
import sys
from collections import OrderedDict

if len(sys.argv) != 3:
    print("Usage: {} <input file> <output file>".format(sys.argv[0]))
    sys.exit(1)

INFILE = sys.argv[1]
OUTFILE = sys.argv[2]


# what tags I want to keep
WANT_TAGS = ["Projects", "Devices", "Organizations"]

# what paths I want to keep
WANT_PATHS = [
    '/devices/{id}',
    '/devices/{id}/ips',
    '/organizations',
    '/organizations/{id}',
    '/organizations/{id}/projects',
    '/organizations/{id}/devices',
    '/projects',
    '/projects/{id}',
    '/projects/{id}/devices',
    '/projects/{id}/ips',
    '/ips/{id}',
    '/ips/{id}/available',
    '/ips/{id}/customdata',
    '/projects/{project_id}/ips/{id}/customdata',
    '/vrfs/{vrf_id}/ips/{id}',
]


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


EXPLODE_ALLOWED_TYPES = [
    "array",
    "object",
]


def fixExplode(di):
    if isinstance(di, dict):
        if 'explode' in di:
            if di['schema']['type'] in EXPLODE_ALLOWED_TYPES:
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


originalSpec = loadYaml(INFILE)
fixedSpec = copy.deepcopy(originalSpec)

tags = []
paths = OrderedDict()
schemas = OrderedDict()

for t in originalSpec['tags']:
    if t['name'] in WANT_TAGS:
        tags.append(t)

for path in originalSpec['paths']:
    if path in WANT_PATHS:
        paths[path] = originalSpec['paths'][path]

neededSchemas = findSchemas(paths)
for s in neededSchemas:
    schemas[s] = originalSpec['components']['schemas'][s]

neededSchemas = set()
newSchemasDiscovered = True

# this is just cherrypicking schemas that are wanted
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

# FIX 0. organization href to project
fixedSpec['components']['schemas']['Project']['properties']['organization'] = {
    "$ref": "#/components/schemas/Href"
}

# FIX 1. href property to all schemas if they have propertiesm and don't already have it
for s in fixedSpec['components']['schemas']:
    if 'properties' in fixedSpec['components']['schemas'][s]:
        if 'href' not in fixedSpec['components']['schemas'][s]['properties']:
            fixedSpec['components']['schemas'][s]['properties']['href'] = {
                "type": "string",
                "format": "uri"
            }

# FIX 2. remove defaults for always_pxe and hardware_reservation_id
fixSchemas = ["DeviceCreateInput"]
removeProperties = ["always_pxe", "hardware_reservation_id"]
for s in fixSchemas:
    for p in removeProperties:
        if p in fixedSpec['components']['schemas'][s]['properties']:
            del fixedSpec['components']['schemas'][s]['properties'][p]['default']

# FIX 3. fix type and format for integers
fixNumInt(fixedSpec)

# FIX 4. fix explode in non-array parameters
fixExplode(fixedSpec)

# FIX 5. add backend_transfer_enabled to Project Schema
project_props = fixedSpec['components']['schemas']['Project']['properties']
project_props['backend_transfer_enabled'] = {'type': 'boolean'}

# FIX 6. add `name` param to allow for search by resource name
search_param = {
    "name": "name",
    "in": "query",
    "description": "Search by name substring",
    "required": False,
    "schema": {
        "type": "string"
    }
}
search_capable_paths = [
    '/projects',
    '/organizations/{id}/projects',
    '/projects/{id}/devices',
    '/organizations/{id}/devices',
]
# for path in search_capable_paths:
#   fixedSpec['paths'][path]['get']['parameters'].append(search_param)

with open(OUTFILE, 'w') as f:
    originalSpec = yaml.dump(
        fixedSpec, f, sort_keys=False, default_flow_style=False)

print(INFILE, "was fixed into", OUTFILE)
