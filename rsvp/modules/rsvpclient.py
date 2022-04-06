import typing

from .nmsclient import NmsClient

import logging
from .utils import jinja2_load

from pprint import pprint

logger = logging.getLogger()


class RsvpClient(NmsClient):
    def __init__(self, api_key: str, base_url: str, verify: bool = True):
        super().__init__(api_key, base_url, verify)

    def _nexthop_map(self):
        ospf_nbrs = self.get_ospf_nbr()
        d = dict()
        for ospf_nbr in ospf_nbrs:
            d[ospf_nbr.ospfNbrIpAddr] = ospf_nbr.ospfNbrRtrId

        return d

    def get_rsvp_lsp_info(self, search_string):
        search_result = self.search_oxidized(search_string)
        data = dict()

        if search_result is not None:

            for node in search_result:
                hostname = node['node']
                device = self.get_device(hostname)

                data['src_hostname'] = device.hostname
                data['src_ip'] = device.ip

                config = self.get_oxidized_config(hostname).splitlines()
                for line in config:

                    mpls_create_lsp = ('create mpls rsvp-te lsp "%s"' % search_string)
                    mpls_add_path = ('configure mpls rsvp-te lsp "%s" add path' % search_string)

                    if mpls_create_lsp in line:
                        dst_ip = line.split()[-1]
                        data['dst_ip'] = dst_ip
                        data['dst_hostname'] = self.get_devices('ipv4', dst_ip)[0].hostname

                    if mpls_add_path in line:
                        if line.endswith('primary'):
                            data['path_primary'] = line.split()[7].strip('"')
                        if line.endswith('secondary'):
                            data['path_secondary'] = line.split()[7].strip('"')

            return data

    def get_rsvp_path_info(self, search_string):

        search_result = self.search_oxidized(search_string)
        data = dict()

        if search_result is not None:

            nexthops = self._nexthop_map()

            for node in search_result:
                # hostname = node['node']
                device = self.get_device(node.full_name)

                data['src_hostname'] = device.hostname
                data['src_ip'] = device.ip

                config = self.get_oxidized_config(device.hostname).splitlines()
                hops = []

                create_mpls_rsvp_path = ('create mpls rsvp-te path "%s"' % search_string)
                mpls_rsvp_path_exist = False
                mpls_rsvp_path = ('configure mpls rsvp-te path %s add ero' % search_string)

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
                            # device_id = self.search_ports(line_split[-4].split("/")[0], "ifName")[0]['device_id']
                            nexthop_ip = nexthops[line_split[-4].split("/")[0]]
                            devices = self.get_devices(filter_type="ipv4", query=nexthop_ip)
                            device = [d for d in devices if d.status]

                            if len(device) > 1:
                                logger.warning("more then two devices with te same IP were found: {}".format(device))

                            device = device[0]

                            hop['nexthop_hostname'] = self.get_device(str(device.device_id)).hostname
                            hop['nexthop_hostname_short'] = ".".join(self.get_device(str(device.device_id)).hostname.split(".")[:3])
                            hops.append(hop)
                            logger.debug(hop)
                        data['hops'] = hops

                        if not data['hops']:
                            data['path_type'] = 'ldp'
                        else:
                            data['path_type'] = 'rsvp-te'
                    # else:
                    #     continue

                return data

    def create_rsvp_path(self, path_name: str, path_hops: typing.List, backward=False):

        if backward:
            path_hops = list(reversed(path_hops))

        path = dict()
        path['name'] = path_name

        hops = []
        if path_hops is not None:
            for i in range(len(path_hops) - 1):

                ports = self.search_ports(path_hops[i].replace(".", "_") + " rtif", 'ifName')

                i += 1

                device = self.get_device(path_hops[i] + self.domain)

                for port in ports:

                    try:
                        if port['device_id'] == device.device_id:
                            ip = port['ifName'].split("(")[1].split("/")[0]
                            hop = {'device': device.hostname, 'ip': ip, 'order_number': i * 10 + 100}
                            hops.append(hop)
                    except AttributeError as e:
                        logger.error("Error: {} - Port {} doesn't belong to device: {} id: {}. Check that the Device name is correct".format(e, port, device.hostname, device.device_id))

                # else:
                #     logger.info("P2P interface not found between device name: %s id: %s and %s" % (device.hostname, device.device_id, ports))

        logging.info(hops)
        path['hops'] = hops
        template = jinja2_load("/Users/dgilardoni/PycharmProjects/ixrtools/rsvp/modules/rsvp_path.j2")
        t = template.render(path)
        t = t.split("\n")
        return t
