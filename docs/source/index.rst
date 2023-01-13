.. Equinixmetalpy documentation master file, created by
   sphinx-quickstart on Mon Nov  7 12:26:30 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

#########################################
:mod:`Equinixmetalpy` --- Python library for Equinix Metal
#########################################

.. module:: equinixmetalpy

:mod:`equinixmetalpy` is a Python client library for Equnix Metal HTTP API
`<https://deploy.equinix.com/developers/api/metal/>`_.

Installation
============

Install from PyPI::

    pip install equinixmetalpy


Initialization
==============

:mod:`equinixmetalpy` must be initialized with :meth:`equinixmetalpy.client`. A
Equinix Metal Token is required. The token can be passed explicitly to :meth:`equinixmetalpy.client` or defined as environment variables
``METAL_AUTH_TOKEN``.

Here's an example of initializing the Equinixmetalpy Client::

   from equinixmetalpy import Client

   client = Client(token="<METAL_AUTH_TOKEN>")  

.. autofunction:: equinixmetalpy.Client

Example
===========
Find below a working example for GET a ssh_key (`per this http request
<https://deploy.equinix.com/developers/api/metal/#tag/SSHKeys>`_) and printing the ID associated with the ssh key. If you'd like to try out this quick example, you can follow these instructions to add ssh keys to your DO account::

   from equinixmetalpy import Client

   client = Client(token="<YOUR-API-TOKEN>")  

   ssh_keys_resp = client.ssh_keys.list()
   for k in ssh_keys_resp["ssh_keys"]:
      print(f"ID: {k['id']}, NAME: {k['name']}, FINGERPRINT: {k['fingerprint']}")

The above code snippet should output the following::

   ID: 123456, NAME: my_test_ssh_key, FINGERPRINT: 5c:74:7e:60:28:69:34:ca:dd:74:67:c3:f3:00:7f:fe
   ID: 123457, NAME: my_prod_ssh_key, FINGERPRINT: eb:76:c7:2a:d3:3e:80:5d:ef:2e:ca:86:d7:79:94:0d

Pagination
~~~~~~~~~~~
Below is an example on handling pagination. One must parse the URL to find the next page::

   resp = self.client.ssh_keys.list(per_page=50, page=page)
   pages = resp.links.pages
      if 'next' in pages.keys():
            parsed_url = urlparse(pages['next'])
            page = parse_qs(parsed_url.query)['page'][0]
      else:
            paginated = False


equinixmetalpy.Client Usage
===========

.. automodule:: equinixmetalpy.operations
   :members:
   :undoc-members:
   :show-inheritance:
