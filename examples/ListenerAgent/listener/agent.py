

from __future__ import absolute_import

from datetime import datetime
import logging
import sys

from pprint import pformat

from volttron.platform.messaging.health import STATUS_GOOD
from volttron.platform.vip.agent import Agent, Core, PubSub, compat
from volttron.platform.agent import utils
from volttron.platform.messaging import headers as headers_mod
import importlib
import random
import json
import socket
import pyrebase
import urllib3
import time
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import re
from uuid import getnode

utils.setup_logging()
_log = logging.getLogger(__name__)
__version__ = '3.2'
DEFAULT_MESSAGE = 'Listener Message'
DEFAULT_AGENTID = "listener"
DEFAULT_HEARTBEAT_PERIOD = 5

try:
    config = {
        "apiKey": "AIzaSyAY_DKJdz09U3OvDaQ4QjF1dEI2yyvxifI",
        "authDomain": "guidekub-ff865.firebaseapp.com",
        "databaseURL": "https://guidekub-ff865.firebaseio.com",
        "storageBucket": "guidekub-ff865.appspot.com",
    }
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()
except Exception as er:
    print er

class Gpub(Agent):
    """Listens to everything and publishes a heartbeat according to the
    heartbeat period specified in the settings module.
    """

    def __init__(self, config_path, **kwargs):
        super(Gpub, self).__init__(**kwargs)
        self.config = utils.load_config(config_path)
        self._agent_id = self.config.get('agentid')
        self._message = self.config.get('message')
        self._heartbeat_period = self.config.get('heartbeat_period',
                                                 DEFAULT_HEARTBEAT_PERIOD)
        try:
            self._heartbeat_period = int(self._heartbeat_period)
        except:
            _log.warn('Invalid heartbeat period specified setting to default')
            self._heartbeat_period = DEFAULT_HEARTBEAT_PERIOD
        log_level = self.config.get('log-level', 'INFO')
        if log_level == 'ERROR':
            self._logfn = _log.error
        elif log_level == 'WARN':
            self._logfn = _log.warn
        elif log_level == 'DEBUG':
            self._logfn = _log.debug
        else:
            self._logfn = _log.info

    @Core.receiver('onsetup')
    def onsetup(self, sender, **kwargs):
        # Demonstrate accessing a value from the config file
        _log.info(self.config.get('message', DEFAULT_MESSAGE))
        self._agent_id = self.config.get('agentid')

    @Core.receiver('onstart')
    def onstart(self, sender, **kwargs):
        _log.debug("VERSION IS: {}".format(self.core.version()))
        self.onstart2()
        print "start"


    @PubSub.subscribe('pubsub', '')
    def on_match(self, peer, sender, bus,  topic, headers, message):
        """Use match_all to receive all messages and print them out."""
        if sender == 'pubsub.compat':
            message = compat.unpack_legacy_message(headers, message)
        self._logfn(
            "Peer: %r, Sender: %r:, Bus: %r, Topic: %r, Headers: %r, "
            "Message: \n%s", peer, sender, bus, topic, headers,  pformat(message))

    @Core.periodic(5)
    def deviceMonitorBehavior2(self):

        try:
            # to get physical address:
            original_mac_address = getnode()
            print("MAC Address: " + str(original_mac_address))  # this output is in raw format

            # convert raw format into hex format
            hex_mac_address = str(":".join(re.findall('..', '%012x' % original_mac_address)))
            print("HEX MAC Address: " + hex_mac_address)
            mac = hex_mac_address.replace(':', '')
            print mac
        except:
            mac = "AAAA"

        try:
            db.child(mac).child('datetime').child("dt").set(
                datetime.now().replace(microsecond=0).isoformat())
            print "---------------update firebase ok"
        except Exception as er:
            print er

    def onstart2(self):

        print "on match start"
        try:
            # to get physical address:
            original_mac_address = getnode()
            print("MAC Address: " + str(original_mac_address))  # this output is in raw format

            # convert raw format into hex format
            hex_mac_address = str(":".join(re.findall('..', '%012x' % original_mac_address)))
            print("HEX MAC Address: " + hex_mac_address)
            mac = hex_mac_address.replace(':', '')
            print mac
        except:
            mac = "AAAA"


        try:
            db.child(mac).child('starttime').child("dt").set(
                datetime.now().replace(microsecond=0).isoformat())
            print "---------------update firebase ok"
        except Exception as er:
            print er



def main(argv=sys.argv):
    '''Main method called by the eggsecutable.'''
    try:
        utils.vip_main(Gpub, version=__version__)
    except Exception as e:
        _log.exception('unhandled exception')


if __name__ == '__main__':
    # Entry point for script
    sys.exit(main())
