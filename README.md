# equinixmetalpy

Python SDK for Equinix Metal API, generated with azure/autorest, insipired by https://github.com/digitalocean/pydo

## Using

See [example.py](example.py).

## Patching Equinix Metal OpenAPI spec

We need to do some fixes to the default openapi yaml specification from Equinix Metal. The [fixSpec.py](fixSpec.py) script modifies the original in `openapi.yaml` into `openapi.fixed.yaml`.

The script also prunes the paths in the spec, so that we don't need to wait long time for generating the code. The fixed spec only contains API for Projects, Devices and Operation right now.

## Generating

First install what you need `make install`, and then generate:

`make generate`

## Config

Autorest is configurable via markdown file in [client_gen_config.md](client_gen_config.md). It's possible to tweak the OpenAPI JSON with some sort of JSON query and transform language. It's not straightforward.




