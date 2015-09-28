# -*- coding: utf-8 -*-
########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

# Built-in Imports
import os
import importlib
import json
from time import sleep

# Cloudify Imports
try:
    from plugin import constants
except:
    import constants

from cloudify import ctx
from cloudify.exceptions import NonRecoverableError


def validate_node_property(key, ctx_node_properties):
    """Checks if the node property exists in the blueprint.

    :raises NonRecoverableError: if key not in the node's properties
    """

    if key not in ctx_node_properties:
        raise NonRecoverableError(
            '{0} is a required input. Unable to create.'.format(key))


def log_available_resources(list_of_resources):
    """This logs a list of available resources.
    """

    message = 'Available resources: \n'

    for resource in list_of_resources:
        message = '{0}{1}\n'.format(message, resource)

    ctx.logger.debug(message)


def unassign_runtime_property_from_resource(property_name, ctx_instance):
    """Pops a runtime_property and reports to debug.

    :param property_name: The runtime_property to remove.
    :param ctx_instance: The CTX Node-Instance Context.
    :param ctx:  The Cloudify ctx context.
    """

    value = ctx_instance.runtime_properties.pop(property_name)
    ctx.logger.debug(
        'Unassigned {0} runtime property: {1}'.format(property_name, value))


def get_instance_or_source_node_properties():

        if ctx.type == constants.RELATIONSHIP_INSTANCE:
            return ctx.source.node.properties
        elif ctx.type == constants.NODE_INSTANCE:
            return ctx.node.properties
        else:
            raise NonRecoverableError(
                'Invalid use of ctx. '
                'get_instance_or_source_node_properties '
                'called in a context that is not {0} or {1}.'
                .format(
                    constants.RELATIONSHIP_INSTANCE,
                    constants.NODE_INSTANCE))


def get_target_property(ctx, relationship_name, property_name):
    # FIX: this function will only return the first property found for
    # the first corresponding relationship found. Maybe return an array
    # of properties if more than one relationship correspond.
    if ctx.instance.relationships:
        for relationship in ctx.instance.relationships:
            if relationship.type == relationship_name:
                for property in relationship.target.instance.runtime_properties:
                    if property_name == property:
                        return relationship.target.instance.runtime_properties[property]
        raise NonRecoverableError(
                'Relationship property {} for {} has not been found.'.format(
                        property_name, ctx.node.name)
                )
    else:
        raise NonRecoverableError('Missing relationship for {}.'.format(
                                                        ctx.node.name)
                                  )


def wait_status(ctx, resource,
                expected_status=constants.SUCCEEDED, 
                timeout=600
                ):
    """ A helper to send request to Azure. The operation status
    is check to monitor the request. Failures are managed too.

    :param ctx: The Cloudify context to log information.
    :param resource: The resource to waiting for.
    :param expected_status: The expected status for the operation.
    :param timeout: Maximum time to wait in seconds.
    """

    module = importlib.import_module('plugin.{}'.format(resource), 
                                     package=None
                                     )
    ctx.logger.debug('Waiting state {} for {}...'.format(expected_status,
                                                        resource)
                    )
    status = 'empty'
    ttw=0

    while ((status != expected_status) and (status != constants.FAILED) and 
           (ttw <= timeout)):
        status = getattr(module, 'get_provisioning_state')()
        ctx.logger.info('{} is {}.'.format(resource, status))
        ttw += constants.TIME_DELAY
        sleep(constants.TIME_DELAY)
    
    if status != expected_status :
        raise NonRecoverableError(
            'Failed waiting {} for {}: {}.'.format(
                            expected_status, resource, status)
            )


def get_azure_config(ctx):
    
    if ctx.type == 'node-instance':
        if ctx.node.properties[constants.AZURE_CONFIG_KEY]:
            return ctx.node.properties[constants.AZURE_CONFIG_KEY]
        else:
            return ctx.provider_context[constants.AZURE_CONFIG_KEY]
    elif ctx.type == 'relationship-instance':
        if ctx.source.node.properties[constants.AZURE_CONFIG_KEY]:
            return ctx.source.node.properties[constants.AZURE_CONFIG_KEY]
        else:
            return ctx.provider_context[constants.AZURE_CONFIG_KEY]
    elif ctx.type == 'deployment':
        return ctx.node.properties[constants.AZURE_CONFIG_KEY]


class WindowsAzureError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return 'Error {}: {}.'.format(self.code, self.message)