#!/usr/bin/env python3


class Utils:
    
    def utils_test(self):
        print('utils test')
        

class AlertStrategyBase(Utils):
    def __init__(self, influx_auth, webhook_url):
        self.influx_auth = influx_auth
        self.webhook_url = webhook_url

    def analyze(self):
        raise NotImplementedError("Subclasses should implement this method.")