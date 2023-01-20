#!/usr/bin/env python3

import os
import time

import equinixmetalpy


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


client = equinixmetalpy.Client(os.environ["METAL_AUTH_TOKEN"])
project_id = os.environ["METAL_PROJECT_ID"]

dci = equinixmetalpy.models.DeviceCreateInMetroInput(
    operating_system="ubuntu_18_04",
    plan="c3.small.x86",
    hostname="test",
    metro="sv",
    billing_cycle="hourly",
    tags=["test"]
)

print("About to create device in project: " + project_id)
new_device_resp = client.create_device(project_id, dci)

# The variable can contain either new device object or error.
# Check it with raise_if_error.
equinixmetalpy.raise_if_error(new_device_resp)

print("New Device:")
print(new_device_resp)

wait_for_device_active(new_device_resp.id)

print("Device is active:")
print(new_device_resp)

print("About to delete device")
device_del_resp = client.delete_device(new_device_resp.id)
equinixmetalpy.raise_if_error(device_del_resp)
print("Deleted device")
