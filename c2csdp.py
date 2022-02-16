#!/usr/bin/env python3

### IMPORTS ###
import argparse
import logging
import yaml
import classic
import csdp

def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert Codefresh Classic pipelines')
    parser.add_argument('filename',
        help='File containing the Codefresh Classic pipeline yaml code')
    parser.add_argument('--log-level', default='info',
        choices=['info', 'debug', 'warning', 'error', 'critical'],
        help='set the log level')
    parser.add_argument('--ingress-host', required=True,
        help='Ingress URL - Required')
    parser.add_argument('--volume-size', default='20', type=int,
        help='Size (in Gi) of the volume to allocate')
    args = parser.parse_args()
    return args
#
#   Main
#
def main():

    args=parse_arguments()
    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(format = log_format, level = args.log_level.upper())

    v1=classic.Classic(args.filename)
    v2=csdp.Csdp(v1, args.ingress_host, args.volume_size)

    logging.info("Processing triggers")
    for obj in v1.triggers:
        trig = classic.Trigger(obj)
        logging.info("Processing Trigger %s", trig.name)
        v2.convertTrigger(trig)

    logging.info("Processing steps")
    previous = None
    for step in v1.steps:
        v2.convertStep(step, previous)
        previous = step.name

    logging.info("Processing variables")
    for var in v1.variables:
        v2.convertVariable(var, "github", v2.uuid)

    v2.save()

if __name__ == "__main__":
    main()
