# -*- coding: utf-8 -*-
import constants
import requests
import re
from cloudify import ctx
from utils import WindowsAzureError


class AzureConnectionClient():
    """Provides functions for getting the Azure Service Management Service
    """

    def __init__(self):
        self.connection = None
        self.token = None
        self._get_token()

    def azure_get(self, ctx, path, header={}):
        path = '{}/{}'.format(constants.AZURE_API_URL, path)
       #ctx.logger.debug(path)
        header.update({'Content-Type':'application/json', 
                        'Authorization':'Bearer {}'.format(self.token)
                        })
        #ctx.logger.debug('Requests get: {} with header {}'.format(path, header))
        return self._azure_response(requests.get(path,headers=header))

    def azure_post(self, ctx, path, json, header={}):
        path = '{}/{}'.format(constants.AZURE_API_URL, path)
        #ctx.logger.debug(path)
        header.update({'Content-Type':'application/json', 
                    'Authorization':'Bearer {}'.format(self.token)
                    })
        return self._azure_response(requests.post(path,headers=header,json=json))


    def azure_put(self, ctx, path, json={}, header={}):
        path = '{}/{}'.format(constants.AZURE_API_URL, path)
        #ctx.logger.debug(path)
        header.update({'Content-Type':'application/json', 
                       'Authorization':'Bearer {}'.format(self.token)
                       })
        return self._azure_response(requests.put(path,headers=header,json=json))


    def azure_delete(self, ctx, path, header={}):
         path = '{}/{}'.format(constants.AZURE_API_URL, path)
         #ctx.logger.debug(path)
         header.update({'Content-Type':'application/json', 
                       'Authorization':'Bearer {}'.format(self.token)
                       })
         return self._azure_response(requests.delete(path,headers=header))


    def _get_token(self):
        if self.token is None:
            payload = {
                'grant_type': 'password',
                'client_id': constants.APPLICATION_ID,
                'username': ctx.node.properties['username'],
                'password': ctx.node.properties['password'],
                'resource': constants.RESOURCE_CONNECTION_URL,
            }
            #ctx.logger.info('Getting token from Azure...')
            json = self._azure_response(requests.post(constants.TOKEN_URL,
                                                 data=payload
                                                 )
                                   ).json()
            #ctx.logger.info('Token\'s been successfully taken from Azure')
            self.token = json['access_token']
        else:
            ctx.logger.debug('Token\'s been already taken. Reusing it.')


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
