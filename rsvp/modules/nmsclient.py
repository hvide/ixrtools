import requests
import typing

from urllib.parse import urlencode

import logging

from pprint import pprint

from .models import Device, SearchOxidizedResult, OspfNbrResult, Port

requests.packages.urllib3.disable_warnings()

logger = logging.getLogger()


class NmsClient:
    def __init__(self, api_key: str, base_url: str, verify: bool = True):

        self.verify = verify
        self.api_key = api_key
        self.base_url = base_url

        self._headers = {'X-Auth-Token': self.api_key}

        self.domain = ".as43531.net"

    def _make_request(self, method: str, endpoint: str, data: typing.Dict):

        if method == "GET":
            try:
                response = requests.get(
                    self.base_url + endpoint, params=data, headers=self._headers, verify=self.verify)
            except Exception as e:  # Takes into account any possible error, most likely network errors
                logger.error(
                    "Connection error while making %s request to %s: %s", method, endpoint, e)
                return None

        else:
            raise ValueError()

        if response.status_code == 200:
            return response.json()
        else:
            logger.error("Error while making %s request to %s: %s (error code %s)",
                         method, endpoint, response.json(), response.status_code)
            return response.json()

        # return None

    def get_devices(self, filter_type=None, query=None):
        """
        Return a list of devices.
        :param filter_type: Can be one of the following to filter or search by:
            all: All devices
            active: Only not ignored and not disabled devices
            ignored: Only ignored devices
            up: Only devices that are up
            down: Only devices that are down
            disabled: Disabled devices
            os: search by os type
            mac: search by mac address
            ipv4: search by IPv4 address
            ipv6: search by IPv6 address (compressed or uncompressed)
            location: search by location
            hostname: search by hostname
            device_id: exact match by device-id
        :param query: If searching by, then this will be used as the input.
        :return:
        """

        data = dict()

        if filter_type is not None:
            data['type'] = filter_type

        if query is not None:
            data['query'] = query

        devices_list = self._make_request("GET", "/devices", data)

        devices = []

        if devices_list is not None:
            for device in devices_list['devices']:
                devices.append(Device(device))

            return devices

    def get_device(self, hostname: str):

        device = self._make_request("GET", "/devices" + "/" + hostname, dict())

        if device is not None:
            return Device(device['devices'][0])
            # return device

    def get_ospf_nbr(self):

        result = self._make_request("GET", "/ospf", dict())

        ospf_nbr = []

        if result is not None:
            ospf_nbr = [OspfNbrResult(x) for x in result['ospf_neighbours']]

        return ospf_nbr

    def get_oxidized_config(self, hostname: str):
        device_config = self._make_request(
            "GET", "/oxidized/config" + "/" + hostname, dict())

        if device_config is not None:
            return device_config['config']

    def search_oxidized(self, search_string: str):
        data = self._make_request(
            "GET", "/oxidized/config/search" + "/" + search_string, dict())

        if data["status"] == "ok":
            nodes = [SearchOxidizedResult(node) for node in data['nodes']]
            data["nodes"] = nodes
        return data

        # else:
        #     return data

    def search_ports(self, search_string: str, field=None):
        """
        Search for ports matching the query.
        :param search_string: search string to search in fields
        :param field: ifAlias, ifDescr, and ifName
        :return:
        """

        if field is not None:
            search_result = self._make_request(
                "GET", "/ports/search" + "/" + field + "/" + search_string, dict())
        else:
            search_result = self._make_request(
                "GET", "/ports/search" + "/" + search_string, dict())

        if search_result is not None:
            return search_result['ports']

    def get_port_info(self, port_id: int):
        port_info = self._make_request(
            "GET", "/ports" + "/" + str(port_id), dict())

        if port_info is not None:
            return Port(port_info['port'][0])
