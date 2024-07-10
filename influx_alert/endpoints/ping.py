from ..endpoint import Endpoint


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
        results = self.parent.influx_client.query(QUERY)
        for result in results:
            print(result)
        
    