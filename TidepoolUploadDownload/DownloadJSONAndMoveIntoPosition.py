#!/usr/bin/python

import os
import sys
from datetime import datetime,timedelta
import json

# Add parent directory to python path
the_path = ('/').join(os.getcwd().split('/')[:-1]) 
print 'Adding %s to PYTHONPATH.'%(the_path)
sys.path.append(the_path)

from TimeClass import MyTime

def DownloadJSONAndMoveIntoPosition(options,args) :

    # First, download the latest data:
    os.system('source DownloadJSON.sh %s'%(options.file))

    today = datetime.now()
    # Navigate to the beginning of this week:
    start_of_this_week = today - timedelta(days=today.weekday())
    # Trick to get rid of excess:
    start_of_this_week = datetime.strptime(start_of_this_week.strftime('%Y-%m-%dT00:00:00'),'%Y-%m-%dT%H:%M:%S')
    # Now count back to the week we want
    start = start_of_this_week - timedelta(days=options.week*7)
    end   = start + timedelta(days=7) - timedelta(seconds=1)
    #print("Today: " + today.strftime('%Y-%m-%dT%H:%M:%S'))
    print 'Will download the following:'
    print 'Start: %s'%(start.strftime('%Y-%m-%dT%H:%M:%S'))
    print 'End  : %s'%(end.strftime('%Y-%m-%dT%H:%M:%S'))

    start_utc = MyTime.TimeFromString(start.strftime('%Y-%m-%dT%H:%M:%S'))
    end_utc   = MyTime.TimeFromString(end.strftime('%Y-%m-%dT%H:%M:%S'))

    start_outfilestr = start.strftime('_%y%m%d')
    end_outfilestr   = end.strftime('_%y%m%d')
    if options.week == 0 :
        start_outfilestr = '_999999'
        end_outfilestr = '_thisWeek'
    outfilename = '../data/Tidepool_Export%s%s.json'%(start_outfilestr,end_outfilestr)
    print 'Name : %s'%(outfilename)

    raw_input('Press enter to continue.')

    json_file = open(options.file)
    data = json.load(json_file)
    data_skimmed = [] # This will be a list of dictionaries.

    for line in data :

        uTime = 0

        if line.get('deviceTime',False) :
            uTime = MyTime.TimeFromString(line['deviceTime'])
        elif line.get('computerTime',False) :
            uTime = MyTime.TimeFromString(line['computerTime'])

        if not uTime :
            print 'Error: could not figure out the time of this line.'
            print line
            import sys; sys.exit()
            
        if uTime > end_utc or uTime < start_utc :
            continue

        data_skimmed.append(line)
    
    if len(data_skimmed) == 0 :
        print 'Warning - period contains no data. Ending without producing a file.'
        return True

    with open(outfilename, 'w') as outfile :

        #json.dump(data_skimmed, outfile)
        outfile.write(
            '[\n' +
            ',\n'.join(json.dumps(i) for i in data_skimmed) +
            '\n]\n')

    print 'Saved %s.'%(outfilename)

    return True

if __name__ == "__main__" :
    from optparse import OptionParser
    p = OptionParser()

    p.add_option('--week',type='int',default=0,dest='week',help='Number of weeks ago (0)')
    p.add_option('--file',type='string',default='download.json',dest='file',help='JSON file to parse')

    options,args = p.parse_args()
    DownloadJSONAndMoveIntoPosition(options,args)
