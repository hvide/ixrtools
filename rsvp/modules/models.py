import typing


class Device:
    def __init__(self, device_info: typing.Dict):
        self.device_id: int = device_info['device_id']
        self.disabled: bool = device_info['disabled']
        # self.hostname: str = ".".join(device_info['hostname'].split(".", 3)[:3])
        self.hostname: str = device_info['hostname']
        self.ip: str = device_info['ip']
        self.status: str = device_info['status']
        self.sysName: str = device_info['sysName']
        self.version: str = device_info['version']
        self.hardware: str = device_info['sysDescr'].split(' ', 3)[1][1:-1] \
                                if device_info['os'] == "xos" \
                                else device_info['hardware']
        self.serial: str = device_info['serial']
        self.sysDescr: str = device_info['sysDescr']

    def to_dict(self) -> typing.Dict:
        return {
            'device_id': self.device_id,
            'disabled': self.disabled,
            'hostname': self.hostname,
            'status': self.status,
            'sysName': self.sysName,
            'sysDescr': self.sysDescr,
            'hardware': self.hardware,
            'ip': self.ip,
            'version': self.version,
            'serial': self.serial
        }

    def __repr__(self):
        return str(self.hostname)


class SearchOxidizedResult:
    def __init__(self, search_oxidized_result: typing.Dict):
        self.dev_id: int = search_oxidized_result['dev_id']
        self.full_name: str = search_oxidized_result['full_name']
        self.node: str = search_oxidized_result['node']

    def to_dict(self) -> typing.Dict:
        return {
            'device_id': self.dev_id,
            'hostname': self.full_name,
            'sysName': self.node,
        }

    def __repr__(self):
        return self.full_name


class OspfNbrResult:
    def __init__(self, neighbour: typing.Dict):
        self.device_id: int = neighbour['device_id']
        self.ospfNbrIpAddr: str = neighbour['ospfNbrIpAddr']
        self.ospfNbrRtrId: str = neighbour['ospfNbrRtrId']
        self.ospfNbrState: str = neighbour['ospfNbrState']

    def to_dict(self) -> typing.Dict:
        return {
            'device_id': self.device_id,
            'ospfNbrIpAddr': self.ospfNbrIpAddr,
            'ospfNbrRtrId': self.ospfNbrRtrId,
            'ospfNbrState': self.ospfNbrState,
        }

    def __repr__(self):
        return str(self.device_id)



# class RsvpLsp:
#     def __init__(self, data: typing.Dict):
#         self.source_ip = data['source_hostname']
#         self.source_hostname = data['source_hostname']
#         self.destination_ip = data['destination_ip']
