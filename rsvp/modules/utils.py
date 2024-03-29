import yaml
import urllib.parse
import jinja2
import socket
import os



def yml_load(x):
    with open(x) as f:
        try:
            return yaml.load(f, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            print(exc)


def str_to_url(string):
    return urllib.parse.quote(string)


def jinja2_load(filename):
    with open(filename) as t:
        return jinja2.Template(t.read())

def resolve(hostname):
    return socket.gethostbyname(hostname + '.as43531.net')
