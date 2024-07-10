# ping_alert_strategy.py

from .alert_strategy_base import AlertStrategyBase

class PingAlertStrategy(AlertStrategyBase):
    def __init__(self, influx_auth, webhook_url):
        super().__init__(influx_auth, webhook_url)

    def unreachable(self):
        # 实现对 ping 表的分析逻辑，并触发告警
        
        print("Analyzing ping data...")
        # Implement your alert logic here
        
        self.utils_test()
        

