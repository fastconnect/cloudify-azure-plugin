﻿import constants
import utils
import requests
from cloudify import ctx
from plugin import utils


class AzureConnectionClient():
    """Provides functions for getting the Azure Service Management Service
    """

    def __init__(self):
        self.connection = None
        self.token = None
        self._get_token()

    def azure_get(self, ctx, path, header={}):
        path = '{}/{}?api-version={}'.format(constants.AZURE_API_URL, path,
                                             constants.AZURE_API_VERSION
                                             )
        header.update({'Content-Type':'application/json', 
                       'Authorization':'Bearer {}'.format(self.token)
                       })
        ctx.logger.debug('Requests get: {} with header {}'.format(path, header))
        return self._azure_response(requests.get(path,headers=header))


    def azure_post(self, ctx, path, data, header={}):
         path = '{}/{}?api-version={}'.format(constants.AZURE_API_URL, path,
                                              constants.AZURE_API_VERSION
                                              )
         header.update({'Content-Type':'application/json', 
                       'Authorization':'Bearer {}'.format(self.token)
                       })
         return self._azure_response(requests.post(path,headers=header,json=data))


    def _get_token(self):
        if self.token is None:
            payload = {
                'grant_type': 'password',
                'client_id': constants.APPLICATION_ID,
                'username': ctx.node.properties['username'],
                'password': ctx.node.properties['password'],
                'resource': constants.RESOURCE_CONNECTION_URL,
            }
            ctx.logger.info('Getting token from Azure...')
            json = self._azure_response(requests.post(constants.TOKEN_URL,
                                                 data=payload
                                                 )
                                   )
            ctx.logger.info('Token\'s been successfully taken from Azure')
            self.token = json['access_token']
        else:
            ctx.logger.debug('Token\'s been already taken. Reusing it.')


    def _azure_response(self, response):
        json = response.json()
        ctx.logger.debug('Request : {}'.format(response.request.body))
        if response.status_code != 200:
            ctx.logger.debug('Raise WindowsAzureError: {}'.format(json))
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
            raise utils.WindowsAzureError(
                    response.status_code,
                    message
                    )
        else:
            return json
