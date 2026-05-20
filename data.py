from dotenv import load_dotenv
load_dotenv()

class Api:
    def fred(self):
        from fredapi import Fred
        return Fred()

    def av_ts(self):
        from alpha_vantage.timeseries import TimeSeries
        return TimeSeries(output_format='pandas')

    def av_fx(self):
        from alpha_vantage.foreignexchange import ForeignExchange
        return ForeignExchange(output_format='pandas')

    def av_ti(self):
        from alpha_vantage.techindicators import TechIndicators
        return TechIndicators(output_format='pandas')
    
api = Api()
