#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Author : xchliu
    Date   : 2/25/16
    
"""
from src.meta_data.table import Table

from weight import TOTAL
from weight import table_weight

class CheckItem(object):
    """

    """
    def __init__(self, table):
        self.table = table
        self.columns = table.columns

    def primary(self):
        """
        check the primary key
        :return:
        """
        primary = None
        score = 0
        for c in self.columns:
            if c.key == 'PRI':
                primary = c
        if not primary:
            return score
        counter = 0
        if 'int' in primary.type:
            counter += 1
        if 'bigint' in primary.type:
            counter += 1
        if 'unsigned' in primary.type:
            counter += 1
        if primary.isnull == 'NO':
            counter += 1
        if 'auto_increment' in primary.extra:
            counter += 2
        score = float(counter)/6*TOTAL
        print score
        return score


def estimate(schema, table):
    """
    analyse a table columns and keys
    :return a tuple(score, [suggest])
    """
    score = list()
    t = Table(schema, table)
    c = CheckItem(t)
    for item,weight in table_weight.items():
        # skip the item while its weight is 0
        if weight == 0:
            continue
        func = getattr(c, item, None)
        if func:
            score.append((weight, func()))
    print score
    return avg_score(score)


def avg_score(scores):
    """
    get the avg score from all the result of item checking
    :param scores:
    :return:
    """
    return sum(map(lambda x: x[0]*x[1]/float(TOTAL), scores))


def estimate_column():
    """

    :return:
    """


def main():
    print estimate('mega', 'report_weekly')
    return


if __name__ == "__main__":
    main()