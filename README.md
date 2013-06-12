lime
====

An API for extracting tick data for US equities for ad-hoc analysis in Python with Pandas.

Currently lime supports two main work horse functions:

*  `get_single(date, stock_ticker,)` - retrives a single days trading history returned in a nice neat pandas dataframe. 
*  `get _many(date_range, stock_ticker)` - retrives tick data over a range of dates, and compiles those dates in a nice neat dataframe for easy output.

*additional functions are included to make this process easier*

### Improvements

Currently, lime can get the tick data for any US trade stock, but this is limiting. 

Planned enhancements are:

*  support for any US security 
*  support for international securities
*  support for passing a list of tickers / securities for easy analysis


A basic demo of what lime can do will is located [here](http://nbviewer.ipython.org/urls/raw.github.com/agconti/lime/master/lime_demo.ipynb).