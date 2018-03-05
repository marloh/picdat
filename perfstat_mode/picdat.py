"""
From here, the tool gets started.
"""
import getopt
import logging
import os
import shutil
import traceback
import sys

sys.path.append('..')

from perfstat_mode import constants
from perfstat_mode import util
from perfstat_mode import data_collector
from general import table_writer
from general import visualizer

__author__ = 'Marie Lohbeck'
__copyright__ = 'Copyright 2017, Advanced UniByte GmbH'

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


def print_help_and_exit(program_name):
    """
    This function prints a String about the program's usage to the command line and then quits
    the program.
    :param program_name: The program's name.
    :return: None
    """
    print(constants.HELP % program_name)
    sys.exit(0)


def validate_input_file(input_file):
    """
    This function validates an input file given by the user with some simple criteria.
    :param input_file: The user-given input file
    :return: None
    :raises fileNotFoundError: raises an exception, if input_file is neither a directory nor a file.
    :raises typeError: raises an exception, if input_file is a file of the wrong data type
    (neither .data nor .zip).
    """
    if os.path.isdir(input_file):
        return
    elif not os.path.isfile(input_file):
        raise FileNotFoundError

    data_type = util.data_type(input_file)

    if data_type != 'data' and data_type != 'zip':
        raise TypeError


def take_perfstats():
    """
    This function requests a PerfStat output location of the user and decides, whether its type is
    data or zip. If applicable, it extracts the zip folder into a temporary directory.
    :return: The temporary directory's path (might be None, after usage of files inside this
    directory should become deleted) and a list of all PerfStat data files extracted from user
    input.
    """
    while True:
        input_file = input('Please enter a path to some PerfStat output (folder or zipfolder '
                           'or .data file, default is ./output.data):' + os.linesep)

        if input_file == '':
            input_file = constants.DEFAULT_PERFSTAT_OUTPUT_FILE

        try:
            validate_input_file(input_file)
            return input_file
        except FileNotFoundError:
            print('This file does not exist. Try again.')
        except TypeError:
            print('Unexpected data type: File must be of type .data or .zip. Try again.')


def take_directory():
    """
    This function requests a destination directory of the user. All results of the PicDat program
    will be written to this directory.
    :return: The path to the directory, the results should be written in
    """
    destination_directory = input('Please select a destination directory for the results ('
                                  'Default is ./results):' + os.linesep)
    if destination_directory == '':
        destination_directory = 'results'

    return destination_directory


def prepare_directory(destination_dir):
    """
    Copies the templates .jss and .css files into the given directory. Also creates an empty
    subdirectory for csv tables.
    :param destination_dir: The directory, the user gave in as destination.
    :return: The path to the csv directory inside destination_dir. In this directory, PicDat should
    write all csv tables.
    """
    logging.info('Prepare directory...')

    csv_dir = destination_dir + os.sep + 'tables'
    if not os.path.isdir(csv_dir):
        os.makedirs(csv_dir)

    dygraphs_dir = destination_dir + os.sep + 'dygraphs'
    if not os.path.isdir(dygraphs_dir):
        os.makedirs(dygraphs_dir)

    dygraphs_js_source = constants.DYGRAPHS_JS_SRC
    dygraphs_js_dest = dygraphs_dir + os.sep + 'dygraph.js'
    dygraphs_css_source = constants.DYGRAPHS_CSS_SRC
    dygraphs_css_dest = dygraphs_dir + os.sep + 'dygraph.css'
    shutil.copyfile(dygraphs_js_source, dygraphs_js_dest)
    shutil.copyfile(dygraphs_css_source, dygraphs_css_dest)

    return csv_dir


def handle_user_input(argv):
    """
    Processes command line options belonging to PicDat. If no log level is given, takes default
    log level instead. If no input file or output directory is given, PicDat will ask the user
    about them at runtime. If a log file is desired, logging content is redirected into picdat.log.
    :param argv: Command line parameters.
    :return: A tuple of two paths; the first one leads to the PerfStat input, the second one to
    the output directory.
    """

    # get all options from argv and turn them into a dict
    try:
        opts, _ = getopt.getopt(argv[1:], 'hsld:i:o:', ['help', 'sortbynames', 'logfile', 'debug=',
                                                        'inputfile=', 'outputdir='])
        opts = dict(opts)
    except getopt.GetoptError:
        logging.exception('Couldn\'t read command line options.')
        print_help_and_exit(argv[0])

    # print help information if option 'help' is given
    if '-h' in opts or '--help' in opts:
        print_help_and_exit(argv[0])

    # Looks, whether user wants to sort legend entries alphabetically instead of by relevance
    if '-s' in opts or '--sortbynames' in opts:
        sort_columns_by_name = True
    else:
        sort_columns_by_name = False

    # extract log level from options if possible
    if '-d' in opts:
        log_level = util.get_log_level(opts['-d'])
    elif '--debug' in opts:
        log_level = util.get_log_level(opts['--debug'])
    else:
        log_level = constants.DEFAULT_LOG_LEVEL

    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=log_level)

    # extract inputfile from options if possible
    if '-i' in opts:
        input_file = opts['-i']
    elif '--inputfile' in opts:
        input_file = opts['--inputfile']
    else:
        input_file = take_perfstats()

    try:
        validate_input_file(input_file)
    except FileNotFoundError:
        logging.error('File %s does not exist.', input_file)
        sys.exit(1)
    except TypeError:
        logging.error('File %s is of unexpected data type.', input_file)
        sys.exit(1)

    # extract outputdir from options if possible
    if '-o' in opts:
        output_dir = opts['-o']
    elif '--outputdir' in opts:
        output_dir = opts['--outputdir']
    else:
        output_dir = take_directory()

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # decide, whether logging information should be written into a log file
    if '-l' in opts or '--logfile' in opts:
        [logging.root.removeHandler(handler) for handler in logging.root.handlers[:]]
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', filename=output_dir
                            + os.sep + constants.LOGFILE_NAME, level=log_level)

    logging.info('inputfile: %s, outputdir: %s', os.path.abspath(input_file), os.path.abspath(
        output_dir))

    return input_file, output_dir, sort_columns_by_name


def run(argv):
    """
    The tool's main routine. Calls all functions to read the data, write CSVs
    and finally create an HTML. Handles user communication.
    :param argv: Command line parameters.
    :return: None
    """
    temp_path = None
    console_file = None
    identifier_dict = None

    try:
        # read command line options and take additional user input
        input_file, result_dir, sort_columns_by_name = handle_user_input(argv)

        # extract zip if necessary
        perfstat_output_files = None
        if os.path.isdir(input_file):
            perfstat_output_files, console_file = util.get_all_output_files(input_file)
        elif util.data_type(input_file) == 'data':
            perfstat_output_files = [input_file]
        elif util.data_type(input_file) == 'zip':
            logging.info('Extract zip...')
            temp_path, perfstat_output_files, console_file = util.extract_to_temp_dir(input_file)

        # interrupt program if there are no .data files found
        if not perfstat_output_files:
            logging.info('The input you gave (%s) doesn\'t contain any .data files.', input_file)
            sys.exit(0)

        # if given, read cluster and node information from console.log file:
        if console_file is not None:
            logging.info('Read console.log file for getting cluster and node names...')
            try:
                identifier_dict = util.read_console_file(console_file)
            except KeyboardInterrupt:
                raise
            except:
                logging.info('console.log file from zip couldn\'t be read for some reason: %s',
                             traceback.format_exc())
                identifier_dict = None
        else:
            logging.info('Did not find a console.log file to extract perfstat\'s cluster and node '
                         'name.')

        logging.debug('identifier dict: ' + str(identifier_dict))

        # create directory and copy the necessary templates files into it
        csv_dir = prepare_directory(result_dir)

        for perfstat_node in perfstat_output_files:

            # get nice names (if possible) for each PerfStat and the whole html file
            perfstat_address = perfstat_node.split(os.sep)[-2]

            if identifier_dict is None:
                html_title = perfstat_node
                node_identifier = perfstat_address
            else:
                try:
                    node_identifier = identifier_dict[perfstat_address][1]
                    html_title = util.get_html_title(identifier_dict, perfstat_address)
                    logging.debug('html title (from identifier dict): ' + str(html_title))
                except KeyError:
                    logging.info(
                        'Did not find a node name for address \'%s\' in \'console.log\'. Will '
                        'use just \'%s\' instead.', perfstat_address, perfstat_address)
                    html_title = perfstat_node
                    node_identifier = perfstat_address

                logging.info('Handle PerfStat from node "' + node_identifier + '":')
            node_identifier += '_'

            if len(perfstat_output_files) == 1:
                node_identifier = ''

            # collect data from file
            logging.info('Read data...')
            tables, identifier_dict = data_collector.read_data_file(perfstat_node,
                                                                    sort_columns_by_name)

            logging.debug('tables: %s', tables)
            logging.debug('all identifiers: %s', identifier_dict)

            # frame html file path
            html_filepath = result_dir + os.sep + node_identifier + constants.HTML_FILENAME + \
                constants.HTML_ENDING

            csv_filenames = util.get_csv_filenames(identifier_dict['object_ids'], node_identifier)
            csv_abs_filepaths = [csv_dir + os.sep + filename for filename in csv_filenames]
            csv_filelinks = [csv_dir.split(os.sep)[-1] + '/' + filename for filename in
                             csv_filenames]

            # write data into csv tables
            logging.info('Create csv tables...')
            table_writer.create_csv(csv_abs_filepaths, tables)

            # write html file
            logging.info('Create html file...')
            visualizer.create_html(html_filepath, csv_filelinks, html_title, identifier_dict)

            # reset global variable 'localtimezone'
            util.localtimezone = None

        logging.info('Done. You will find charts under: %s', os.path.abspath(result_dir))

    finally:
        # delete extracted zip
        if temp_path is not None:
            shutil.rmtree(temp_path)
            logging.info('(Temporarily extracted files deleted)')


# run
run(sys.argv)