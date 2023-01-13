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
from .models import Error
import os
from ._http_logger import HttpLoggingPolicy

__all__: List[str] = [
    "ApiException",
    "Manager",
    "is_error",
    "collect_error_message",
    "raise_if_error",
]  # Add all objects you want publicly available to users at this package level


EM_API = "https://api.equinix.com/metal/v1"


class Manager(Client):
    def __init__(
        self,
        credential: str,
        base_url: str = EM_API,
        **kwargs: Any
    ) -> None:
        azure_credential = AzureKeyCredential(credential)
        if os.getenv("METAL_PYTHON_DEBUG") == "1":
            kwargs["logging_policy"] = HttpLoggingPolicy(api_endpoint=base_url)
        super().__init__(azure_credential, base_url, **kwargs)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


class ApiException(Exception):
    pass


def is_error(result):
    err_classes = [
        Error,
    ]
    if type(result) in err_classes:
        return True
    return False


def collect_error_message(err_result):
    err_list = []
    if err_result.error is not None:
        err_list.append(err_result.error)
    if err_result.errors is not None:
        err_list.extend(err_result.errors)
    return ", ".join(err_list)


def raise_if_error(result):
    if is_error(result):
        raise ApiException(collect_error_message(result))
    return result
