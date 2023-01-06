# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Any
from ._client import Client
from azure.core.credentials import AzureKeyCredential

__all__: List[
    str
] = ["Manager"]  # Add all objects you want publicly available to users at this package level


class Manager(Client):
    def __init__(

        self,
        credential: str,
        base_url: str = "https://api.equinix.com/metal/v1",
        **kwargs: Any
    ) -> None:
        azure_credential = AzureKeyCredential(credential)
        super().__init__(azure_credential, base_url, **kwargs)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
