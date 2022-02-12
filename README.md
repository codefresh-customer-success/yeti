# yeti
Converter for Classic pipelines to CSDP Argo Workflows manifests

## Usage
```
% python3 c2csdp.py -h
usage: c2csdp.py [-h] [--debug] [--cli CLI] pipelineName

Convert Classic pipelines

positional arguments:
 filename  Name of the pipeline to convert

optional arguments:
 -h, --help    show this help message and exit
 --debug       debug mode
 --cli CLI     path to the Codefresh classic CLI
```
## Restrictions

* Parallel mode is not supported
* support only GitHub source
* support only git type
* support only freestyle steps
* stages are totally ignored
