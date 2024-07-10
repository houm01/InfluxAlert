from ..endpoint import Endpoint
from nb_log import get_logger

log = get_logger('ping')


class PingEndpoint(Endpoint):
    
    def unreachable(self, limit: int=3):
        QUERY = f"""select
            "percent_packet_loss", 
            "name", 
            "url", 
            "result_code" 
            from ping 
            where time > now() - 1d 
            group by "url" 
            order by desc 
            limit {limit}"""
        
        log.debug(QUERY)
        
        for results in self.parent.influx_client.query(QUERY):
            has_loss = all(result['percent_packet_loss'] == 100.0 for result in results)
            if has_loss:
                r = results[0]
                url = r['url']
                alarm_content = '{} Ping不可达'.format(r['name'])
                log.info(f'发现告警: [{alarm_content}]')
                self.parent.extensions.tool_check_insert_send_mongo(
                    restore_influx=f"""select "percent_packet_loss" from ping where "url" = '{url}' order by time desc limit {limit}""",
                    url=url,
                    alarm_name='Ping 不可达',
                    entity_name=url,
                    alarm_content=alarm_content,
                    alarm_time=self.parent.extensions.time_get_now_time_mongo(),
                    priority='High',
                    is_notify=True)

        for mongo_item in self.parent.extensions.mongo_query_trigger(alarm_name='Ping 不可达'):
            for results in self.parent.influx_client.query(mongo_item['restore_influx']):
                # print(i)
                all_zero = all(result['percent_packet_loss'] == 0.0 for result in results)
                if all_zero:
                    self.parent.extensions.tool_check_insert_send_mongo(
                        event_type='resolved',
                        mongo_id=mongo_item['_id'],
                        event_id=mongo_item['event_id'],
                        entity_name=mongo_item['entity_name'],
                        alarm_name=mongo_item['alarm_name'],
                        alarm_content=mongo_item['alarm_content'],
                        priority=mongo_item['priority'],
                        is_notify=True)

    