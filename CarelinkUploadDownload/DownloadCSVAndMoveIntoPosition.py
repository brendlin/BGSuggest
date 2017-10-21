#!/usr/bin/python

import os
import sys
import datetime

test_script = False

cmd = 'osascript DownloadCSV.scpt %s %s'%(sys.argv[1],sys.argv[2])

if test_script :
    print cmd
    os.system('touch %s/Downloads/safari/CareLink-Export-Test.csv'%(os.getenv("HOME")))
else :
    os.system(cmd)

n_files = 0

download_dir = '%s/Downloads/safari'%(os.getenv("HOME"))
for i in os.listdir(download_dir) :
    tmp_filepath = '%s/%s'%(download_dir,i)
    if test_script :
        print i,tmp_filepath
    creation_time = os.path.getmtime(tmp_filepath)
    age_seconds = (datetime.datetime.now() - datetime.datetime.fromtimestamp(creation_time)).seconds
    if ('CareLink-Export' in i) and age_seconds < 20 :
        the_filepath = tmp_filepath
        n_files += 1

if n_files > 1 :
    print 'Error! Please clean up the directory %s.'%(download_dir)
    sys.exit()

days_old = (datetime.datetime.now() - datetime.datetime.strptime(sys.argv[2],'%m/%d/%Y')).days
if days_old > 0 :
    first_day = '%s%s%s'%(sys.argv[1].split('/')[2].split('20')[1],
                          sys.argv[1].split('/')[0],
                          sys.argv[1].split('/')[1])
    last_day = '%s%s%s'%(sys.argv[2].split('/')[2].split('20')[1],
                         sys.argv[2].split('/')[0],
                         sys.argv[2].split('/')[1])
    new_filepath = '%s/BGSuggest/data/CareLink_Export_%s_%s.csv'%(os.getenv("HOME"),first_day,last_day)
else :
    new_filepath = '%s/BGSuggest/data/CareLink_Export_thisWeek.csv'%(os.getenv("HOME"))

mv_cmd = 'mv %s %s'%(the_filepath,new_filepath)

if test_script :
    print mv_cmd
    os.system('rm %s/Downloads/safari/CareLink-Export-Test.csv'%(os.getenv("HOME")))

if not test_script :
    os.system(mv_cmd)
