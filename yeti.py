
import argparse
import pathlib
import os
import subprocess

DEBUG=False

def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert Classic pipelines')
    parser.add_argument('pipelineName', help='Name of the pipeline to convert')
    parser.add_argument('--debug', action='store_true', help='debug mode')
    parser.add_argument('--cli', type=pathlib.Path, default='/usr/local/bin/codefresh', help='path to the Codefresh classic CLI')
    args = parser.parse_args()
    global DEBUG
    DEBUG=args.debug

    if DEBUG:
        print(f"Pipeline: {args.pipelineName}")
        print(f"DEBUG: {args.debug}")
        print(f"CLI: {args.cli}")
    return args

def extractYaml(cli, pipelineName):
    if DEBUG:
      print(f"Running: {cli} get pip {pipelineName} -o yaml > pipeline.yaml")
    ret=subprocess.run(f"{cli} get pip  {pipelineName} -o yaml > pipeline.yaml",
          capture_output=True, shell=True) # stderr=subprocess.STDOUT, check=True
    if et.returncode != 0:
        print("Cannot extract the pipeline requested")
        print(f"  exit code: {ret.returncode}")
        print(f"  sdtout: {ret.stdout}")
        print(f"  error: {ret.stderr}")
        
def main():
    args=parse_arguments()
    os.makedirs(args.pipelineName, exist_ok=True)
    extractYaml(cli=args.cli, pipelineName=args.pipelineName)
if __name__ == "__main__":
    main()
