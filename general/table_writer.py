"""
Is responsible for writing given data into csv files.
"""
import logging

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


def create_csv(csv_filepaths, tables):
    """
    Creates CSV tables from data collected before.
    :param csv_filepaths: the paths, the csv tables generated by this function should be saved.
    :param tables: Nested lists which contain all table content.
    :return: None
    """
    for table_index in range(len(tables)):
        table = tables[table_index]
        with open(csv_filepaths[table_index], 'w') as table_file:

            for row in table:
                logging.debug('row list: %s', row)

                row_line = ''

                # write a value from each column into one line
                for entry in row[:-1]:
                    row_line += entry.replace(',',' -')
                    row_line += ', '
                row_line += row[-1].replace(',',' -')
                
                logging.debug('row line: %s', row_line)

                # write out line
                table_file.write(row_line + '\n')

        logging.info('Wrote chart values into %s', csv_filepaths[table_index])
