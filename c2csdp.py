#!/usr/bin/env python3

### IMPORTS ###
import argparse
import logging
import yaml

from classic import Classic
from csdp import Csdp

def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert Codefresh Classic pipelines')
    parser.add_argument('filename',
        help='File containing the Codefresh Classic pipeline yaml code')
    parser.add_argument('--log-level', default='info',
        choices=['info', 'debug', 'warning', 'error', 'critical'],
        help='set the log level')
    args = parser.parse_args()
    return args
#
#   Main
#
def main():

    args=parse_arguments()
    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(format = log_format, level = args.log_level.upper())

    v1=Classic(args.filename)
    logging.debug("V1 object: %s", v1.print())
    v2=Csdp(v1)
    v2.save()

if __name__ == "__main__":
    main()