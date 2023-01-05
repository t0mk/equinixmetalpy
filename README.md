# equinixmetalpy

Python SDK for Equinix Metal API, generated with azure/autorest, insipired by https://github.com/digitalocean/pydo

## Using

See [example.py](example.py).

## Patching Equinix Metal OpenAPI spec

We need to do some fixes to the default openapi yaml specification from Equinix Metal. The [fixSpec.py](fixSpec.py) script modifies the original in `openapi.yaml` into `openapi.fixed.yaml`.

## Generating

First install what you need `make install`, and then generate:

`make generate`

.. takes about 5 minutes on Dell XPS 9830 (16 GB RAM).

## Config

Autorest is configurable via markdown file in [client_gen_config.md](client_gen_config.md). It's possible to tweak the OpenAPI JSON with some sort of JSON query and transform language. It's not straightforward.




