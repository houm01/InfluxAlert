from ..endpoint import Endpoint
from nb_log import get_logger

log = get_logger('no_data')


ALARM_NAME_NO_DATA = '无监控数据'


class NoDataEndpoint(Endpoint):
    
    def node_exporter(self):
        query = """select
    *
    from node_uname_info 
    where time > now() - 1d 
    group by "url"
    order by desc
    limit 1"""
        
        log.debug(f'query: [{query.strip()}]')
        for results in self.parent.influx_client.query(query=query):
            diff_now = self.parent.extensions.time_diff_influx_now(source_time=results['time'])
            log.debug(diff_now)
            
            if diff_now > 3:
                nodename = results['nodename']
                
                for url_dict in self.parent.influx_client.query(f"""select * from node_uname_info where "nodename" = '{nodename}' order by time desc limit 1"""):
                    url = url_dict['url']
                
                self.parent.extensions.tool_check_insert_send_mongo(
                    restore_influx=f"""select last(*) from node_uname_info where "url" = '{url}'""",
                    alarm_content= results['nodename'] + ' ' + url.replace('http://', '').replace(':9100/metrics', '') + ' ' + ALARM_NAME_NO_DATA,
                    alarm_name=ALARM_NAME_NO_DATA,
                    priority='高',
                    entity_name=nodename,
                    is_notify=True)


        for mongo_item in self.parent.extensions.mongo_query_trigger(alarm_name=ALARM_NAME_NO_DATA):
            log.debug('恢复语法: ' + mongo_item['restore_influx'])
            
            for results in self.parent.influx_client.query(mongo_item['restore_influx']):
                log.debug(results)
                
                diff_now = self.parent.extensions.time_diff_influx_now(source_time=results['time'])
                nodename = mongo_item['entity_name']
                
                if diff_now < 3:
                    self.parent.extensions.tool_check_insert_send_mongo(mongo_id = mongo_item['_id'],
                        event_type='trigger',
                        alarm_content= mongo_item['alarm_content'],
                        alarm_name=ALARM_NAME_NO_DATA,
                        priority='高',
                        entity_name=nodename,
                        is_notify=True)
                    
    def trigger_windows_exporter(self):
        query = """select
*
from windows_cs_hostname 
where time > now() - 1d 
group by "url"
order by desc
limit 1"""
        
        log.debug(f'query: [{query.strip()}]')
        for results in self.parent.influx_client.query(query=query):
            hostname = results['hostname']
            diff_now = self.parent.extensions.time_diff_influx_now(source_time=results['time'])
            log.debug(f'{hostname} {diff_now}')
            if diff_now > 5:
                
                
                for url_dict in self.parent.influx_client.query(f"""select * from windows_cs_hostname where "hostname" = '{hostname}' order by time desc limit 1"""):
                    url = url_dict['url']
                
                self.parent.extensions.tool_check_insert_send_mongo(
                    restore_influx=f"""select last(*) from windows_cs_hostname where "url" = '{url}'""",
                    alarm_content= results['hostname'] + ' ' + url.replace('http://', '').replace(':9182/metrics', '') + ' ' + ALARM_NAME_NO_DATA,
                    alarm_name=ALARM_NAME_NO_DATA,
                    priority='高',
                    entity_name=hostname,
                    is_notify=True)

        for mongo_item in self.parent.extensions.mongo_query_trigger(alarm_name=ALARM_NAME_NO_DATA):
            log.debug('恢复语法: ' + mongo_item['restore_influx'])
            
            for results in self.parent.influx_client.query(mongo_item['restore_influx']):
                log.debug(results)
                
                diff_now = self.parent.extensions.time_diff_influx_now(source_time=results['time'])
                hostname = mongo_item['entity_name']
                
                if diff_now < 3:
                    self.parent.extensions.tool_check_insert_send_mongo(
                        mongo_id = mongo_item['_id'],
                        event_type='resolved',
                        alarm_content= mongo_item['alarm_content'],
                        alarm_name=ALARM_NAME_NO_DATA,
                        priority='高',
                        entity_name=hostname,
                        is_notify=True)