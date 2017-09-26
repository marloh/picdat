"""
Contains the class StatitClass. This class is responsible for processing a certain request
type. The statit-requests are about some blocks in the PerfStat called something like 'statit'.
These blocks may appear several times in a PerfStat iteration. PicDat is interested in a special
subsection of the statit block called 'Disk Statistics'. This subsections holds a table of
information about all disks of the device the PerfStat is about. PicDat only looks for the first
two columns of this table: The first one contains the disk names and the second one a related
number called 'ut%'. PicDat is going to create exactly one csv table and one chart about the
statit blocks.
"""
import logging

import constants
import util
from table import Table

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


STATIT_DISK_STAT_UNIT = '%'
STATIT_CHART_TITLE = 'statit%sdisk_statistics'


class StatitClass:
    """
    This object type is responsible for holding several information about statit blocks.
    in PerfStat output. It's a centralization of headers and values for the disk statistic charts.
    Further, it contains all other information necessary to read headers and values from a
    PerfStat file.
    """

    def __init__(self):
        self.statit_counter = 0
        self.statit_timestamps = []

        self.inside_statit_block = False
        self.inside_disk_stats_block = False

        self.table = Table()
        self.disk_names = set()

        self.flat_headers = None
        self.flat_values = None

        self.line_buffer = None

    def check_statit_begin(self, line):
        """
        This function looks, whether a line from a PerfStat output marks the beginning of a
        statit block. If so, it increments the statit_counter and sets the inside_statit_block
        boolean to true.
        :param line: A line from a PerfStat file as String.
        :return: True, if the line contains a statit beginning marker and False otherwise.
        """
        if '---- statit ---' in line:
            self.statit_counter += 1
            self.inside_statit_block = True
            return True
        else:
            return False

    def process_disc_stats(self, line):
        """
        Collects all relevant information from a line in a statit block. There are two
        possibilities: Either the relevant part of the statit block - the part under 'Disk
        statistics' - already began or it didn't. In case it did, the function collects the value
        and the disk from the line into the object's table. It also watches for the end of this
        block. Otherwise, it watches for the statit timestamp respectively for the 'Disk
        statistics' part's begin.
        :param line: A line from a PerfStat file as String.
        :return: None.
        """
        line_split = line.split()
        if self.inside_disk_stats_block:
            if len(line_split) == 0 \
                    or line == 'Aggregate statistics:' \
                    or line == 'Spares and other disks:':
                self.inside_statit_block = False
                self.inside_disk_stats_block = False
                self.line_buffer = None
                return

            # don't care about sub headers:
            if len(line_split) == 1 and line.startswith('/') and line.endswith(':'):
                self.line_buffer = None
                return

            # In Disk Statistics blocks, PerfStat seems to break some lines out of nowhere
            # sometimes.
            if len(line_split) < constants.STATIT_COLUMNS:
                if self.line_buffer is None:
                    self.line_buffer = line
                    logging.debug('buffered statit line snippet: %s', line)
                    return
                else:
                    line_split = self.line_buffer.split() + line_split
                    logging.debug('joined statit line: %s', line_split)

            disk = line_split[0]
            ut_percent = line_split[1]

            self.disk_names.add(disk)
            self.table.insert(self.statit_counter, disk, ut_percent)

            self.line_buffer = None

            # In Disk Statistics blocks, PerfStat seems to break some lines out of nowhere
            # sometimes. To distinguish between fresh lines and some line break snippets,
            # the program checks, whether the second word from 'line' is actually the same as the
            # one lying directly under the column header 'ut%':

            #if ut_percent == line[self.ut_column_indices[0]: self.ut_column_indices[1]].strip():
            #    self.disk_names.add(disk)
            #    self.table.insert(self.statit_counter, disk, ut_percent)

        else:
            if len(line_split) == 0:
                return
            if len(self.statit_timestamps) < self.statit_counter:
                if 'Begin: ' in line:
                    try:
                        self.statit_timestamps.append(util.build_date(line.split(' ', 1)[1]))
                    except (KeyError, IndexError, ValueError):

                        if not self.statit_timestamps:
                            alternative_timestamp = constants.DEFAULT_TIMESTAMP

                            logging.warning(
                                'PerfStat bug in statit block. Could not read any timestamp '
                                'from line: \'%s\' This should have been the very first statit '
                                'timestamp of this document. PicDat is using default timestamp '
                                'instead. This timestamp is: \'%s\'. Note that this may lead to '
                                'falsifications in charts!', line.strip(), alternative_timestamp)

                        else:
                            alternative_timestamp = self.statit_timestamps[-1]
                            logging.warning(
                                'PerfStat bug in statit block. Could not read any timestamp '
                                'from line: \'%s\' PicDat is using the timestamp from the last '
                                'statit block instead. This timestamp is: \'%s\'. Note that this '
                                'may lead to falsifications in charts!',
                                line.strip(), alternative_timestamp)

                        self.statit_timestamps.append(alternative_timestamp)
                return
            if line_split[0] == 'disk':
                self.inside_disk_stats_block = True

    def rework_statit_data(self, iteration_timestamps):
        """
        Simplifies statit data: Flattens the table data structure into the lists flat_headers and   
        flat_values. Also inserts empty data lines into flat_values, to separate iterations in
        resulting charts from each other.
        :param iteration_timestamps: A list of datetime objects, marking the ends of all
        iterations in one PerfStat file. They are needed to insert the empty lines at the right
        places.
        :return: None
        """
        self.flat_headers, self.flat_values = self.table.flatten(self.disk_names,
                                                                 self.statit_timestamps, 1)
        self.add_empty_lines(iteration_timestamps)

    def add_empty_lines(self, iteration_end_timestamps):
        """
        Inserts empty data lines into the flat_values list retroactively. The empty lines are
        inserted between two rows belonging to different iterations. This is for interrupting the
        dygraphs graph lines between iterations in resulting charts.
        :param iteration_end_timestamps: A list of datetime objects, marking the ends of all
        iterations in one PerfStat file.
        :return: None
        """
        iter_iterations = iter(iteration_end_timestamps)
        next_iteration = next(iter_iterations)
        counter = 0
        try:
            for statit in self.statit_timestamps:
                if next_iteration < statit:
                    self.flat_values.insert(counter, util.empty_line(self.flat_values))
                    next_iteration = next(iter_iterations)
                    counter += 1
                counter += 1
        except StopIteration:
            pass

    @staticmethod
    def get_units():
        return [STATIT_DISK_STAT_UNIT]

    @staticmethod
    def get_request_strings(delimiter):
        return [STATIT_CHART_TITLE % delimiter]

    @staticmethod
    def get_x_labels():
        return ['time']

    @staticmethod
    def get_barchart_booleans():
        return ['false']