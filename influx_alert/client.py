

from .endpoints.ping import PingEndpoint
from .endpoints.vmware import VMWareEndpoint
from .endpoints.no_data import NoDataEndpoint
from .endpoints.extensions import ExtensionsEndpoint
from influxdb import InfluxDBClient
import urllib3
urllib3.disable_warnings()
from pymongo import MongoClient
from cc_feishu.client import Client as FeishuClient



class BaseClient:
    
    def __init__(self, 
                 influx_host, 
                 influx_port,
                 influx_username,
                 influx_password,
                 influx_database,
                 influx_ssl,
                 mongo_host,
                 mongo_port,
                 mongo_username,
                 mongo_password,
                 mongo_authsource,
                 mongo_database,
                 feishu_app_id,
                 feishu_app_secret,
                 wecom_webhook_url):
        
        self._influx_host = influx_host
        self._influx_port = influx_port
        self._influx_username = influx_username
        self._influx_password = influx_password
        self._influx_database = influx_database
        self._influx_ssl = influx_ssl

        self._mongo_host = mongo_host
        self._mongo_port = mongo_port
        self._mongo_username = mongo_username
        self._mongo_password = mongo_password
        self._mongo_authsource = mongo_authsource
        self._mongo_database = mongo_database
    
        # self.webhook_url = webhook_url
        self.feishu_app_id = feishu_app_id
        self.feishu_app_secret = feishu_app_secret
        
        self.wecom_webhook_url = wecom_webhook_url
        
        self.influx_client = self._build_influxdb_client()
        self.mongo_client = self._build_mongo_client()
        self.feishu_client = self._build_feishu_client()

        self.ping = PingEndpoint(self)
        self.vmware = VMWareEndpoint(self)
        self.extensions = ExtensionsEndpoint(self)
        self.no_data = NoDataEndpoint(self)
        

    def _build_influxdb_client(self):
        pass

    def _build_mongo_client(self):
        pass
    
    def _build_feishu_client(self):
        pass

class Client(BaseClient):
    def _build_influxdb_client(self):
        return InfluxDBClient(host=self._influx_host, 
                        port=self._influx_port,
                        username=self._influx_username,
                        password=self._influx_password,
                        database=self._influx_database,
                        ssl=self._influx_ssl)
        
    def _build_mongo_client(self):
        client = MongoClient(host=self._mongo_host,
                             port=self._mongo_port,
                             username=self._mongo_username,
                             password=self._mongo_password,
                             authSource=self._mongo_authsource)
        
        return client['automate']['alert'] 
    
    def _build_feishu_client(self):
        return FeishuClient(app_id=self.feishu_app_id, app_secret=self.feishu_app_secret)
    