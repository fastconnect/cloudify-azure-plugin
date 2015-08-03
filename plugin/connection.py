from plugin import utils
from azure.servicemanagement import ServiceManagementService
from azure.storage.blobservice import BlobService


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

    def storageClient(self):
        """Represents the AzureConnection to storage Service from Azure
        """
        keys_storage = (self.client()).get_storage_account_keys(
                                     self._get_storage_account())

        return BlobService(
                    account_name= self._get_storage_account(),
                    account_key=keys_storage.storage_service_keys.primary
                    )

    def _get_azure_subscription(self):
        node_properties = \
            utils.get_instance_or_source_node_properties()
        return node_properties["subscription"]

    def _get_azure_certificate(self):
        node_properties = \
            utils.get_instance_or_source_node_properties()
        return node_properties["certificate"]

    def _get_storage_account(self):
        node_properties = \
            utils.get_instance_or_source_node_properties()
        return node_properties["storage_account"]
