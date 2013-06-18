class lime(object):
    '''
    A simple API for extracting stock tick data
    '''
    def __init__(self, *args, **kwargs):
        from pandas import DataFrame
        df = DataFrame.from_items([('A', [1, 2, 3])])
        self.start_date = ''
        self.end_date = ''
        self.file_format = 'csv'
        self.exchange = ''
        self.exchange_found = False
        self.exchanges = {'Nasdaq': '.O', 'Nyse' : '.N', 'Amex': '.A'}

        # default to today's date if date is empty
        if self.start_date == '':
            self.start_date = self.get_date_today()
        # set string formatting requirements
        else:
            self.start_date =  self.start_date.strftime('%Y%m%d')

        
    def exchange_tracker(self, *args):
        '''
        modifies ticker with correct exchange extension
        '''
        import re
        processed = False
        
        try:
            split_results = re.split('[.]', self.ticker)
            if split_results[1] == ('O' or 'N' or 'A'):
                processed = True
                self.exchange_found = True
        except:
            pass
        
        if processed == False and self.exchange.lower() == 'nasdaq':
            self.ticker = str(self.ticker)+'.O'
            self.exchange_found = True
            return self.ticker
        if processed == False and self.exchange.lower() == 'nyse':
            self.ticker = str(self.ticker)+'.N'
            self.exchange_found = True
            return self.ticker
        if processed == False and self.exchange.lower() == 'amex':
            self.ticker = str(self.ticker)+'.A'
            self.exchange_found = True
            return self.ticker

    def efficient_ticker_retrieval (self, *args):
        '''
        1 query way to get ticker data

        self, start_date, ticker, file_format
        '''
        from pandas import read_csv
        from urllib2 import urlopen

        s = 'http://www.netfonds.no/quotes/tradedump.php?date=%s&paper=%s&csv_format=%s'%(self.start_date, self.ticker, self.file_format)
        #print s # for debugging

        # generally will error if wrong ticker is given by slow_ticker_retrieveal
        # add error checking here
        try:
            df = read_csv(s)
        except:
            df = urlopen(s).read()
        return df
        
    
    def slow_ticker_retrieval(self, *args):
        '''
        finds ticker info w/o exchange info
        '''

        # create a ticker bin var for comparison
        origninal_ticker = self.ticker
        self.exchange_found = False

        for i,key in enumerate(self.exchanges):
                self.ticker = origninal_ticker
                self.ticker = str(self.ticker) + str(self.exchanges[key])
                df = self.efficient_ticker_retrieval()
                if isinstance(df, str) != True and (len(df.columns) > 1) :
                    self.exchange_found = True
                    self.exchange = key
                    return df
                    break

    def get_date_today(self):
        '''
        gets today's date
        '''
        import datetime
        return datetime.date.today().strftime('%Y%m%d')

    def lime_date_parse(self, date):
        '''
        date must be a python datetime object
        '''
        return date.strftime('%Y%m%d')

    def get_single(self, ticker, *args, **kwargs):
        '''
         ticker, *args, **kwargs

         get stock prices
        '''
        import datetime
        self.ticker = ticker
        
        
        if self.exchange_found == True:
            df = self.efficient_ticker_retrieval()
        elif self.exchange_found == False and self.exchange == '':
            df = self.slow_ticker_retrieval()   
        elif self.exchange_found == False and self.exchange != '':
            self.ticker  = self.exchange_tracker()
            df = self.efficient_ticker_retrieval()
        
        if isinstance(df, str) != True :
            df.time = df.time.apply(lambda x: datetime.datetime.strptime(x, '%Y%m%dT%H%M%S'))
            df = df.set_index(df.time)
            return df
        else:
            print "invalid query, please try again"

    def get_many(self, begining_date, ticker, end_date, *args, **kwargs):
        '''
        self, begining_date, end_date (optional), ticker

        start date is the day you want to start exctracting info from 

        ie extract info :

        (start_date)    (end_date)
        May 21, 2013 to June 1, 2013

        Tick data only persits for 21 days! Any queries longer than that will fail

        If no end_date is specified then it defaults today
        '''
        from datetime import timedelta

        from pandas import concat
        from pandas import date_range

        self.ticker = ticker
        self.end_date = end_date
        self.exchange_found = False
        df = 'I am a string, take it or leave it.'

        # generate warnings -- should be put into thier own methods
        if (end_date - begining_date) > timedelta(21):
            print "invalid query, date range is greater than 21 days. Data does not exist beyond 21 days"

        if (end_date - begining_date) < timedelta(0):
            print "you most likely reversed the begining_date and end_date"

        # prep dates
        begining_date = self.lime_date_parse(begining_date)

        if end_date == '':
            self.end_date = self.get_date_today()
        else:
            self.end_date = self.lime_date_parse(end_date)

        # Get stock tick data
        for single_date in date_range(start=begining_date, end=self.end_date, freq='B'):
            self.start_date = self.lime_date_parse(single_date)
            if isinstance(df, str) != True:
                concat([df, self.get_single(self.ticker)])
            else:
                df = self.get_single(self.ticker)
        return df