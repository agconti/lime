from datetime import timedelta


class LimeInvaildQuery(Exception):
    '''
    An Exception for Handling invalid requests

    ###Parameters
    * url -- string, should be self._url used to access NetFonds
    '''

    def __init__(self, url):
        self.url = url
        self.msg = ('Lime was not able to contact Netfonds, based'
                    ' on the information you provided.'
                    'Please check your request and try again.')

    def __str__(self):
        return repr("Invalid Query:{}:\n{}".format(self.msg, self.url))


class LimeInvaildDate(Exception):
    '''
    An Exception for handling invalid dates for requests

    ###Parameters
    * start -- datetime object, should be self.start_date
    * end -- datetime object, should be self.end_date

    '''

    def __init__(self, start, end):
        self.msg = self.check_date(start, end)
        self.start = start
        self.end = end

    def check_date(self):
        '''
        returns the appropriate error message based
        on the provided dates.
        '''
        if (self.end - self.start) > timedelta(21):
            self.msg = ('Date range is greater than 21 days.'
                        'Data does not exist on NetFonds beyond 21 days.\n'
                        'Please reconstruct your query and try again.')
        if self.start > self.end:
            self.msg = ('The Start Date is greater than the End Date.\n'
                        'You most likely reversed the begining_date and end_date.')

    def __str__(self):
        return repr("Invalid Date:{}:\n{}".format(self.msg, self.date))
        