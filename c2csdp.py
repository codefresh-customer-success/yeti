#!/usr/bin/env python3
'''
Codefresh Classic to CSDP pipeline converter
'''
### IMPORTS ###
import argparse
import logging
import classic
import csdp

def parse_arguments():
    '''Defining arguments to the script'''
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
    '''main function'''
    args=parse_arguments()
    log_format = "%(asctime)s:%(levelname)s:%(name)s.%(funcName)s: %(message)s"
    logging.basicConfig(format = log_format, level = args.log_level.upper())

    v1_pipeline=classic.Classic(args.filename)
    v2_object=csdp.Csdp(v1_pipeline, args.ingress_host, args.volume_size)

    logging.info("Processing triggers")
    for obj in v1_pipeline.triggers:
        trig = classic.Trigger(obj)
        logging.info("Processing Trigger %s", trig.name)
        v2_object.convert_trigger(trig)

    logging.info("Processing steps")
    previous = None
    for step in v1_pipeline.steps:
        v2_object.convert_step(step, previous)
        previous = step.name

    logging.info("Processing variables")
    for var in v1_pipeline.variables:
        v2_object.convert_variable(var, "github", v2_object.uuid)

    logging.info("Processing secret volumes")
    for vol in v1_pipeline.secretVolumes:
        v2_object.add_secret_volume(vol)

    v2_object.save()

if __name__ == "__main__":
    main()
