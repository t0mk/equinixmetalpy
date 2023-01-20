# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from equinixmetalpy import GeneratedClient, _version
from .models import Error

from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.policies import SansIOHTTPPolicy
from azure.core.pipeline import PipelineRequest, PipelineResponse

import os
from typing import List, Any
import logging
import sys
import re
import types
import json
from http.client import responses

_LOGGER = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stderr)
_LOGGER.addHandler(handler)
_LOGGER.setLevel(logging.DEBUG)


__all__: List[str] = [
    "ApiException",
    "Client",
    "is_error",
    "collect_error_message",
    "raise_if_error",
]  # Add all objects you want publicly available to users at this package level


EM_API = "https://api.equinix.com/metal/v1"

HEADERS_TO_SANITIZE = ["x-auth-token", "set-cookie"]


def prettyjson(txt):
    return json.dumps(json.loads(txt), sort_keys=True, indent=4, separators=(",", ": "))


def get_bottom_divider(topdiv):
    return "└" + "─" * (len(topdiv) - 2) + "┘" + "\n"


def get_top_divider(title):
    return "┌{}[ {} ]{}┐".format("─" * 4, title, "─" * 4)


def get_headers_string(headers_dict):
    log_string = "Headers:"
    for header, value in headers_dict.items():
        if header.lower() in HEADERS_TO_SANITIZE:
            log_string += "\n  '{}': REDACTED".format(header)
        else:
            log_string += "\n  '{}': '{}'".format(header, value)
    return log_string


class HttpLoggingPolicy(SansIOHTTPPolicy):

    """
    HTTP request/response logger.
    """

    def __init__(self, api_endpoint):  # pylint: disable=unused-argument
        self.api_endpoint = api_endpoint

    def on_request(self, request):  # pylint: disable=too-many-return-statements
        # type: (PipelineRequest) -> None
        """Logs HTTP request to the DEBUG logger.
        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        topdiv = get_top_divider(
            "Http {} to {}".format(
                request.http_request.method,
                request.http_request.url.replace(self.api_endpoint, ""),
            )
        )
        http_request = request.http_request
        if not _LOGGER.isEnabledFor(logging.DEBUG):
            return

        _LOGGER.debug(topdiv)
        try:
            log_string = get_headers_string(http_request.headers)
            # We don't want to log the binary data of a file upload.
            if isinstance(http_request.body, types.GeneratorType):
                log_string += "\nFile upload in body"
            elif isinstance(http_request.body, types.AsyncGeneratorType):
                log_string += "\nFile upload"
            elif http_request.body:
                if http_request.headers.get("content-type", "").startswith(
                    "application/json"
                ):
                    log_string += "\nBody:\n" + prettyjson(http_request.body)
                else:
                    log_string += "\nBody:\n{}".format(str(http_request.body))
            else:
                log_string += "\nEmpty body"
            _LOGGER.debug(log_string)
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.debug("Failed to log request: %r", err)
        _LOGGER.debug(get_bottom_divider(topdiv))

    def on_response(self, request, response):
        # type: (PipelineRequest, PipelineResponse) -> None
        """Logs HTTP response to the DEBUG logger.
        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: The PipelineResponse object.
        :type response: ~azure.core.pipeline.PipelineResponse
        """
        http_response = response.http_response
        topdiv = get_top_divider(
            'Http {} "{}" from {}'.format(
                http_response.status_code,
                responses.get(http_response.status_code, "Unknown"),
                request.http_request.url.replace(self.api_endpoint, ""),
            )
        )
        try:
            if not _LOGGER.isEnabledFor(logging.DEBUG):
                return

            _LOGGER.debug(topdiv)
            log_string = get_headers_string(http_response.headers)
            # We don't want to log binary data if the response is a file.
            # log_string += "\nBody:"
            pattern = re.compile(
                r'attachment; ?filename=["\w.]+', re.IGNORECASE)
            header = http_response.headers.get("content-disposition")

            if header and pattern.match(header):
                filename = header.partition("=")[2]
                log_string += "\nBody contains file attachments: {}".format(
                    filename)
            elif http_response.headers.get("content-type", "").endswith("octet-stream"):
                log_string += "\nBody contains binary data."
            elif http_response.headers.get("content-type", "").startswith("image"):
                log_string += "\nBody contains image data."
            elif http_response.headers.get("content-type", "").startswith(
                "application/json"
            ):
                log_string += "\nBody:\n" + prettyjson(http_response.text())
            else:
                if response.context.options.get("stream", False):
                    log_string += "\nBody is streamable."
                else:
                    txt = http_response.text()
                    if txt:
                        log_string += "\nBody:\n{}".format(txt)
                    else:
                        log_string += "\nEmpty body"
                    # log_string += "\n{}".format(http_response.text())
            _LOGGER.debug(log_string)
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.debug("Failed to log response: %s", repr(err))
        _LOGGER.debug(get_bottom_divider(topdiv))


class Client(GeneratedClient):
    def __init__(self, credential: str, base_url: str = EM_API, **kwargs: Any) -> None:
        credential = AzureKeyCredential(credential)
        if os.getenv("METAL_PYTHON_DEBUG") == "1":
            kwargs["logging_policy"] = HttpLoggingPolicy(api_endpoint=base_url)
        sdk_moniker = f"equinixmetalpy/{_version.VERSION}"
        super().__init__(credential, base_url, sdk_moniker=sdk_moniker, **kwargs)


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
