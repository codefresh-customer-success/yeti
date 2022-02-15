#!/usr/bin/env python3

### IMPORTS ###
import logging
import uuid
import os
import yaml

from string import Template

from .eventsource       import EventSource
from .sensor            import Sensor
from .ingress           import Ingress
from .workflow_template import WorkflowTemplate

### GLOBALS ###

### FUNCTIONS ###
def createFreestyleBlock(name, image, dir, commands):
    yaml_filename = "./manifests/freestyle.template.yaml"
    with open(yaml_filename, mode='r') as file:
        contents = file.read()
        template = Template(contents)
    values = {
        'name': name,
        'image': image,
        'dir': dir,
        'commands': commands
    }
    yamlBlock=template.substitute(values)
    return yaml.safe_load(yamlBlock)

def createTaskBlock(name, previous):
    block = { "name": name, "template": name}
    if previous:
        block['depends']=previous
    return block

### CLASSES ###
class Csdp:
    """Class related to Codefresh Classic operations and data"""
    def __init__(self, v1, ingressUrl):
        self.logger = logging.getLogger(type(self).__name__)
        self.uuid=str(uuid.uuid1())
        self.ingressUrl=ingressUrl
        self.project = v1.project
        self.name = v1.name
        self.eventSource = EventSource(name=v1.name, project=v1.project,
            provider="github", uuid=self.uuid)
        self.sensor = Sensor(v1.name, "github", self.uuid)
        self.workflowTemplate = WorkflowTemplate(v1.name)
        self.ingress = Ingress(v1.project)

    def save(self):
        os.makedirs(self.project, exist_ok=True)
        self.eventSource.save(self.project, self.name)
        self.sensor.save(self.project, self.name)
        self.workflowTemplate.save(self.project, self.name)
        self.ingress.save(self.project)

    def convertTrigger(self, trig):
        #
        # Add EventBlock to EventSource:
        (owner,repoName) = trig.repo.split('/')
        self.logger.debug("Convert Trigger %s", self.name)
        self.logger.debug("  owner %s", owner)
        self.logger.debug("  repo name %s", repoName)

        yaml_filename = "./manifests/eventBlock.template.yaml"
        with open(yaml_filename, mode='r') as file:
            contents = file.read()
            template = Template(contents)
        values = {
            'event': trig.events,
            'owner': owner,
            'repoName': repoName,
            'shortName': self.name,
            'project': self.project,
            'provider': trig.provider,
            'uuid': self.uuid,
            'ingressUrl': self.ingressUrl
        }
        eventYaml=template.substitute(values)
        self.logger.debug("Event block:\n %s", eventYaml)
        self.logger.debug("event source : %s", self.eventSource.manifest)
        self.eventSource.manifest['spec'][trig.provider]=yaml.safe_load(eventYaml)

        block = {
            "path": f"/webhooks/{self.project}/${self.name}/{trig.provider}-{self.uuid}",
            "backend": {
                "service": {
                    "name": f"{self.name}-eventsource-svc",
                    "port": {
                        "number": 80
                    }
                }
            },
            "pathType": "ImplementationSpecific"
        }
        self.logger.debug("Before inserting ingress block: %s", self.ingress.manifest['spec']['rules'][0])
        self.ingress.manifest['spec']['rules'][0]['http']['paths'].append(block)
    #
    # Step is converted into:
    #  - a template in the workflow template
    #  - a call in the "pipeline" workflow
    def convertStep(self, step, previousStep = None):
        if step.type == "freestyle":
            templateBlock=createFreestyleBlock(step.name, step.image, step.cwd, step.commands)
            self.workflowTemplate.manifest['spec']['templates'].append(templateBlock)
            taskBlock=createTaskBlock(step.name, previousStep)
            self.workflowTemplate.manifest['spec']['templates'][0]['dag']['tasks'].append(taskBlock)

    #
    # Variable is added to the sensor (input to argoWorkflow)
    # parameters (match payload to input param)
    def convertVariable(self, var, provider, uuid):
        self.sensor.manifest['spec']['triggers'][0]['template']['argoWorkflow']['source']['resource']['spec']['arguments']['parameters'].append(
            {"name": var.name, "value": var.value}
        )
        self.sensor.manifest['spec']['triggers'][0]['template']['argoWorkflow']['parameters'].append(
            {
                "dest": f"spec.arguments.parameters.{var.order}.value",
                "src": {
                     "dependencyName": f"{provider}-{uuid}",
                     "dataTemplate": var.path
                }
            }
        )

### Setters and getters
    @property
    def workflowTemplate(self):
        return self._workflowTemplate

    @workflowTemplate.setter
    def workflowTemplate(self, value):
        if not value.manifest['kind'] == "WorkflowTemplate":
            self.logger.error("This is not a workflowTemplate")
            raise TypeError
        self._workflowTemplate=value

    @property
    def sensor(self):
        return self._sensor

    @sensor.setter
    def sensor(self, value):
        if not value.manifest['kind'] == "Sensor":
            self.logger.error("This is not a sensor")
            raise TypeError
        self._sensor=value

    @property
    def ingress(self):
        return self._ingress

    @ingress.setter
    def ingress(self, value):
        self.logger.debug("Ingress setter value: %s", value)
        self.logger.debug("Ingress setter manifest: %s", value.manifest)
        self.logger.debug("Ingress setter kind: %s", value.manifest['kind'])
        if not value.manifest['kind'] == "Ingress":
            self.logger.error("This is not a ingress")
            raise TypeError
        self._ingress=value

    @property
    def eventSource(self):
        return self._eventSource

    @eventSource.setter
    def eventSource(self, value):
        if not value.manifest['kind'] == "EventSource":
            self.logger.error("This is not an event source")
            raise TypeError
        self._eventSource=value

    @property
    def ingressUrl(self):
        return self._ingressUrl
    @ingressUrl.setter
    def ingressUrl(self, value):
        if not isinstance(value, str):
            raise TypeError
        if not value.startswith("https://"):
            self.logger.warn("Ingress url shold start with https://")
        self._ingressUrl = value

    @property
    def project(self):
        return self._project

    @project.setter
    def project(self, value):
        if not isinstance(value, str):
            raise TypeError
        if len(value) < 3:
            raise ValueError
        self._project = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError
        if len(value) < 3:
            raise ValueError
        self._name = value

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value
