#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import os
import pandas as pd
import js2py
import datetime
import pytz # timezone ("naive", "aware")
tz = pytz.utc
import evolution_bayes

def scan_dbfile(path='./history'):
    files = os.listdir(path)
    results = []
    for filename in files:
        if filename[-3:] == '.db':
            fullpath = os.path.abspath(os.path.join(path, filename))
            results.append(fullpath)
    return results

def scan_table(dbname='database.db'):
    exchange = os.path.basename(dbname).split("_")[0]
    conn = sqlite3.connect(dbname)
    c = conn.cursor()

    select_table = '''SELECT name FROM sqlite_master WHERE type='table' '''
    results = []
    for table in c.execute(select_table):
        parts = table[0].split('_')
        first = parts[0]
        if first == 'candles':
            results.append([dbname, table[0], exchange, parts[1], parts[-1]])
    conn.close()
    return results

def get_candle_range(dbname, tablename, fromdate, todate, what="*"):
    if isinstance(fromdate, datetime.datetime):
        fromdate = int(fromdate.timestamp())
    if isinstance(todate, datetime.datetime):
        todate = int(todate.timestamp())
    sql = """
      SELECT {} from {}
      WHERE start <= ? AND start >= ?
      ORDER BY start ASC
    """.format(what, tablename)
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    results = []
    params = (todate, fromdate)
    for row in c.execute(sql, params):
        results.append(row)
    conn.close()
    return results

def get_candle(dbname, tablename, what="*"):
    sql = """
      SELECT {} from {}
      ORDER BY start ASC
    """.format(what, tablename)
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    results = []
    for row in c.execute(sql):
        results.append(row)
    conn.close()
    return results

def get_all_candles():
    files = scan_dbfile('../gekko/history')
    print(files)
    columns = ['dbfile', 'table', 'exchange', 'currency', 'assets']
    tables = pd.DataFrame([], columns=columns)
    for f in files:
        merkets = scan_table(dbname=f)
        m = pd.DataFrame(merkets, columns=columns)
        tables = pd.concat([tables, m])

    columns = ['id', 'start', 'open', 'high', 'low', 'close', 'vwp', 'volume', 'trades']
    candles = {}
    candles = pd.DataFrame([], columns=columns)
    for (i, table) in tables.iterrows():
        tablename = table["table"]
        try:
            candle = get_candle(dbname=f, tablename=tablename)
        except:
            continue
        name = os.path.basename(table["dbfile"])
        m = pd.DataFrame(candle, columns=columns)
        m["dbname"] = name+"_"+tablename
        candles = pd.concat([candles, m])
    candles["start"] = pd.to_datetime(candles["start"], unit='s')
    candles.index = candles["start"]
    return candles

if __name__ == '__main__':
    print(get_all_candles())
