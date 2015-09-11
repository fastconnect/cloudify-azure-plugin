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


def wait_status(ctx, resource, 
                start_status=constants.CREATING,
                wait_status=constants.SUCCEEDED
                ):
    """ A helper to send request to Azure. The operation status
    is check to monitor the request. Failures are managed too.

    :param ctx: The Cloudify context to log information.
    :param resource: The resource to waiting for.
    :param start_status: The initial status.
    :param wait_status: The expected status.
    """

    module = importlib.import_module('plugin.{}'.format(resource), 
                                     package=None
                                     )
    ctx.logger.debug('Waiting state {} for {}...'.format(wait_status,
                                                        resource)
                    )
    status = start_status

    while status == start_status :
        status = getattr(module, 'get_provisioning_state')()
        ctx.logger.info('{} is still {}.'.format(resource, status))
        sleep(constants.TIME_DELAY)
    
    if status != wait_status :
        raise NonRecoverableError(
            'Failed waiting {} for {}: {}.'.format(
                            wait_status, resource, status)
            )


class WindowsAzureError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return 'Error {}: {}.'.format(self.code, self.message)