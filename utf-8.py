#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File Title: utf-8.py
# Author: Selphia
# Mail: LoliSound@gmail.com
# Time: 2017年10月14日 星期六 08时34分32秒
# Version: 1.0
import os,re

pwd=os.walk(os.getcwd())
for a,b,c in pwd:
    for i in c:
        if re.search('.*\.txt$',i):
            file_FullPath=os.path.join(a,i)
            file_open=open(file_FullPath,'r',encoding='gbk')
            file_read=file_open.read()
            file_open.close()
            file_write=open(file_FullPath,'w',encoding='utf-8')
            file_write.write(file_read)
            file_write.close()
