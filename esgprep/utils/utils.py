#!/usr/bin/env python
"""
   :platform: Unix
   :synopsis: Useful functions to use with esgprep modules.

"""

# Module imports
import os
import re
import logging
import textwrap
from argparse import HelpFormatter, ArgumentTypeError
from datetime import datetime


class MultilineFormatter(HelpFormatter):
    """
    Custom formatter class for argument parser to use with the Python
    `argparse <https://docs.python.org/2/library/argparse.html>`_ module.

    """

    def __init__(self, prog):
        # Overload the HelpFormatter class.
        super(MultilineFormatter, self).__init__(prog, max_help_position=60, width=100)

    def _fill_text(self, text, width, indent):
        # Rewrites the _fill_text method to support multiline description.
        text = self._whitespace_matcher.sub(' ', text).strip()
        multiline_text = ''
        paragraphs = text.split('|n|n ')
        for paragraph in paragraphs:
            lines = paragraph.split('|n ')
            for line in lines:
                formatted_line = textwrap.fill(line, width,
                                               initial_indent=indent,
                                               subsequent_indent=indent) + '\n'
                multiline_text += formatted_line
            multiline_text += '\n'
        return multiline_text

    def _split_lines(self, text, width):
        # Rewrites the _split_lines method to support multiline helps.
        text = self._whitespace_matcher.sub(' ', text).strip()
        lines = text.split('|n ')
        multiline_text = []
        for line in lines:
            multiline_text.append(textwrap.fill(line, width))
        multiline_text[-1] += '\n'
        return multiline_text


def init_logging(logdir, level='INFO'):
    """
    Initiates the logging configuration (output, message formatting).
    In the case of a logfile, the logfile name is unique and formatted as follows:
    ``name-YYYYMMDD-HHMMSS-JOBID.log``

    :param str logdir: The relative or absolute logfile directory. If ``None`` the standard output is used.
    :param str level: The log level.

    """
    __LOG_LEVELS__ = {'CRITICAL': logging.CRITICAL,
                      'ERROR': logging.ERROR,
                      'WARNING': logging.WARNING,
                      'INFO': logging.INFO,
                      'DEBUG': logging.DEBUG,
                      'NOTSET': logging.NOTSET}
    logging.getLogger("requests").setLevel(logging.CRITICAL)  # Disables logging message from request library
    if logdir:
        logfile = 'esgprep-{0}-{1}.log'.format(datetime.now().strftime("%Y%m%d-%H%M%S"),
                                               os.getpid())
        if not os.path.isdir(logdir):
            os.makedirs(logdir)
        logging.basicConfig(filename=os.path.join(logdir, logfile),
                            level=__LOG_LEVELS__[level],
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%Y/%m/%d %I:%M:%S %p')
    else:
        logging.basicConfig(level=__LOG_LEVELS__[level],
                            format='%(asctime)s %(levelname)s %(message)s',
                            datefmt='%Y/%m/%d %I:%M:%S %p')


def directory_checker(path):
    """
    Checks if the supplied directory exists. The path is normalized without trailing slash.

    :param str path: The path list to check
    :returns: The same path list
    :rtype: *str*
    :raises Error: If one of the directory does not exist

    """
    directory = os.path.normpath(str(path))
    if not os.path.isdir(directory):
        msg = 'No such directory: {0}'.format(directory)
        raise ArgumentTypeError(msg)
    return directory


def version_checker(version):
    """
    Checks the version format from command-line.

    :type version: The version string from command-line
    :returns: The version if allowed
    :rtype: *str*
    :raises Error: If invalid version format

    """
    if re.compile(r'^[\d]{1,8}$').search(str(version)):
        if len(version) == 8:
            try:
                datetime.strptime(version, '%Y%m%d')
            except ValueError:
                msg = 'Invalid version date: {0}.'.format(str(version))
                raise ArgumentTypeError(msg)
        return version
    else:
        msg = 'Invalid version type: {0}.\nAvailable format is YYYYMMDD or an integer.'.format(str(version))
        raise ArgumentTypeError(msg)