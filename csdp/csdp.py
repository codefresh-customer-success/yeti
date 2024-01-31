#!/usr/bin/env python3

### IMPORTS ###
import logging
from multiprocessing import Condition
import uuid
import os
import sys
from string import Template
import yaml
from classic            import StepTypeNotSupported
from .eventsource       import EventSource
from .sensor            import Sensor
from .ingress           import Ingress
from .workflow_template import WorkflowTemplate

### GLOBALS ###


### FUNCTIONS ###
def convert_condition_into_depends_string(cond):
    '''Transform the string for the when V1 clause into a V2  depends step.state'''
    condition_conversion = {
        "success": ["Succeeded"],
        "failure": ["Errored"],
        "finished": ["Succeeded", "Errored"],
        "skipped": ["Skipped"]
    }
    str = " && ("
    counter= 0
    for c in condition_conversion[cond.state]:
        if counter != 0:
            str += "|| "
        str += '%s.%s' % (cond.step_name, c)
        counter += 1
    str += ")"
    return str
  
def create_plugin_task_block(plugin, previous):
    '''Create a block of Yaml in a dag to call a plugin'''
    logging.info("Create workflow template block for %s", plugin.name)
    block = {
        "name": plugin.name,
        #"continueOn": {"failed":not bool(plugin.fail_fast)},
        "templateRef": {
            "name": f"c2csdp.{plugin.plugin_name}.{plugin.plugin_version}",
            "template": plugin.plugin_name
        },
        "arguments": {
            "parameters": []
        }
    }
    for x in plugin.parameters:
        block['arguments']['parameters'].append(
            {
             "name": x.name,
             "value": x.value
            }
        )
    if previous:
        block['depends']=previous.name
        if previous.fail_fast == "true":
            plugin.conditions.append(Condition(previous.name, "failure"))
        logging.debug("Processing conditions")
        for x in plugin.conditions:
            block['depends'] += convert_condition_into_depends_string(x)
    else:
            logging.debug("NO conditions")

    return block

### CLASSES ###
class Csdp:
    """Class related to Codefresh Classic operations and data"""
    def __init__(self, v1, ingress_url, volume_size):
        self.logger = logging.getLogger(type(self).__name__)
        self.uuid=str(uuid.uuid1())
        self.ingress_url=ingress_url
        self.project = v1.project
        self.name = v1.name
        self.volume_size = volume_size
        self.event_source = EventSource(name=v1.name, project=v1.project,
            provider="github", uuid=self.uuid)
        self.sensor = Sensor(v1.project, v1.name, "github", self.uuid, self.volume_size)
        self.workflow_template = WorkflowTemplate(v1.project, v1.name)
        self.ingress = Ingress(v1.project)

    def save(self):
        '''Save the whole CSDP object to disk in the project folder'''
        os.makedirs(self.project, exist_ok=True)
        self.event_source.save(self.project, self.name)
        self.sensor.save(self.project, self.name)
        self.workflow_template.save(self.project, self.name)
        self.ingress.save(self.project)

    def convert_trigger(self, trig):
        '''convert the trigger and add it to the EventSource block'''
        (owner,repo_name) = trig.repo.split('/')
        self.logger.info("Convert Trigger %s", self.name)

        yaml_filename = "./manifests/eventBlock.template.yaml"
        with open(yaml_filename, mode='r', encoding='UTF-8') as file:
            contents = file.read()
            template = Template(contents)
        values = {
            'event': trig.events,
            'owner': owner,
            'repo_name': repo_name,
            'name': self.name,
            'project': self.project,
            'provider': trig.provider,
            'uuid': self.uuid,
            'ingress_url': self.ingress_url
        }
        event_yaml=template.substitute(values)
        self.event_source.manifest['spec'][trig.provider]=yaml.safe_load(event_yaml)

        block = {
            "path": f"/webhooks/{self.project}/{self.name}/{trig.provider}-{self.uuid}",
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
        self.ingress.manifest['spec']['rules'][0]['http']['paths'].append(block)
    #
    # Step is converted into:
    #  - a template in the workflow template
    #  - a call in the "pipeline" workflow
    def convert_step(self, step, previous_step = None):
        '''Convert a V1 step into a task'''
        self.logger.info("Converting step %s (%s)", step.name, step.type)

        if step.type == "plugins":
            template_block=create_plugin_task_block(step, previous_step)
            self.workflow_template.manifest['spec']['templates'][0]['dag']['tasks'].append(template_block)
        else:
            raise StepTypeNotSupported(step.type)

    def convert_variable(self, var, provider, uuid):
        '''Variable is added to the sensor (input to argoWorkflow)
           parameters (match payload to input param)
        '''
        self.sensor.manifest['spec']['triggers'][0]['template']['argoWorkflow']['source']['resource']['spec']['arguments']['parameters'].append(
            {"name": var.name, "value": var.value}
        )
        if var.source == 'pipeline':
            self.workflow_template.manifest['spec']['templates'][0]['inputs']['parameters'].append(
                {"name": var.name, "value": var.value}
            )
        else:
            self.workflow_template.manifest['spec']['templates'][0]['inputs']['parameters'].append(
                {"name": var.name}
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

    #
    # Add secret volumes to workflow template
    # Like in case of kaniko build for example
    def add_secret_volume(self, volume):
        'Add mount for secret volume - aka docker secrets for kaniko'
        self.workflow_template.manifest['spec']['volumes'].append(
            {
                "name": volume,
                "secret": {
                    "secretName": volume,
                    "items": [
                        {
                            "key": ".dockerconfigjson",
                            "path": "config.json"
                        }
                    ]
                }
            }
        )
### Setters and getters
    @property
    def workflow_template(self):
        return self._workflowTemplate

    @workflow_template.setter
    def workflow_template(self, value):
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
        if not value.manifest['kind'] == "Ingress":
            self.logger.error("This is not a ingress")
            raise TypeError
        self._ingress=value

    @property
    def event_source(self):
        return self._eventSource

    @event_source.setter
    def event_source(self, value):
        if not value.manifest['kind'] == "EventSource":
            self.logger.error("This is not an event source")
            raise TypeError
        self._eventSource=value

    @property
    def ingress_url(self):
        '''Return Ingress URL'''
        return self._ingress_url
    @ingress_url.setter
    def ingress_url(self, value):
        if not isinstance(value, str):
            raise TypeError
        if not value.startswith("https://"):
            self.logger.warning("Ingress url shold start with https://")
        self._ingress_url = value

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
    def volume_size(self):
        return self._volume_size

    @volume_size.setter
    def volume_size(self, value):
        if not isinstance(value, int):
            raise TypeError
        self._volume_size = value

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value
