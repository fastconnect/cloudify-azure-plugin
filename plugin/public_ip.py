# -*- coding: utf-8 -*-
from plugin import (connection,
                    constants,
                    utils
                    )

from cloudify import ctx
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError


def get_provisioning_state(**_):
    utils.validate_node_property(constants.PUBLIC_IP_KEY, ctx.instance.runtime_properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_06
    public_ip_name = ctx.instance.runtime_properties[constants.PUBLIC_IP_KEY]

    response = connection.AzureConnectionClient().azure_get(
            ctx, 
            ("subscriptions/{}/resourcegroups/{}/"+
            "providers/microsoft.network/publicIPAddresses"+
            "/{}?api-version={}").format(
                subscription_id, 
                resource_group_name, 
                public_ip_name,
                api_version
            )
        )
    jsonGet = response.json()
    status_public_ip = jsonGet['properties']['provisioningState']
    return status_public_ip


def delete(**_):
    utils.validate_node_property(constants.PUBLIC_IP_KEY, ctx.instance.runtime_properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    api_version = constants.AZURE_API_VERSION_06
    public_ip_name =ctx.instance.runtime_properties[constants.PUBLIC_IP_KEY]

    response = connection.AzureConnectionClient().azure_delete(
      ctx, 
      ("subscriptions/{}/resourceGroups/{}/providers/microsoft.network" + 
      "/publicIPAddresses/{}?api-version={}").format(subscription_id, 
                                                    resource_group_name, 
                                                    public_ip_name, 
                                                    api_version
                                                    )
      )
    return response.status_code


def create(**_):
    utils.validate_node_property(constants.PUBLIC_IP_KEY, ctx.instance.runtime_properties)

    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    location = azure_config[constants.LOCATION_KEY]
    api_version = constants.AZURE_API_VERSION_06
    public_ip_name = ctx.instance.runtime_properties[constants.PUBLIC_IP_KEY]
    public_ip_allocation_method = "Dynamic"

    json ={
       "location": str(location),
       "properties": {
            "publicIPAllocationMethod": str(public_ip_allocation_method)
            }
        }

    cntn = connection.AzureConnectionClient()

    response = cntn.azure_put(ctx, 
                   ("subscriptions/{}/resourcegroups/{}/" +
                    "providers/microsoft.network" +
                    "/publicIPAddresses/{}" +
                    "?api-version={}").format(
                                            subscription_id, 
                                            resource_group_name, 
                                            public_ip_name, 
                                            api_version
                                            ),
                    json=json
                    )
    return response.status_code


def get_public_address_id(ctx):
    azure_config = utils.get_azure_config(ctx)

    subscription_id = azure_config[constants.SUBSCRIPTION_KEY]
    resource_group_name = azure_config[constants.RESOURCE_GROUP_KEY]
    location = azure_config[constants.LOCATION_KEY]
    api_version = constants.AZURE_API_VERSION_05_preview
    public_ip_name =ctx.instance.runtime_properties[constants.PUBLIC_IP_KEY]

    response = connection.AzureConnectionClient().azure_get(
                              ctx, 
                              ('subscriptions/{}' +
                              '/resourceGroups/{}' +
                              '/providers/microsoft.network/' +
                              'publicIPAddresses/{}' +
                              '?api-version={}').format(
                                  subscription_id,
                                  resource_group_name,
                                  public_ip_name,
                                  api_version
                                  )
                              )

    return response.json()['id']
