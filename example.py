#!/usr/bin/env python3

from src.equinixmetalpy.models import DeviceCreateInMetroInput
import os
import time

# for prettier printing
# $ pip install rich
from rich import print

import equinixmetalpy

from equinixmetalpy import ApiException


def wait_for_device_active(did):
    wait_timeout = time.time() + time.time() + 60 * 5
    while wait_timeout > time.time():
        device = client.find_device_by_id(did)
        if device.state == 'active':
            return device
        print(
            f"Waiting for device {did} to become active, device state is {device.state}")
        time.sleep(5)
    raise Exception("Timed out waiting for device to become active")


client = equinixmetalpy.Manager(os.getenv("PACKET_AUTH_TOKEN"))


projects_resp = client.find_projects()
pid = projects_resp.projects[0].id

dci = DeviceCreateInMetroInput(
    operating_system="ubuntu_18_04",
    plan="c3.small.x86",
    hostname="test",
    metro="sv",
    billing_cycle="hourly",
    tags=["test"]
)


def set_defined(object, key, value):
    if not hasattr(object, key):
        raise Exception(
            "Object {0} does not have attribute {1}".format(object, key))
    if value is not None:
        setattr(object, key, value)


#set_defined(dci, "metro", "ff")


new_device_resp = client.create_device(pid, dci)
print("New Device:")
print(type(new_device_resp))
print(new_device_resp)
equinixmetalpy.raise_if_error(new_device_resp)

wait_for_device_active(new_device_resp.id)

project_devices_resp = client.find_project_devices(pid)
print("Project Devices:")
print(project_devices_resp)

delete_device_resp = client.delete_device(
    project_devices_resp.devices[0].id
)
print("Deleted Device Resp:")
print(delete_device_resp)
