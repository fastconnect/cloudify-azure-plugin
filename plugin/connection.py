from plugin import utils
from azure.servicemanagement import ServiceManagementService

class AzureConnectionClient():
    """Provides functions for getting the Azure Service Management Service
    """

    def __init__(self):
        self.connection = None

    def client(self):
        """Represents the AzureConnection Client
        """

        azure_subscription = self._get_azure_subscription()
        azure_certificate = self._get_azure_certificate()

        return ServiceManagementService(azure_subscription, 
                                        azure_certificate)
    
    def _get_azure_subscription(self):
        node_properties = \
            utils.get_instance_or_source_node_properties()
        return node_properties["subscription"]
    
    def _get_azure_certificate(self):
        node_properties = \
            utils.get_instance_or_source_node_properties()
        return node_properties["certificate"]
