# equinixmetalpy

Python SDK for Equinix Metal API, generated with azure/autorest,
insipired by <https://github.com/digitalocean/pydo>

## Quickstart

Simple example showing how to create a device:

```python
import os

import equinixmetalpy

client = equinixmetalpy.Client(os.environ["METAL_AUTH_TOKEN"])
project_id = os.environ["METAL_PROJECT_ID"]

dci = equinixmetalpy.models.DeviceCreateInMetroInput(
    operating_system="ubuntu_18_04",
    plan="c3.small.x86",
    hostname="test",
    metro="sv",
    billing_cycle="hourly",
    tags=["test"]
)

print("About to create device in project: " + project_id)
new_device_resp = client.create_device(project_id, dci)
```

See [examples/device_basic.py](examples/device_basic.py) and other
scripts in [examples](examples) directory for more complete code.

## Debugging HTTP API calls

If you want to see HTTP traffic, set env var `METAL_PYTHON_DEBUG` to
"1".

## Patching Equinix Metal OpenAPI spec

We need to do some fixes to the default openapi yaml specification
from Equinix Metal. The [fixSpec.py](fixSpec.py) script modifies the
original in `openapi.yaml` into `openapi.fixed.yaml`.

The script also prunes paths in the spec, so that we don't need to
wait long time for generating code for all the API operations. The
fixed spec only contains API for Projects, Devices and Organization right
now.

## Generating

First install what you need `make install`, and then generate:

`make generate`

### Config for code generation

Autorest is configurable via markdown file in [client_gen_config.md]
(client_gen_config.md). It's possible to tweak the OpenAPI JSON with
 some sort of JSON query and transform language. It's not
 straightforward.

