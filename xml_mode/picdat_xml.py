'''

'''
import logging
import os
from xml_mode import data_collector
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


def run():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

    data_file = "somepath"
    info_file = "somepath"
    html_title = 'PicDat for XML'
    html_filepath = 'somepath'
    csv_dir = 'somepath'

    # collect data from file
    logging.info('Read data...')
    tables, identifier_dict = data_collector.read_data(data_file, info_file)
    logging.debug('tables: %s', tables)
    logging.debug('all identifiers: %s', identifier_dict)

    csv_filenames = identifier_dict.pop('csv_names')
    csv_abs_filepaths = [csv_dir + os.sep + filename for filename in csv_filenames]
    csv_filelinks = [csv_dir.split(os.sep)[-1] + '/' + filename for filename in
                     csv_filenames]

    # write data into csv tables
    logging.info('Create csv tables...')
    table_writer.create_csv(csv_abs_filepaths, tables)

    # write html file
    logging.info('Create html file...')
    visualizer.create_html(html_filepath, csv_filelinks, html_title, identifier_dict)

    #logging.info('Done. You will find charts under: %s', os.path.abspath())


run()