# equinixmetalpy

Python SDK generated with azure/autorest, insipired by https://github.com/digitalocean/pydo

It only create methods ofr API call, I haven't found a way for it to create models (classes) for API objects and query bodies yet.

## Using

See [example.py](example.py).

## Generating

First install what you need `make install`, and then generate:

`make generate`

.. takes about 5 minutes on Dell XPS 9830 (16 GB RAM).

## Config

Autorest is configurable via markdown file in [client_gen_config.md](client_gen_config.md). It's possible to tweak the OpenAPI JSON with some sort of JSON query and transform language. It's not straightforward.




