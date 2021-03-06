"""
Constants for different modules.
"""

import logging
from os import sep

__author__ = 'Marie Lohbeck'
__copyright__ = 'Copyright 2018, Advanced UniByte GmbH'

# license notice:
#
# This file is part of PicDat.
# PicDat is free software: you can redistribute it and/or modify it under the terms of the GNU
# General Public (at your option) any later version.
#
# PicDat is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with PicDat. If not,
# see <http://www.gnu.org/licenses/>.

# String to print together with the program name if user uses command line option --help or -h or
# any not recognized options:
HELP = '''
PicDat is a tool for visualising performance data. It can handle PerfStat files as well as ASUP files.

For visualising PerfStats, give a single .data or .out file or a .zip file as input, or a folder,
containing unpacked PerfStat files. Within a .zip or a folder, it is possible to pass several PerfSat
files at once, for example PerfStats for several nodes inside the same cluster. Each PerfStat file
will have an own .html as result. 

For visualising ASUP xml files, give a .tgz archive, as you can download it from NetApp or give a
folder, containing at least 'CM-STATS-HOURLY-INFO.XML' and 'CM-STATS-HOURLY-DATA.XML'. If you want
to visualise several xml ASUPs in a row, give a directory as input, which contains several .tgz
archives. The alphabetical order of the archives names should be equivalent to the chronological
order of the content. Different from PerfStat input, PicDat will stick ASUP results all together,
so don't mess around with data from different nodes or anything, when doing so!

Performance data in ASUPs for later ontap versions is not in xml format anymore. To visualise them,
you will have to preprocess them with trafero, which returns json files. Give PicDat either a
single json file or a directory with several json files. If you give a directory, each json file
must belong to the same cluster and node.

usage: %s [--help] [--sortbyname] [--inputfile "input"] [--outputdir "output"] [--debug "level"]

    --help, -h: prints this message
    
    --sortbyname, -s: Sorts the legends of most charts alphabetically. Per default,
                      legend entries are sorted by relevance, means the graph with the
                      highest values in sum is displayed at the top of the legend.
                      
    --input "input", -i "input": input is the path to some performance data. Should be a folder,
                                 .zip file, .data file, .out file, .tgz, or .h5 file. 
                                 (for more details look above)
                                 
    --outputdir "output", -o "output": output is the directory's path, where this program puts its
                                       results. If there is no directory existing yet under this
                                       path, one would be created. If there already are some
                                       PicDat results, they might be overwritten.
                                       
    --debug "level", -d "level": level should be inside debug, info, warning, error, critical. It
                                 describes the filtering level of command line output during
                                 running this program. Default is "info".
                                 
    --logfile, -l: redirects logging information into a file called picdat.log.
    
    --compact, -c: packs all necessary resources into the charts files. With this, the charts.html
                   files get more portable, because they do not depend on any other files, and
                   furthermore, there will be less problems with the browsers Edge and Chrome.
    
    --webserver, -w: at the end of execution, starts a local web server in output directory to
                     serve dygraphs JavaScript from it. This is a workaround for security settings
                     of browsers like Google Chrome and Internet Explorer.
'''


# this log level is used, if the user didn't specify one:
DEFAULT_LOG_LEVEL = logging.INFO

# name of log file:
LOGFILE_NAME = 'picdat.log'

# program saves its results in a directory named like that (might have an additional number):
DEFAULT_DIRECTORY_NAME = 'results'

# program names csv files with the name of the chart they belong to, and the following ending:
CSV_FILE_ENDING = '_chart_values.csv'

# program names html file inside the result directory like this:
HTML_FILENAME = 'charts'
HTML_ENDING = '.html'

# this is the path to the text file the program uses as template to create the html head and
# all js code in the body:
HTML_TEMPLATE = 'templates' + sep + 'html_template.txt'
# and the same thing when command line option 'compact' is given; this template also includes all
# dygraph code:
HTML_TEMPLATE_COMPACT = 'templates' + sep + 'html_template_compact.txt'

# these are the paths to the dygraph files the html document needs to show its charts:
DYGRAPHS_JS_SRC = 'templates' + sep + 'dygraph.js'
DYGRAPHS_CSS_SRC = 'templates' + sep + 'dygraph.css'

# these are the expected names of relevant files in xml mode:
ASUP_INFO_FILE = 'CM-STATS-HOURLY-INFO.XML'
ASUP_DATA_FILE = 'CM-STATS-HOURLY-DATA.XML'
ASUP_HEADER_FILE = 'HEADERS'
