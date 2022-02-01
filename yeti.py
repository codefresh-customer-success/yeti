
import argparse
import pathlib
import os
import subprocess
import yaml
import uuid

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
    global yamlData

    if DEBUG:
      print(f"Running: {cli} get pip {pipelineName} -o yaml > pipeline.yaml")

    ret=subprocess.run(f"{cli} get pip  {pipelineName} -o yaml > pipeline.yaml",
          capture_output=True, shell=True) # stderr=subprocess.STDOUT, check=True
    if ret.returncode != 0:
        print("Cannot extract the pipeline requested")
        print(f"  exit code: {ret.returncode}")
        print(f"  sdtout: {ret.stdout}")
        print(f"  error: {ret.stderr}")
        return null


    with open("pipeline.yaml", "r") as stream:
        try:
            yamlData=yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return yamlData

def createEvenSource(projectName, shortName, uuidStr, yamlData):
    provider=yamlData['spec']['triggers'][0]['provider']
    fullRepoName=yamlData['spec']['triggers'][0]['repo']
    (owner,repoName)=fullRepoName.split('/')
    ESYaml={
        'apiVersion': "argoproj.io/v1alpha1",
        'kind':'EventSource',
        'metadata': {
            'name': shortName
        },
        'spec': {
          'eventBusName': 'codefresh-eventbus',
          'service': {
            'ports': [ {'port': 80}]
          },
          'template': {
             'serviceAccountName': 'argo-server'
          },
          provider: {
            provider + '-' + uuidStr : {
              'events': ['push'],
              'repositories': [
                {
                    'owner': owner,
                    'names': [repoName]
                }
              ],
              'webhook': {
                'port': '80',
                'method': 'POST',
                'endpoint': '/webhooks/' + shortName + '/' + provider + '-' + uuidStr

              },
              'active': 'true',
              'insecure': 'false',
              'contentType': 'json',
              'deleteHookOnFinish': 'true',
              'apiToken': {
                'name': 'autopilot-secret',
                'key': 'git_token'
              }
            }
          }
        }
    }

    # Write file
    ESFile =  open(f"{projectName}/{shortName}.event-source.yaml", "w")
    yaml.dump(ESYaml, ESFile)
    if DEBUG:
        print("Generate EventSource:")
        print(yaml.dump(ESYaml))

def createSensor(projectName, shortName, uuidStr, yamlData):
    provider=yamlData['spec']['triggers'][0]['provider']
    sensorYaml={
      'apiVersion': "argoproj.io/v1alpha1",
      'kind':'Sensor',
      'metadata': {
        'name': shortName
      },
      'spec': {
        'eventBusName': 'codefresh-eventbus',
        'template': {
          'serviceAccountName': 'argo-server'
        },
        'dependencies': [
          {
            'name': provider + '-' + uuidStr,
            'eventName': provider + '-' + uuidStr,
            'eventSourceName': projectName
          }
          # TODO: Add filters
        ],
        'triggers': [
          {
            'template': {
              'name': shortName,
              'conditions': provider + '-' + uuidStr,
              'argoWorkflow': {
                'operation': 'submit',
                'source': {
                  'resource': {
                    'apiVersion': 'argoproj.io/v1alpha1',
                    'kind': 'WorkflowTemplate',
                    'metadata': {
                      'name': shortName + '-pipeline',
                      'spec': {
                        'arguments': {
                          'parameters': [
                                # TODO
                          ]     # parameter array
                        },      # arguments
                        'workflowTemplateRef' : {
                          'name': shortName+ '-template'
                          'template': 'pipeline'
                        },
                        'volumeClaimTemplates': [
                          {
                            'metadata': { 'name': 'codefresh-volume'},
                            'spec': {
                              'accessModes': ['ReadWriteOnce'],
                              'resources': {
                                'requests':{
                                  'storage': '20Gi'
                                }   #requests
                              }     # resources
                            }       # spec
                          }         # VolumeClaimTemplate element
                        ]           # VolumeClaimTemplate array
                      }
                    }
                  }                 # resource
                }                   # source
              }                     # argoWrokflow
            }                       # template
          }                         # trigger element
        ]                           # triggers array
      }                             # spec
    }                               # full Sensor

    # Write file
    sensorFile =  open(f"{projectName}/{shortName}.sensor.yaml", "w")
    yaml.dump(sensorYaml, sensorFile)
    if DEBUG:
        print("Generate Sensor:")
        print(yaml.dump(sensorYaml))

def createWorkflowTemplate(projectName, shortName, yamlData):
    wkfYaml={
      'apiVersion': "argoproj.io/v1alpha1",
      'kind':'WorkflowTemplate',
      'metadata': {
        'name': shortName + "-template"
      },
      'spec': {
        'entrypoint': 'pipeline',

        'templates': [
          {
            'name': 'pipeline',
            'inputs': {
                "parameters" : [
                    # TODO:
                        # pipeline variables
                        # shared config
                ]           # parameter array
            },              # inputs of pipeline
            'dag': {
              'tasks': []   # TO be filled later in process
            }               # dag
          }
        ]                   # templates array
      }                     # spec
    }                       # WorkflowTemplate

    # Write file
    wkfFile=open(f"{projectName}/{shortName}.workflow-template.yaml", "w")
    yaml.dump(wkfYaml, wkfFile)
    if DEBUG:
        print("Generate WorkflowTemplate:")
        print(yaml.dump(wkfYaml))

#
#   Main
#
def main():

    args=parse_arguments()
    yamlData=extractYaml(cli=args.cli, pipelineName=args.pipelineName)
    projectName=yamlData['metadata']['project'] if yamlData['metadata']['project'] else "default"
    pipelineShortName=yamlData['metadata']['shortName']

    # Generate Content
    os.makedirs(projectName, exist_ok=True)
    createWorkflowTemplate(projectName, pipelineShortName, yamlData)

    if len(yamlData['spec']['triggers']) == 0:
        print("No trigger defined")
        print(" Skipping EventSource Creation")
        print(" Skipping Sensor Creation")
    else:
        uuidStr=str(uuid.uuid1())
        createEvenSource(projectName, pipelineShortName, uuidStr, yamlData)
        createSensor(projectName, pipelineShortName, uuidStr, yamlData)




if __name__ == "__main__":
    main()
