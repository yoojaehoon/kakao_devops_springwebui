#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prettytable import PrettyTable

def printData(data, output_format='table', **kwargs):
    if kwargs.has_key('header'):
        header = kwargs['header']
    else:
        header = None

    if kwargs.has_key('minimal_key'):
        minimal_key = kwargs['minimal_key']

    if output_format == 'table':
        printTable(data, header)

    elif output_format == 'minimal' and minimal_key:
        printMinimal(data,minimal_key)

    else:
        print 
        print data
        print 

def printMinimal(data, minimal_key):
    print data[minimal_key]

def printTable(data, header):
    if type(data) == type(dict()):
        table = PrettyTable(['Feild', 'Value'])
        table.align = 'l'

        for key in data:
            if type(data[key]) == type(list()):
                i = 1
                for l in data[key]:
                    table.add_row(['%s #%d' %(key, i), l])
                    i += 1
            else:
                table.add_row([key, data[key]])

        print table

    elif type(data) == type(list()):
        if len(data) > 0:
            if not header:
                header = []

                for key in data[0]:
                    header.append(key)

            table = PrettyTable(header)

            for d in data:
                row = []
                for key in header:
                    row.append(d[key])

                table.add_row(row)

            print table

        else:
            if header:
                table = PrettyTable(header)
                print table

            else:
                print
                print data
                print

    else:
        print
        print data
        print
