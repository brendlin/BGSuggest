#!/usr/bin/python

import os
import sys
import datetime

def DownloadCSVAndMoveIntoPosition(start,end) :
    test_script = False
    days_old = (datetime.datetime.now() - datetime.datetime.strptime(end,'%m/%d/%Y')).days

    if days_old < 0 :
        print 'Error! Attempting to download data from the future! Exiting.'
        sys.exit()

    cmd = 'osascript DownloadCSV.scpt %s %s'%(start,end)
    print cmd

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
        print 'Error! Cannot locate the correct file in %s.'%(download_dir)
        return False

    if n_files == 0 :
        print 'Error! No new file found in %s.'%(download_dir)
        return False

    if days_old > 0 :
        first_day = '%s%s%s'%(start.split('/')[2].split('20')[1],
                              start.split('/')[0],
                              start.split('/')[1])
        last_day = '%s%s%s'%(end.split('/')[2].split('20')[1],
                             end.split('/')[0],
                             end.split('/')[1])
        new_filepath = '%s/BGSuggest/data/CareLink_Export_%s_%s.csv'%(os.getenv("HOME"),first_day,last_day)
    else :
        new_filepath = '%s/BGSuggest/data/CareLink_Export_thisWeek.csv'%(os.getenv("HOME"))

    mv_cmd = 'mv %s %s'%(the_filepath,new_filepath)

    if test_script :
        print mv_cmd
        os.system('rm %s/Downloads/safari/CareLink-Export-Test.csv'%(os.getenv("HOME")))

    if not test_script :
        os.system(mv_cmd)

    return True

if __name__ == "__main__":

    if len(sys.argv) < 3 :
        print 'Usage: python DownloadCSVAndMoveIntoPosition.py 12/25/2017 12/31/2017'
        sys.exit()

    DownloadCSVAndMoveIntoPosition(sys.argv[1],sys.argv[2])
