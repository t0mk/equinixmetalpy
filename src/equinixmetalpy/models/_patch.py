# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List
from . import _models_py3

__all__: List[
    str
] = []  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
    _models_py3.DeviceList.list = property(lambda self: self.devices)
    _models_py3.ProjectList.list = property(lambda self: self.projects)
    _models_py3.OrganizationList.list = property(lambda self: self.organizations)
