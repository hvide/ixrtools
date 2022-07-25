import typing
import os
from .nmsclient import NmsClient

import logging
from .utils import jinja2_load, resolve

from pprint import pprint

logger = logging.getLogger()

DIR = os.path.dirname(os.path.realpath(__file__)) + '/'


class RsvpClient(NmsClient):
    def __init__(self, api_key: str, base_url: str, verify: bool = True):
        super().__init__(api_key, base_url, verify)

    def _nexthop_map(self):
        ospf_nbrs = self.get_ospf_nbr()
        d = dict()
        for ospf_nbr in ospf_nbrs:
            d[ospf_nbr.ospfNbrIpAddr] = ospf_nbr.port_id
        return d

    def _get_device_by_int_ip(self, nexthop_ip):
        devices = self.get_devices(filter_type="ipv4", query=nexthop_ip)
        device = [d for d in devices if d.status]

        if len(device) > 1:
            logger.warning(
                "more then two devices with te same IP were found: {}".format(device))
            return

        return device[0]

    def get_rsvp_path_info(self, search_string):

        search_result = self.search_oxidized(search_string)
        # pprint(search_result)

        if search_result['status'] == "ok":
            data = {
                'status': 'ok',
                'content': {
                    'paths': [],
                },
            }

            nexthops = self._nexthop_map()
            # pprint(nexthops)

            for node in search_result["nodes"]:

                path = dict()

                device = self.get_device(node.full_name)

                path['src_hostname'] = '.'.join(device.hostname.split(".")[:3])
                path['src_ip'] = device.ip

                config = self.get_oxidized_config(device.hostname).splitlines()
                hops = []

                create_mpls_rsvp_path = (
                    'create mpls rsvp-te path "%s"' % search_string)
                mpls_rsvp_path_exist = False
                mpls_rsvp_path = (
                    'configure mpls rsvp-te path %s add ero' % search_string)

                for line in config:

                    if create_mpls_rsvp_path in line:
                        mpls_rsvp_path_exist = True

                    hop = dict()
                    if mpls_rsvp_path_exist:
                        if mpls_rsvp_path in line:
                            line_split = line.split()
                            hop['order'] = line_split[-1]
                            hop['hop_type'] = line_split[-3]
                            hop['nexthop_ip'] = line_split[-4]

                            try:
                                nexthop_port_id = nexthops[line_split[-4].split("/")[
                                    0]]
                            except KeyError as e:
                                logger.error(f"Next hop IP: {e} is not in ospf. The path: {search_string} "
                                             f"on device: {device.hostname} is probably 'down'.")
                                path["status"] = "error"
                                path["data"] = f"Next hop IP: {e} is not in ospf. The path: {search_string} " \
                                    f"on device: {device.hostname} is probably 'down'."
                                return path

                            # device = self._get_device_by_int_ip(nexthop_ip)
                            device_id = self.get_port_info(
                                nexthop_port_id).device_id

                            hop['nexthop_hostname'] = self.get_device(
                                str(device_id)).hostname
                            hop['nexthop_hostname_short'] = ".".join(
                                self.get_device(str(device_id)).hostname.split(".")[:3])
                            hops.append(hop)
                            logger.debug(hop)
                        path['hops'] = hops

                        if not path['hops']:
                            path['path_type'] = 'ldp'
                        else:
                            path['path_type'] = 'rsvp-te'
                    # else:
                    #     continue

                data['content']['search_string'] = search_string
                # status = "ok"
                # path["status"] = "ok"
                data['content']['paths'].append(path)

            return data

        else:
            logger.warning(f"{search_result}")
            return search_result

    def create_rsvp_path(self, path_name: str, path_hops: typing.List, backward=False) -> typing.List:

        if backward:
            path_hops = list(reversed(path_hops))

        path = dict()
        path['name'] = path_name

        # Remove empty line in path_hops
        for i, x in enumerate(path_hops):
            if x == '':
                path_hops.pop(i)

        print(path_hops)

        hops = []
        if path_hops is not None:
            for i in range(len(path_hops) - 1):

                ports = self.search_ports(
                    path_hops[i].replace(".", "_") + " rtif", 'ifName')

                i += 1

                device = self.get_device(path_hops[i] + self.domain)

                x = [port['device_id'] for port in ports]
                if not device.device_id in x:
                    logger.warning(
                        f"Error {device.hostname} {device.device_id}")
                    return {'status': 'error', 'data': f"Error: Couldn't find the interface on <b>{path_hops[i]}</b> towards <b>{path_hops[i - 1 ]}</b></br> Try checking the port description on {path_hops[i]}."}

                for port in ports:

                    try:
                        if port['device_id'] == device.device_id:
                            ip = port['ifName'].split("(")[1].split("/")[0]
                            hop = {'device': device.hostname, 'ip': ip,
                                   'order_number': (i - 1) * 10 + 100}
                            hops.append(hop)
                    except AttributeError as e:
                        logger.error("Error: {} - Port {} doesn't belong to device: {} id: {}. Check that the Device name is correct".format(
                            e, port, device.hostname, device.device_id))

        logging.info(hops)
        path['hops'] = hops
        template = jinja2_load(DIR + "/rsvp_path.j2")
        t = template.render(path)
        lines = t.split("\n")
        return {'status': 'ok', 'data': lines}
        # return {'status': 'error', 'content': "Test error"}

    def create_rsvp_lsp(self, lsp_name: str, hostname: str) -> typing.List:

        destination = resolve(hostname)

        data = {
            'lsp_name': lsp_name,
            'destination': destination,
        }

        template = jinja2_load(DIR + "/rsvp_lsp.j2")
        t = template.render(data)
        lines = t.split("\n")
        return {'status': 'ok', 'data': lines}

    def attach_path_to_lsp(self, lsp_name: str, path_name: str, primary: bool) -> typing.List:

        if primary:
            pri_sec = "primary"
        else:
            pri_sec = "secondary"

        data = {
            'lsp_name': lsp_name,
            'path_name': path_name,
            'pri_sec': pri_sec,
        }

        template = jinja2_load(DIR + "/attach_path_to_lsp.j2")
        t = template.render(data)
        lines = t.split("\n")
        return {'status': 'ok', 'data': lines}
