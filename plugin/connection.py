# -*- coding: utf-8 -*-
import requests
import re
import time
from cloudify import ctx
from plugin import constants
from utils import (WindowsAzureError,
                   get_azure_config
                   )


class AzureConnectionClient():
    """Provides functions for getting the Azure Service Management Service
    """
    token = None
    expires_on = None
    def __init__(self):
        self.connection = None
        self._get_token()

    def azure_get(self, ctx, path, header={}):
        """Make a GET REST request to Azure

        :param ctx: The Cloudify ctx context.
        :param path: URI path of the request.
        :param header: header of the request.
        :return: The response of the request with his json and status code.
        """
        path = '{}/{}'.format(constants.AZURE_API_URL, path)
        #ctx.logger.debug(path)
        header.update({'Content-Type':'application/json',
                        'Authorization':'Bearer {}'.format(
                                      AzureConnectionClient.token
                                      )
                        })
        #ctx.logger.debug('Requests get: {} with header {}'.format(path, header))
        return self._azure_response(requests.get(path,headers=header))

    def azure_post(self, ctx, path, json, header={}):
        """Make a POST REST request to Azure

        :param ctx: The Cloudify ctx context.
        :param path: URI path of the request.
        :param json: json of the request.
        :param header: header of the request.
        :return: The response of the request with his json and status code.
        """
        path = '{}/{}'.format(constants.AZURE_API_URL, path)
        #ctx.logger.debug(path)
        header.update({'Content-Type':'application/json',
                    'Authorization':'Bearer {}'.format(
                                      AzureConnectionClient.token
                                      )
                    })
        return self._azure_response(requests.post(path,headers=header,json=json))

    def azure_put(self, ctx, path, json={}, header={}):
        """Make a PUT REST request to Azure

        :param ctx: The Cloudify ctx context.
        :param path: URI path of the request.
        :param json: json of the request.
        :param header: header of the request.
        :return: The response of the request with his json and status code.
        """
        path = '{}/{}'.format(constants.AZURE_API_URL, path)
        #ctx.logger.debug(path)
        header.update({'Content-Type':'application/json',
                       'Authorization':'Bearer {}'.format(
                                      AzureConnectionClient.token
                                      )
                       })
        return self._azure_response(requests.put(path,headers=header,json=json))

    def azure_delete(self, ctx, path, header={}):
        """Make a DELETE REST request to Azure

        :param ctx: The Cloudify ctx context.
        :param path: URI path of the request.
        :param header: header of the request.
        :return: The response of the request with his json and status code.
        """
        path = '{}/{}'.format(constants.AZURE_API_URL, path)
        #ctx.logger.debug(path)
        header.update({'Content-Type':'application/json',
                   'Authorization':'Bearer {}'.format(
                                  AzureConnectionClient.token
                                  )
                   })
        return self._azure_response(requests.delete(path,headers=header))

    def _get_token(self):
        if ((AzureConnectionClient.token is None) or
            (time.gmtime() > AzureConnectionClient.expires_on)) :

            azure_config = get_azure_config(ctx)

            payload = {
            'grant_type': 'password',
            'client_id': constants.APPLICATION_ID,
            'username': azure_config[constants.USERNAME_KEY],
            'password': azure_config[constants.PASSWORD_KEY],
            'resource': constants.RESOURCE_CONNECTION_URL,
            }
            #ctx.logger.info('Getting token from Azure...')
            response = requests.post(constants.TOKEN_URL, data=payload)
            json = self._azure_response(response).json()
            #ctx.logger.info('Token\'s been successfully taken from Azure')
            AzureConnectionClient.token = json['access_token']
            AzureConnectionClient.expires_on = time.gmtime(float(json['expires_on']))
        #else:
        #   ctx.logger.debug('Token\'s been already taken. Reusing it.')

    def _azure_response(self, response):
        #ctx.logger.debug('Request : {}'.format(response.headers))

        if not re.match(r'(^2+)', '{}'.format(response.status_code)):
            json = response.json()
            #ctx.logger.debug('Raise WindowsAzureError: {}'.format(json))
            if json.get('error_description'):
                message = 'Error {}: {}'.format(
                    response.status_code,
                    json['error_description']
                    )
            elif json.get('error'):
                message = 'Error {}: {}, {}'.format(
                    response.status_code,
                    json['error']['code'],
                    json['error']['message']
                    )
            else:
                message = 'Error {}: Unknwn error.'.format(
                                        response.status_code
                                        )
            raise WindowsAzureError(
                    response.status_code,
                    message
                    )
        else:
            return response