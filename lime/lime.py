import datetime
from datetime import timedelta
from pandas import DataFrame, concat, date_range, read_csv

from .exceptions import LimeInvaildQuery, LimeInvaildDate, LimeInvaildTicker


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

    def check_date(self, start, end):
        ''' Checks wether supplied dates are accpable. '''
        if timedelta(0) > (end - start) > timedelta(21):
            raise LimeInvaildDate(start, end)
        return True

    def check_ticker_exchange_extenstion(self):
        ''' Checks if ticker has a valid exchange extension. '''
        extension = self.ticker.split('.')[1]
        if extension == ('O' or 'N' or 'A'):
            return True
        return False

    def check_ticker_exchange_extenstion(self):
        '''
        modifies ticker with correct exchange extension
        '''
        try:
            self.check_ticker_exchange_extenstion()
        except IndexError:
            ## TODO: Needs to be refactored
            self.ticker = "{}{}".format(self.ticker,
                                        self._exchanges[self._exchange.title()])
            self._exchange_found = True
            return self.ticker

    def get_exchange_from_ticker(self):
        '''
        Loops through the three exchanges Netfonds supports, Nasdaq; NYSE; Amex,
        and returns the correct exchange extension if it exists.
        '''
        for key in self._exchanges.keys():
            self.ticker = "{}{}".format(self.ticker, self._exchanges[key])
            self._df = self.get_tick_data()
            if self._df is not None and (len(self._df.columns) > 1):
                return self._exchange = key

        raise LimeInvaildTicker()

    def get_tick_data(self):
        '''
        Retrives tick data from Netfonds from a known ticker.
        '''
        uri = '{}?date={}&paper={}&csv_format={}'.format(self._url,
                                                         self.start_date,
                                                         self.ticker,
                                                         self._file_format)
        return read_csv(uri)  

    
    def get_trades(self, ticker):
        '''
        Gets the trades made for a ticker on a specified day.
        '''
        self.ticker = ticker
        
        if self._exchange_found:
            self._df = self.get_tick_data()
        
        # finds the correct ticker if its not found
        if not self._exchange_found:
            if self._exchange == '':
                self._df = self.get_exchange_from_ticker()
            else:
                self.ticker = self.exchange_tracker()
                self._df = self.get_tick_data()
        
        # cleans data after its retrived
        if self._df is not None:
            self._df.time = self._df.time.apply(lambda x: datetime.datetime.strptime(x, '%Y%m%dT%H%M%S'))
            self._df = self._df.set_index(self._df.time)
        else:
            raise LimeInvaildQuery()

    def get_trade_history(self, begining_date, ticker, end_date):
        '''
        Gets the trades made for a ticker from a range of days.

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
        self.check_date(start_date, end_date)

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
                concat([self._df, self.get_trades(self.ticker)])
            else:
                self._df = self.get_trades(self.ticker)
