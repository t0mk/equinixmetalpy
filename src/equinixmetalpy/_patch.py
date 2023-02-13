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
import datetime
from http.client import responses


__all__: List[str] = [
    "MetalApiError",
    "Client",
    "is_error",
    "raise_if_error",
]  # Add all objects you want publicly available to users at this package level


EM_API = "https://api.equinix.com/metal/v1"

HEADERS_TO_SANITIZE = ["x-auth-token", "set-cookie"]


def prettyjson(txt):
    return json.dumps(json.loads(txt), sort_keys=True, indent=4, separators=(",", ": "))


def get_headers_string(headers_dict):
    log_string = ""
    for header, value in headers_dict.items():
        if header.lower() in HEADERS_TO_SANITIZE:
            log_string += "{}: REDACTED\n".format(header)
        else:
            log_string += "{}: {}\n".format(header, value)
    return log_string


def get_timestamp():
    # get timestamp in current timezone
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class HttpLoggingPolicy(SansIOHTTPPolicy):

    """
    HTTP request/response logger.
    """

    def __init__(self, api_endpoint, file=None):  # pylint: disable=unused-argument
        self._logger = logging.getLogger(__name__)
        handler = logging.StreamHandler(stream=sys.stderr)
        if file:
            handler = logging.FileHandler(file)
        self._logger.addHandler(handler)
        self._logger.setLevel(logging.DEBUG)
        self.api_endpoint = api_endpoint

    def on_request(self, request):  # pylint: disable=too-many-return-statements
        # type: (PipelineRequest) -> None
        """Logs HTTP request to the DEBUG logger.
        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        """
        self._logger.debug(get_timestamp())
        topdiv = "=======[REQUEST]=============\nHTTP {} to {}".format(
            request.http_request.method,
            request.http_request.url.replace(self.api_endpoint, ""),
        )
        http_request = request.http_request
        if not self._logger.isEnabledFor(logging.DEBUG):
            return

        self._logger.debug(topdiv)
        try:
            log_string = get_headers_string(http_request.headers)
            # We don't want to log the binary data of a file upload.
            if isinstance(http_request.body, types.GeneratorType):
                log_string += "File upload in body"
            elif isinstance(http_request.body, types.AsyncGeneratorType):
                log_string += "File upload"
            elif http_request.body:
                if http_request.headers.get("content-type", "").startswith(
                    "application/json"
                ):
                    log_string += "Body:\n" + prettyjson(http_request.body)
                else:
                    log_string += "Body: {}\b".format(str(http_request.body))
            else:
                log_string += "<Empty body>"
            self._logger.debug(log_string)
        except Exception as err:  # pylint: disable=broad-except
            self._logger.debug("Failed to log request: %r", err)
        self._logger.debug("")

    def on_response(self, request, response):
        # type: (PipelineRequest, PipelineResponse) -> None
        """Logs HTTP response to the DEBUG logger.
        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: The PipelineResponse object.
        :type response: ~azure.core.pipeline.PipelineResponse
        """
        http_response = response.http_response
        topdiv = '=======[RESPONSE]============\nHTTP {} ({}) from {}'.format(
            http_response.status_code,
            responses.get(http_response.status_code, "Unknown"),
            request.http_request.url.replace(self.api_endpoint, ""),
        )

        try:
            if not self._logger.isEnabledFor(logging.DEBUG):
                return

            self._logger.debug(get_timestamp())
            self._logger.debug(topdiv)
            log_string = get_headers_string(http_response.headers)
            # We don't want to log binary data if the response is a file.
            # log_string += "\nBody:"
            pattern = re.compile(
                r'attachment; ?filename=["\w.]+', re.IGNORECASE)
            header = http_response.headers.get("content-disposition")

            if header and pattern.match(header):
                filename = header.partition("=")[2]
                log_string += "Body contains file attachments: {}".format(
                    filename)
            elif http_response.headers.get("content-type", "").endswith("octet-stream"):
                log_string += "Body contains binary data."
            elif http_response.headers.get("content-type", "").startswith("image"):
                log_string += "Body contains image data."
            elif http_response.headers.get("content-type", "").startswith(
                "application/json"
            ):
                log_string += "Body:\n" + prettyjson(http_response.text())
            else:
                if response.context.options.get("stream", False):
                    log_string += "Body is streamable."
                else:
                    txt = http_response.text()
                    if txt:
                        log_string += "Body:\n{}".format(txt)
                    else:
                        log_string += "<Empty body>"
                    # log_string += "\n{}".format(http_response.text())
            self._logger.debug(log_string)
        except Exception as err:  # pylint: disable=broad-except
            self._logger.debug("Failed to log response: %s", repr(err))
        self._logger.debug("")


class Client(GeneratedClient):
    def __init__(self, credential: str, base_url: str = EM_API, **kwargs: Any) -> None:
        credential = AzureKeyCredential(credential)
        if os.getenv("METAL_PYTHON_DEBUG") == "1":
            policy_args = dict(api_endpoint=base_url)
            debug_log_file = os.getenv("METAL_PYTHON_DEBUG_PATH", None)
            if debug_log_file is not None:
                if debug_log_file == "":
                    raise ValueError(
                        "METAL_PYTHON_DEBUG_PATH must be a non-empty string"
                    )
                policy_args["file"] = debug_log_file
            logging_policy = HttpLoggingPolicy(**policy_args)
            kwargs["logging_policy"] = logging_policy
        sdk_moniker = f"equinixmetalpy/{_version.VERSION}"
        super().__init__(credential, base_url, sdk_moniker=sdk_moniker, **kwargs)


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


class MetalApiError(Exception):
    isNotFoundError = False

    def __init__(self, error_list):
        if "Not found" in error_list:
            self.isNotFoundError = True
        super().__init__(" ".join([e for e in error_list]))

    pass


def is_error(result):
    err_classes = [
        Error,
    ]
    if type(result) in err_classes:
        return True
    return False


def collect_error_list(err_result, prefix):
    err_list = []
    if prefix != "":
        err_list.append(prefix)
    if err_result.error is not None:
        err_list.append(err_result.error)
    if err_result.errors is not None:
        err_list.extend(err_result.errors)
    return err_list


def raise_if_error(result, prefix=""):
    if prefix != "":
        prefix = prefix + ":"
    if is_error(result):
        raise MetalApiError(collect_error_list(result, prefix))
    return result
