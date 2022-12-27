#!/usr/bin/env python3

import os
import time

# for prettier printing
# $ pip install rich
from rich import print

from src.equinixmetalpy import Client

from azure.core.credentials import AzureKeyCredential



def wait_for_device_active(did):
    wait_timeout = time.time() + time.time() + 60 * 5
    while wait_timeout > time.time() : 
        device = client.find_device_by_id(did)
        if device['state'] == 'active':
            return device
        print(f"Waiting for device {did} to become active, device state is {device['state']}")
        time.sleep(5)
    raise Exception("Timed out waiting for device to become active")

akc = AzureKeyCredential(
    os.getenv("PACKET_AUTH_TOKEN")
)

client = Client(akc)


projects_resp = client.find_projects()
pid = projects_resp['projects'][0]['id']

device_create_request = {
    "hostname": "test",
    "plan": "c3.small.x86",
    "operating_system": "ubuntu_18_04",
    "metro": "sv",
    "billing_cycle": "hourly",
    "project_id": pid,
    "tags": ["test"],
}

new_device_resp = client.create_device(pid, device_create_request)
print("New Device:")
print(new_device_resp)

wait_for_device_active(new_device_resp['id'])

project_devices_resp = client.find_project_devices(pid)
print("Project Devices:")
print(project_devices_resp)

delete_device_resp = client.delete_device(
    project_devices_resp['devices'][0]['id']
)
print("Deleted Device Resp:")
print(delete_device_resp)
