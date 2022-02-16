# yeti
Converter for Classic pipelines to CSDP Argo Workflows manifests

## Usage
```
% usage: c2csdp.py [-h] [--log-level {info,debug,warning,error,critical}] --ingress-host INGRESS_HOST [--volume-size VOLUME_SIZE] filename

Convert Codefresh Classic pipelines

positional arguments:
  filename              File containing the Codefresh Classic pipeline yaml code

optional arguments:
  -h, --help            show this help message and exit
  --log-level {info,debug,warning,error,critical}
                        set the log level
  --ingress-host INGRESS_HOST
                        Ingress URL - Required
  --volume-size VOLUME_SIZE
                        Size (in Gi) of the volume to allocate

```
## Restrictions

* Parallel mode is not supported
* support only GitHub source
* support only git type
* stages are totally ignored

## Supported Steps and Conventions

Pipeline includes the following variables

1. CF_REPO_OWNER
2. CF_REPO_NAME
3. CF_BRANCH

### Freestyle

* working_directory ${{clone}} is honored

### git-clone

* secret github-token is required

### Build

* Build step is done with kaniko, it requires a docker-secert with the name of the registry. If none is passed, 'docker-config' secret is required.
  * Create a docker-registry secret with your docker credentials and apply it to your cluster under the runtime namespace
  * https://jamesdefabia.github.io/docs/user-guide/kubectl/kubectl_create_secret_docker-registry/
* disable_push is not honored yet
