from cloudify.state import current_ctx
from cloudify.mocks import MockCloudifyContext

def mock_ctx(test_name):
    """ Creates a mock context for the instance
        tests
    """

    SUBSCRIPTION_ID = '3121df85-fac7-48ec-bd49-08c2570686d0'
    AZURE_USERNAME = 'api@louisdevandierefastconnect.onmicrosoft.com'
    AZURE_PASSWORD = 'Azerty@01'
    COMPUTE_USER = 'administrateur'
    COMPUTE_PASSWORD = 'Cloud?db'

    test_properties = {
        'subscription_id': SUBSCRIPTION_ID,
        'username': AZURE_USERNAME, 
        'password': AZURE_PASSWORD,
        'location': 'westeurope',
        'publisherName': 'Canonical',
        'offer': 'UbuntuServer',
        'sku': '12.04.5-LTS',
        'version': 'latest',
        'flavor_id': 'Standard_A1',
        'compute_name': test_name,
        'compute_user': COMPUTE_USER,
        'compute_password': COMPUTE_PASSWORD,
        'resources_prefix': 'boulay',
        'network_interface_name': 'cloudifynic',
        'storage_account': 'cloudifystorageaccount',
        'create_option':'FromImage',
        'resource_group_name': 'cloudifygroup',
        'management_network_name': 'cloudifynetwork',
        'management_subnet_name': 'cloudifysubnet',
        'ip_name': 'cloudifyip'
    }

    return MockCloudifyContext(node_id='test',
                               properties=test_properties)
