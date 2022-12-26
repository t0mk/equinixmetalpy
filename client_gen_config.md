# Autorest config

```yaml
title: MetalPythonClient
namespace: equinixmetalpy
python: true
black: true
output-folder: src/
verbose: true
version-tolerant: true
override-client-name: Client

add-credential: true
credential-default-policy-type: AzureKeyCredentialPolicy
credential-key-header-name: X-Auth-Token


directive:
  - from: openapi-document
    where: '$.paths["/devices/{id}/traffic"].get.parameters[4]'
    debug: true
    transform: >
      $["explode"] = undefined;
```

## examples of directives
https://github.com/Azure/autorest/blob/e9bee3709d31d8e01e21c3ab66fc8007696b4301/packages/extensions/core/resources/directives.md

http://azure.github.io/autorest/user/literate-file-formats/configuration.html#directives---global-or-per-language
