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

    def get_df(self):
        ''' Gets the stored tick data '''
        return self._df

    def set_df(self, dataframe):
        '''
        Sets stored tick data
        
        Parameters
        * dataframe -- pandas.DataFrame()
        '''
        self._df = dataframe
        self.process_data()

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

    def validate_ticker_exchange_extenstion(self):
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
            self.validate_ticker_exchange_extenstion()
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
            self.get_tick_data()
            if self._df is not None and (len(self._df.columns) > 1):
                return self._exchange = key

        raise LimeInvaildTicker()

    def set_start_end_dates(self, start, end=None):
        '''
        Parses and Prepares Start and End dates.

        ###Parameters
        * start -- datetime
        * end -- ( optional ) datetime, defaults to today's date
        '''
        self.check_date(start, end)
        self.start_date = self.date_parse(start)
        self.end_date = self.date_parse(end) if end else self.get_date_today()
    
    def process_data(self):
        '''
        Cleans data after its retrived from Netfonds
        '''
        df = self.get_df()
        try:
            df.time = df.time.apply(lambda x: datetime.datetime.strptime(x, '%Y%m%dT%H%M%S'))
            df = df.set_index(df.time)
        except AttributeError:
            raise LimeInvaildQuery()

        self.set_df(df)
   
    def get_tick_data(self):
        '''
        Retrives tick data from Netfonds from a known ticker.
        '''
        uri = '{}?date={}&paper={}&csv_format={}'.format(self._url,
                                                         self.start_date,
                                                         self.ticker,
                                                         self._file_format)
        self.set_df(read_csv(uri))

    def get_trades(self, ticker):
        '''
        Gets the trades made for a ticker on a specified day.
        '''
        self.ticker = ticker
        self.check_ticker_exchange_extenstion()
        
        if self._exchange_found:
            self.get_tick_data()
        
        # finds the correct ticker if its not found
        if not self._exchange_found:
            if self._exchange == '':
                self._df = self.get_exchange_from_ticker()
            else:
                self.ticker = self.exchange_tracker()
                self.get_tick_data()
        
        return self.get_df()
    
    def get_trade_history(self, ticker, start_date, end_date=None):
        '''
        Gets the trades made for a ticker from a range of days.

        ticker, start_date, end_date (optional)

        start date is the day you want to start exctracting info from

        ie extract info :

        (start_date)    (end_date)
        May 21, 2013 to June 1, 2013

        Tick data only persits for 21 days! Any queries longer than that will fail

        If no end_date is specified then it defaults today
        '''
        
        #TODO: revamp setting and Getting

        self.ticker = ticker
        self._exchange_found = False
        self.set_start_end_dates(start_date, end_date)

        for day in date_range(start=start_date, end=self.end_date, freq='B'):
            self.start_date = self.date_parse(day)

            if self.get_df():
                self.set_df(concat([self.get_df(), self.get_trades(self.ticker)]))
            else:
                self.set_df(self.get_trades(self.ticker))

        return self.get_df()
