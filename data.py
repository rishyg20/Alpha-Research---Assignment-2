from sip.alpha import *

class Api:
    def fred(self):
        from fredapi import Fred
        return Fred()

    def alpha_vantage_ts(self):
        from alpha_vantage.timeseries import TimeSeries
        return TimeSeries(output_format='pandas')

    def alpha_vantage_fx(self):
        from alpha_vantage.foreignexchange import ForeignExchange
        return ForeignExchange(output_format='pandas')

    def alpha_vantage_ti(self):
        from alpha_vantage.techindicators import TechIndicators
        return TechIndicators(output_format='pandas')
    
api = Api()
