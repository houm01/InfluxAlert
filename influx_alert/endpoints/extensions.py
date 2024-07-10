from ..endpoint import Endpoint
import pymongo
import uuid
from nb_log import get_logger
import pytz
import datetime
import time
import re
import requests
import json

log = get_logger('extensions')


class ExtensionsEndpoint(Endpoint):
    
    # def __init__(self):
    #     self.ALARM_NAME_PING_UNREACHABLE = 'Ping 不可达'
    #     self.ALARM_NAME_BFD_8 = 'BFD状态异常'
    #     self.ALARM_NAME_PORT_DOWN = '端口状态异常'
    #     self.ALARM_NAME_TRAFFIC = '流量告警'
    #     self.ALARM_BGP_STATUS = 'BGP状态异常'
    #     self.ALARM_NO_SNMP_DATA = '无SNMP监控数据'
    #     self.ALARM_NAME_UPS_STATUS = 'UPS状态异常'
        
    #     # upsAdvBatteryReplaceIndicator
    #     self.ALARM_NAME_upsAdvBatteryReplaceIndicator = 'UPS电池需要更换'

    #     self.EVENT_TYPE_TRIGGER = 'trigger'
    #     self.EVENT_TYPE_RESOLVED = 'resolved'

    #     self.PRIORITY_DISASTER = 'disaster'
    #     self.PRIORITY_HIGH = 'high'
    #     self.PRIORITY_WARNING = 'warning'
        
    #     self.PING_LIMIT = 8
    #     self.PING_RESOLVED = 5
    #     self.BFD_LIMIT = 8

    
    @staticmethod
    def convert_timeobj_to_str(timeobj: str=None, timezone_offset: int=8):
        time_obj_with_offset = timeobj + datetime.timedelta(hours=timezone_offset)
        return time_obj_with_offset.strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def convert_timeobj_to_str_date(timeobj):
        return timeobj.strftime("%Y-%m-%d")

    @staticmethod
    def get_now_date():
        '''
        _summary_

        Returns:
            _type_: _description_
        '''
        now = datetime.datetime.now()
        return now.strftime("%Y%m%d")
    
    @staticmethod
    def get_start_and_end_time(last_minute):

        # 获取当前时间戳（精度为秒）
        current_timestamp = int(time.time())

        # 将当前时间戳转换为毫秒级精度
        current_timestamp_ms = current_timestamp * 1000

        # 计算1分钟前的时间戳（精度为秒）
        start_timestamp = current_timestamp - last_minute * 60

        # 将1分钟前的时间戳转换为毫秒级精度
        start_timestamp_ms = start_timestamp * 1000

        # 打印结果
        return start_timestamp_ms, current_timestamp_ms
    
    @staticmethod
    def get_start_and_end_time_tz(last_minute):
        '''
        _summary_

        Args:
            offset (int): 输入秒数

        Returns:
            _type_: _description_
        '''
        
        current_time = datetime.datetime.utcnow() - datetime.timedelta(seconds= last_minute * 60)
        end_time = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        start_time = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        return end_time, start_time

    @staticmethod
    def convert_time(input_time):
        '''
        将时间对象转换为字符串

        Args:
            input_time (_type_): _description_

        Returns:
            _type_: _description_
        '''
        # 输入的时间字符串
        # input_time = "2024-04-17T23:21:35.362383Z"

        # 转换为 datetime 对象
        dt = datetime.datetime.strptime(input_time, "%Y-%m-%dT%H:%M:%S.%fZ")

        # 设置时区为 GMT+8
        timezone = pytz.timezone('Asia/Shanghai')
        dt = dt.replace(tzinfo=pytz.utc).astimezone(timezone)

        # 格式化为所需的字符串格式
        output_time = dt.strftime("%Y-%m-%d %H:%M:%S")

        return output_time

    @staticmethod
    def get_now_time(now: bool=True):
        current_time = datetime.datetime.now()  # 获取当前时间并加上8小时（对应+08:00时区）
        time_string = current_time.strftime("%Y-%m-%dT%H:%M:%S+08:00")  # 格式化时间字符串
        return time_string
    
    @staticmethod
    def get_now_timestamp():
        # current_time = time.time()
        # return int(datetime.datetime.now().timestamp())
        # microseconds = datetime.datetime.fromtimestamp(time.time()).microsecond
        return int(time.time() * 1000)
    
    def time_get_now_time_mongo(self):
        '''
        获取当前时间, 加入了时区信息, 简单是存储在 Mongo 中时格式为 ISODate

        Returns:
            current_time(class): 时间, 格式: 2024-04-23 16:48:11.591589+08:00
        '''
        current_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
        return current_time
    
    @staticmethod
    def convert_time_influx_to_tz(input_time):
        '''
        _summary_

        Args:
            input_time (_type_): _description_

        Returns:
            _type_: _description_
        '''
        # 转换为 datetime 对象
        dt = datetime.datetime.strptime(input_time, "%Y-%m-%dT%H:%M:%SZ")

        # 设置时区为 GMT+8
        timezone = pytz.timezone('Asia/Shanghai')
        dt = dt.replace(tzinfo=pytz.utc).astimezone(timezone)

        # 格式化为所需的字符串格式
        output_time = dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")

        return output_time

    @staticmethod
    def convert_time_influx_to_mongo(input_time):
        '''
        将 influxdb 中的时间转换为 mongo 的格式, 输入是 CMT+0 时区, 输出也是 GMT+0

        Args:
            input_time (_type_): TZ 格式, 时区是 GMT+0

        Returns:
            _type_: _description_
        '''
        # 转换为 datetime 对象
        if '.' in input_time:
            return datetime.datetime.strptime(input_time, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            return datetime.datetime.strptime(input_time, "%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def convert_str_to_obj(time_str):
        # date_string = '2024-06-01 09:00'
        timezone = pytz.timezone('Asia/Shanghai')

        # 将日期字符串转换为时间对象
        date_object = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M')

        # 设置时区
        date_object = timezone.localize(date_object)
        return date_object

    def time_diff_influx_now(self, source_time):
        '''
        计算influxdb默认的时间和当前时间的差异

        Args:
            source_time (_type_): _description_

        Returns:
            _type_: _description_
        '''
        current_time = datetime.datetime.utcnow()
        target_time = datetime.datetime.strptime(source_time, '%Y-%m-%dT%H:%M:%SZ')
        time_diff = current_time - target_time
        minutes_diff = int(time_diff.total_seconds() // 60)
        return minutes_diff


    
    def tool_check_insert_send_mongo(self,
                                    restore_influx: str=None,
                                    url: str=None,
                                    alarm_content: str=None,
                                    priority: str=None,
                                    event_id: str=str(uuid.uuid4()),
                                    alarm_name: str=None,
                                    entity_name: str=None,
                                    event_type: str='trigger',
                                    automate_ts: str='暂无',
                                    suggestion: str='请参考链接中的文档处理',
                                    referce_name: str='监控团队相关文档',
                                    referce_link: str='',
                                    alarm_time: str='',
                                    mongo_id: str=None,
                                    is_mongo: bool=True,
                                    is_notify: bool=True,
                                    is_send_ehc: bool=False,
                                    is_send_helpdesk: bool=False,
                                    mail_subject: str=None,
                                    mail_content: str=None):
            '''
            这个函数非常重要!!!
            将发送的告警或恢复事件写入到 InfluxDB, 并发送给 OneAlert

            Args:
                restore_influx (str): _description_
                url (str): _description_
                alarm_content (str): _description_
                priority (str): _description_
                alarm_name (str): _description_
                entity_name (str): _description_
                event_type (str): _description_
                automate_ts (str): _description_
                suggestion (str): _description_
                referce_name (str): _description_
                referce_link (str): _description_
                debug (bool): 如果开启, 告警不插入数据库也不发送到 Onealert
            '''
            if event_type == 'trigger':
                event_id = str(uuid.uuid4())

            # 如果为 True, 表示需要插入告警
            if self.mongo_check_alarm_exist(event_type=event_type, alarm_content=alarm_content):
                log.info(f'发现告警: [{alarm_content}], event_id: [{event_id}]')
                if is_mongo:
                    if event_type == 'trigger':
                        resp = self.mongo_insert_alert(
                            event_id=event_id,
                            alarm_content=alarm_content,
                            alarm_name=alarm_name,
                            priority=priority,
                            entity_name=entity_name,
                            restore_influx=restore_influx,
                            url=url,
                            alarm_time=alarm_time)

                        if resp:
                            log.info(f'已插入告警, alarm_content: [{alarm_content}]')
                        else:
                            log.error(f'告警插入到数据库时出错, alarm_content: [{alarm_content}]')
                        
                    elif event_type == 'resolved':
                        log.debug(f'发现告警恢复: [{alarm_content}]')
                        self.mongo_update_resolved(doc_id=mongo_id, resolved_time=self.time_get_now_time_mongo())
                        
                if is_notify:
                    # alert_dict = onealert.build_alert(
                    #     event_id=event_id,
                    #     event_type=event_type,
                    #     entity_name=entity_name,
                    #     alarm_name=alarm_name,
                    #     alarm_content=alarm_content,
                    #     priority=priority,
                    #     automate_ts=Troubleshoot.alert_counter(alarm_content) + '\n' +automate_ts,
                    #     suggestion=suggestion,
                    #     referce_name=referce_name,
                    #     referce_link=referce_link)

                        # onealert.send_notify_test(alert_dict=alert_dict)

                    # self.parent.feishu_send_card()
                    # self.parent.
                    self.parent.feishu_client.message.send_card(
                        template_id='ctp_AA6DQip4Ix5K',
                        template_variable={"title": alarm_content, "content": ""},
                        receive_id ='ou_ca3fc788570865cbbf59bfff43621a78'
                    )
                    
                    

    def mongo_check_alarm_exist(self, event_type, alarm_content) -> bool:
        '''
        _summary_

        Args:
            alarm_content (_type_): 告警内容

        Returns:
            bool: 如果为 True, 表示允许插入告警
        '''
        if event_type == 'trigger':
            query = { "alarm_content": alarm_content }
            fields = {"alarm_name": 1, "alarm_time": 1, "resolved_time": 1}
            # result = self.collection.find(query, fields).sort({ "_id": pymongo.DESCENDING }).limit(1)
            result = self.parent.mongo_client.find(query, fields).sort({ "_id": pymongo.DESCENDING }).limit(1)
            
            if self.parent.mongo_client.count_documents(query) == 0:
                # print("没有数据返回，执行插入数据")
                return True
            else:
                for doc in result:
                    if 'resolved_time' in doc:
                        # 当前没有告警, 可以插入数据
                        return True
        elif event_type == 'resolved':
            return True
    def mongo_insert_alert(self,
                     event_id,
                     alarm_content,
                     alarm_name,
                     priority,
                     entity_name,
                     restore_influx,
                     url,
                     alarm_time):
        '''
        插入告警到 MongoDB

        Args:
            event_id (_type_): _description_
            alarm_content (_type_): _description_
            alarm_name (_type_): _description_
            priority (_type_): _description_
            entity_name (_type_): _description_
            restore_influx (_type_): _description_
            url (_type_): _description_
            alarm_time (_type_): _description_
        '''
        data = {
            "event_id": event_id,
            "alarm_name": alarm_name,
            "alarm_content": alarm_content,
            "priority": priority,
            "restore_influx": restore_influx,
            "url": url,
            "alarm_time": alarm_time,
            "entity_name": entity_name
        }
        
        # 匹配 45xxx 和 45xxx-bboh
        pattern = r"45\d+(-\w+)?"
        
        try:
            storeid = re.search(pattern, alarm_content).group()
            data['storeid'] = storeid
        except Exception as e:
            log.error(f'匹配 [{alarm_content}] 出错, 无法获取到 storeid, {e}')
            
        log.debug(f'没有插入过数据, [{data}]')
        # resp = self.collection.insert_one(data)
        resp = self.parent.mongo_client.insert_one(data)
        log.debug(resp)
        return resp.acknowledged

    def mongo_update_resolved(self, doc_id, resolved_time):
        '''
        更新告警为解决

        Args:
            doc_id (_type_): _description_
            resolved_time (_type_): _description_

        Returns:
            _type_: _description_
        '''
        filter_doc = {"_id": doc_id}
        update = {"$set": { "resolved_time": resolved_time}}

        # 执行更新操作
        # return self.collection.update_one(filter_doc, update)
        return self.parent.mongo_client.update_one(filter_doc, update)
    
    def mongo_query_trigger(self, alarm_name):
        '''
        _summary_

        Returns:
            _type_: _description_
        '''
        query = {
            'alarm_name': alarm_name,
            'resolved_time': {'$exists': False}
        }
        # return self.collection.find(query)
        return self.parent.mongo_client.find(query)

    def notify_feishu_markdown(self):
        pass
    
    def notify_feishu_card(self):
        pass
    
    def notify_wecom_markdown(self, alert_dict):
        if alert_dict['eventType'] == 'trigger':
            title = '有新的告警, 请注意!'
            title_color = 'warning'
        else:
            title = '告警恢复!'
            title_color = 'info'
            
        content = f"""
        <font color=\"{title_color}\">{title}</font>\n 
        {alert_dict['alarmContent']} \n
        >告警名称: <font color=\"comment\">{alert_dict['alarmName']}</font> 
        >实例名称: <font color=\"comment\">{alert_dict['entityName']}</font> 
        >优先级: <font color=\"comment\">{alert_dict['priority']}</font> \n
        {alert_dict['details']}
        """

        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        resp = requests.request(method='POST',
                                url=self.parent.wecom_webhook_url, 
                                data=json.dumps(payload),
                                headers={'Content-Type': 'application/json'},
                                timeout=3)
        return resp.text


    def send_notify_wecom_card(self, alert_dict):
        print(alert_dict)
        
        if alert_dict['eventType'] == 'trigger':
            source_desc = '告警!'
            icon_url = "https://cdn-icons-png.flaticon.com/128/16750/16750201.png"
            desc_color = 2
        else:
            source_desc = '恢复!'
            icon_url = "https://cdn-icons-png.flaticon.com/128/8888/8888205.png"
            desc_color = 3
            
        card_content = {
            "msgtype":"template_card",
            "template_card":{
                "card_type":"text_notice",
                "source":{
                    "icon_url": icon_url,
                    "desc": source_desc,
                    "desc_color": desc_color
                },
                "main_title":{
                    "title": alert_dict['alarmContent'],
                    "desc":"待补充"
                },
                "sub_title_text": "待补充",
                "horizontal_content_list":[
                    {
                        "keyname":"alarmName",
                        "value": alert_dict['alarmName']
                    },
                    {
                        "keyname":"entityName",
                        "value": alert_dict['entityName'],
                    },
                    {
                        "keyname":"priority",
                        "value": alert_dict['priority'],
                    },     
                    {
                        "keyname":"details",
                        "value": alert_dict['details'].strip(),
                    },       
                ],
                "jump_list":[
                    {
                        "type":1,
                        "url":"https://work.weixin.qq.com/?from=openApi",
                        "title":"Grafana"
                    },

                ],
                "card_action":{
                    "type":1,
                    "url":"https://work.weixin.qq.com/?from=openApi",
                    "appid":"APPID",
                    "pagepath":"PAGEPATH"
                },
                # "quote_area":{
                #     "type":1,
                #     "url":"https://work.weixin.qq.com/?from=openApi",
                #     "appid":"APPID",
                #     "pagepath":"PAGEPATH",
                #     "title":"引用文本标题",
                #     "quote_text":"Jack：企业微信真的很好用~\nBalian：超级好的一款软件！"
                # },
            }
        }
        payload = json.dumps(card_content)
        # response = requests.request(method='POST', url='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ccb38d89-e63f-4be1-b620-b7c95cc76b43', data=payload, headers=self.headers, timeout=3)
        response2 = requests.request(method='POST',
                                     url='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=a7b5afa4-2deb-49b6-9e9f-2f55dcfabad1', 
                                     data=payload,
                                     headers=self.headers,
                                     timeout=3)
        
        response2 = requests.request(method='POST',
                                url='https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ccb38d89-e63f-4be1-b620-b7c95cc76b43',
                                data=payload,
                                headers=self.headers, 
                                timeout=3)
        return response2.text


    def notify_onealert(self):
        pass