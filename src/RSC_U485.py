#!/usr/bin/env python2.5
# coding: utf-8
"""ファイルの行数を数えるプログラム
"""


def wordcount(iter):
    """ 与えられたイテレータに含まれる行数を数える

        chr_cnt, line_cnt = mycount.wordcount( file("mycount.py") )
    """
    chr_cnt  = 0  # 文字数
    line_cnt = 0  # 行数
    for l in iter:
        chr_cnt  += len(l) # この行の文字数を数えて積算する
        line_cnt += 1      # 行数を積算する
    return (chr_cnt, line_cnt)


if __name__ == '__main__':
    # メインルーチン
    from serial import Serial
    print "test" 