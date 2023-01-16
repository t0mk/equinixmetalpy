# equinixmetalpy

Python SDK for Equinix Metal API, generated with azure/autorest,
insipired by <https://github.com/digitalocean/pydo>

## Quickstart

To create a device, you can use 

```python
import equinixmetalpy
import os

client = equinixmetalpy.Client(os.getenv("PACKET_AUTH_TOKEN"))

# select first free project
projects_resp = client.find_projects()
pid = projects_resp.projects[0].id

dci = equinixmetalpy.models.DeviceCreateInMetroInput(
    operating_system="ubuntu_18_04",
    plan="c3.small.x86",
    hostname="test",
    metro="sv",
    billing_cycle="hourly",
    tags=["test"]
)

new_device_resp = client.create_device(pid, dci)

# The variable can contain either new device object or error.
# Check it with raise_if_error.
equinixmetalpy.raise_if_error(new_device_resp)

print("New Device:")
print(new_device_resp)

```

## Debugging HTTP API calls

If you want to see HTTP traffice, set env var `METAL_PYTHON_DEBUG` to
"1".

## Patching Equinix Metal OpenAPI spec

We need to do some fixes to the default openapi yaml specification
from Equinix Metal. The [fixSpec.py](fixSpec.py) script modifies the
original in `openapi.yaml` into `openapi.fixed.yaml`.

The script also prunes paths in the spec, so that we don't need to
wait long time for generating code for all the API operations. The
fixed spec only contains API for Projects, Devices and Operation right
now.

## Generating

First install what you need `make install`, and then generate:

`make generate`

### Config for code generation

Autorest is configurable via markdown file in [client_gen_config.md]
(client_gen_config.md). It's possible to tweak the OpenAPI JSON with
 some sort of JSON query and transform language. It's not
 straightforward.

