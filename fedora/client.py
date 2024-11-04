from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
import lxml.etree as ET

class FedoraClient(object):
    url = None
    username = None
    password = None

    namespaces = {
        'apim': 'http://www.fedora.info/definitions/1/0/management/',
        'apia': 'http://www.fedora.info/definitions/1/0/access/'
    }

    def __init__(self, url, username=None, password=None):
        parsed_url = urlparse(url)
        self.url = url.rstrip('/')
        self.username = username
        self.password = password

    def _resolve_pid(self, pid):
        return self.url + '/objects/' + pid

    def _resolve_datastream(self, pid, dsid):
        return self._resolve_pid(pid) + '/datastreams/' + dsid

    def list_datastreams(self, pid, profiles=False):
        """
        List the datastreams for a given pid
        :param pid: The pid of the object
        :param profiles: Whether to return the datastream profiles
        :return: A list of datastream objects
        """
        url = self._resolve_pid(pid) + '/datastreams?format=xml'
        if profiles:
            url += '&profiles=true'
        response = requests.get(url, auth=(self.username, self.password))
        datastreams = []
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            if profiles:
                data = root.findall('.//apia:datastreamProfile', self.namespaces)
                for ds in data:
                    dsid = ds.attrib.get('dsID')
                    label = ds.find('.//apim:dsLabel', self.namespaces).text
                    version = int(ds.find('.//apim:dsVersionID', self.namespaces).text.replace(dsid + '.', ''))
                    state = ds.find('.//apim:dsState', self.namespaces).text
                    mimetype = ds.find('.//apim:dsMIME', self.namespaces).text
                    size = int(ds.find('.//apim:dsSize', self.namespaces).text)
                    control_group = ds.find('.//apim:dsControlGroup', self.namespaces).text
                    location = ds.find('.//apim:dsLocation', self.namespaces).text
                    created_date = ds.find('.//apim:dsCreateDate', self.namespaces).text
                    datastreams.append(Datastream.create_from_profile(dsid, label, version, state, mimetype, size, control_group, location, created_date))
            else:
                data = root.findall('.//apia:datastream', self.namespaces)
                for ds in data:
                    dsid = ds.attrib.get('dsid')
                    label = ds.attrib.get('label')
                    mimetype = ds.attrib.get('mimeType')
                    datastreams.append(Datastream.create_from_list(dsid, label, mimetype))

        return datastreams

class Object:
    def __init__(self, pid: str):
        self.pid = pid
        self.datastreams = {}

    def add_datastream(self, datastream):
        if datastream.dsid not in self.datastreams:
            self.datastreams[datastream.dsid] = datastream

    def has_datastream(self, dsid):
        return dsid in self.datastreams

    def get_datastream(self, dsid):
        return self.datastreams.get(dsid)

class Datastream:
    def __init__(
            self,
            dsid: str,
            label: str,
            version: int,
            state: str,
            mimetype: str,
            size: int,
            control_group: str,
            location: str,
            created_date: str
    ):
        self.dsid = dsid
        self.label = label
        self.version = version
        self.state = state
        self.mimetype = mimetype
        self.size = int(size)
        self.control_group = control_group
        self.location = location
        self.created_date = datetime.strptime(created_date, '%Y-%m-%dT%H:%M:%S.%fZ')

    @staticmethod
    def create_from_profile(
            dsid: str,
            label: str,
            version: int,
            state: str,
            mimetype: str,
            size: int,
            control_group: str,
            location: str,
            created_date: str
    ):
        return Datastream(dsid, label, version, state, mimetype, size, control_group, location, created_date)

    @staticmethod
    def create_from_list(
            dsid: str,
            label: str,
            mimetype: str,
    ):
        return Datastream(dsid, label, -9, '', mimetype, -9 , '', '', datetime.now(tz=timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

    def __str__(self):
        return f"Datastream: {self.dsid} - {self.mimetype} - {self.size} bytes"

    def get_created_date(self):
        return self.created_date
