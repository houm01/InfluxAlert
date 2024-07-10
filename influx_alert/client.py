

from .endpoints.ping import PingEndpoint
from .endpoints.vmware import VMWareEndpoint
from influxdb import InfluxDBClient
import urllib3
urllib3.disable_warnings()
from pymongo import MongoClient


class BaseClient:
    
    def __init__(self, 
                 influx_host, 
                 influx_port,
                 influx_username,
                 influx_password,
                 influx_database,
                 influx_ssl):
        
        self._influx_host = influx_host
        self._influx_port = influx_port
        self._influx_username = influx_username
        self._influx_password = influx_password
        self._influx_database = influx_database
        self._influx_ssl = influx_ssl
    
        self.influx_client = self._build_influxdb_client()
    
        self.ping = PingEndpoint(self)
        self.vmware = VMWareEndpoint(self)
        

    def _build_influxdb_client(self):
        pass

    def mongodb_client(self):
        pass
    
class Client(BaseClient):
    def _build_influxdb_client(self):
        return InfluxDBClient(host=self._influx_host, 
                        port=self._influx_port,
                        username=self._influx_username,
                        password=self._influx_password,
                        database=self._influx_database,
                        ssl=self._influx_ssl)
        
    def mongodb_client(self):
        client = MongoClient(host='',
                             port=27017,
                             username='infra',
                             password='',
                             authSource='infra-python')
        return client[database_name][collection] 