
import argparse
import pathlib
import os
import subprocess
import yaml
import uuid
import logging

import classic as v1

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
    logging.setLevel(arg.log-)
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
