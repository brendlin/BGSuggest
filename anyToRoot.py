import ImportHelpers
from txtToRoot import ProcessFileCSV
from jsonToRoot import ProcessFileJSON

#
# This should integrate both Medtronic and Tidepool exports.
# 

def main(options,args) :

    # All of the setup is now done in this wrapper function
    manager = ImportHelpers.ImportManager(options,args)
    inputfilenames = manager.GetInputFiles()

    for inputfilename in inputfilenames :

        if inputfilename.endswith('.csv') :
            manager.ProcessFile(inputfilename,ProcessFileCSV)
        elif inputfilename.endswith('.json') :
            manager.ProcessFile(inputfilename,ProcessFileJSON)
        else :
            print 'Error - do not know how to process file %s'%(inputfilename)
            import sys; sys.exit()

    # Save output
    manager.Finish()

    return


if __name__ == '__main__' :
    from optparse import OptionParser
    p = OptionParser()
    p.add_option('--ndetailed',type='int',default=4,dest='ndetailed',help='Number of weeks of detail (4)')
    p.add_option('--outname'  ,type='string',default='output.root',dest='outname',help='Output root file name')
    p.add_option('--datadir'  ,type='string',default='data',dest='datadir',help='Data directory')

    options,args = p.parse_args()

    # We will process Medtronic csv files OR TidePool json files!
    options.match_regexp = ['CareLink_Export.*csv','Tidepool_Export.*json']

    main(options,args)
