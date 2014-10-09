import datetime
from datetime import timedelta
from _urllib2 import _urlopen
from pandas import DataFrame, concat, date_range, read_csv

from .exceptions import LimeInvaildQuery, LimeInvaildDate

class Lime:
    '''
    A simple API for extracting stock tick data
    '''
    def __init__(self, start_date, end_date, exchange, file_format='csv'):
        self.start_date = self.date_parse(start_date)
        self.end_date = self.date_parse(end_date)
        self._exchange = exchange
        self._file_format = file_format
        self._df = None
        self._exchange_found = False
        self._exchanges = {
            'Nasdaq': '.O',
            'Nyse': '.N',
            'Amex': '.A'
        }
        self._url = 'http://www.netfonds.no/quotes/tradedump.php'
        
    def get_exchange(self):
        ''' Returns the exchange chosen '''
        return self._exchange

    def initialize_start_date(self, date):
        '''
        Returns parsed todays date, a parsed supplied date
        '''
        if not date:
            date = datetime.date.today()
        return self.date_parse(date)

    def date_parse(self, date):
        '''
        Parses data to YYYY/MM/DD
        '''
        return date.strftime('%Y%m%d')

    def exchange_tracker(self, *args):
        '''
        modifies ticker with correct exchange extension
        '''
        try:
            split_results = self.ticker.split('.')
            if split_results[1] == ('O' or 'N' or 'A'):
                self._exchange_found = True

        except IndexError:
            self.ticker = "{}{}".format(self.ticker,
                                        self._exchanges[self._exchange.title()])
            self._exchange_found = True
            return self.ticker

    def efficient_ticker_retrieval(self):
        '''
        1 query way to get ticker data

        self, start_date, ticker, file_format
        '''        
        uri = '{}?date={}&paper={}&csv_format={}'.format(self._url,
                                                         self.start_date,
                                                         self.ticker,
                                                         self._file_format)
        print uri
        try:
            return read_csv(uri)
        except:
            return _urlopen(uri).read()
        
    def slow_ticker_retrieval(self):
        '''

        this should really be a uitlity function to find the exchange for a given ticker symbol


        finds ticker info w/o exchange info
        '''
        self._exchange_found = False

        for key in self._exchanges.keys():
            self.ticker = "{}{}".format(self.ticker, self._exchanges[key])
            self._df = self.efficient_ticker_retrieval()
            if self._df is not None and (len(self._df.columns) > 1):
                self._exchange_found = True
                self._exchange = key
                break

    def get_single(self, ticker):
        '''
        ticker, *args, **kwargs

        get stock prices
        '''
        self.ticker = ticker
        
        if self._exchange_found:
            self._df = self.efficient_ticker_retrieval()
        
        if not self._exchange_found:
            if self._exchange == '':
                self._df = self.slow_ticker_retrieval() 
            else:
                self.ticker = self._exchange_tracker()
                self._df = self.efficient_ticker_retrieval()
        
        if self._df is not None:
            self._df.time = self._df.time.apply(lambda x: datetime.datetime.strptime(x, '%Y%m%dT%H%M%S'))
            self._df = self._df.set_index(self._df.time)  
        else:
            raise LimeInvaildQuery()

    def get_many(self, begining_date, ticker, end_date):
        '''
        self, begining_date, end_date (optional), ticker

        start date is the day you want to start exctracting info from

        ie extract info :

        (start_date)    (end_date)
        May 21, 2013 to June 1, 2013

        Tick data only persits for 21 days! Any queries longer than that will fail

        If no end_date is specified then it defaults today
        '''
        self.ticker = ticker
        self.end_date = end_date
        self._exchange_found = False

        # generate warnings -- should be put into thier own methods
        if timedelta(0) > (end_date - begining_date) > timedelta(21):
            raise LimeInvaildDate(begining_date, end_date)

        # prep dates
        begining_date = self.date_parse(begining_date)

        if end_date == '':
            self.end_date = self.get_date_today()
        else:
            self.end_date = self.date_parse(end_date)

        # Get stock tick data
        for day in date_range(start=begining_date, end=self.end_date, freq='B'):
            self.start_date = self.date_parse(day)
            if self._df is not None:
                concat([self._df, self.get_single(self.ticker)])
            else:
                self._df = self.get_single(self.ticker)
        
