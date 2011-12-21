# VOEvent transport protocol messages.
# John Swinbank, <swinbank@transientskp.org>, 2011.

import xml.etree.ElementTree as etree
from datetime import datetime

LOCAL_IVO = "ivo://lofar/transients"

etree.register_namespace("trn", "http://www.telescope-networks.org/xml/Transport/v1.1")

class TransportMessage(object):
    def __init__(self):
        self.root_element = etree.Element("{http://www.telescope-networks.org/xml/Transport/v1.1}Transport",
            attrib={
                "version": "1.0",
                "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "xsi:schemaLocation": "http://telescope-networks.org/schema/Transport/v1.1 http://www.telescope-networks.org/schema/Transport-v1.1.xsd"
            }
        )
        timestamp = etree.SubElement(self.root_element, "TimeStamp")
        timestamp.text = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

    def to_string(self):
        return etree.tostring(self.root_element)

class OriginResponseMessage(TransportMessage):
    def __init__(self, remote_ivo):
        super(OriginResponseMessage, self).__init__()
        origin = etree.SubElement(self.root_element, "Origin")
        origin.text = remote_ivo
        response = etree.SubElement(self.root_element, "Response")
        response.text = LOCAL_IVO

class IAmAlive(TransportMessage):
    def __init__(self):
        super(IAmAlive, self).__init__()
        self.root_element.set("role", "iamalive")
        origin = etree.SubElement(self.root_element, "Origin")
        origin.text = LOCAL_IVO

class IAmAliveResponse(OriginResponseMessage):
    def __init__(self, remote_ivo):
        super(IAmAliveResponse, self).__init__(remote_ivo)
        self.root_element.set("role", "iamalive")

class Ack(OriginResponseMessage):
    def __init__(self, remote_ivo):
        super(Ack, self).__init__(remote_ivo)
        self.root_element.set("role", "ack")
