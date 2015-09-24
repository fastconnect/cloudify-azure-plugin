from cloudify.mocks import (MockCloudifyContext,
                            MockNodeInstanceContext,
                           )


class MockNodeInstanceContextRelationships(MockNodeInstanceContext):

    def __init__(self, id=None, runtime_properties=None, relationships=None):
        super(MockNodeInstanceContextRelationships, self).__init__(
                                                        id, 
                                                        runtime_properties)
        self._relationships = []
        if relationships:
        	for i, rel in enumerate(relationships):
        		self._relationships.append(MockRelationshipContext(
        										 rel['node_id'],
        										 rel['relationship_properties'], 
        										 rel['relationship_type'])
        									)
        self._instance = MockNodeInstanceContext(id, runtime_properties)

    @property
    def relationships(self):
        return self._relationships

    @property
    def instance(self):
        return self._instance
    

class MockRelationshipContext(object):

    def __init__(self, node_id=None, runtime_properties=None, type=None):
        self._target = MockNodeInstanceContextRelationships(node_id, runtime_properties)
        self._type = type

    @property
    def target(self):
        return self._target

    @property
    def type(self):
        return self._type


class MockCloudifyContextRelationships(MockCloudifyContext):
    
    def __init__(self,
                 node_id=None,
                 node_name=None,
                 blueprint_id=None,
                 deployment_id=None,
                 execution_id=None,
                 properties=None,
                 runtime_properties=None,
                 capabilities=None,
                 related=None,
                 source=None,
                 target=None,
                 operation=None,
                 resources=None,
                 provider_context=None,
                 bootstrap_context=None,
                 relationships=None):
        super(MockCloudifyContextRelationships, self).__init__(
                            node_id,
                            node_name,
                            blueprint_id,
                            deployment_id,
                            execution_id,
                            properties,
                            capabilities,
                            related,
                            source,
                            target,
                            operation,
                            resources,
                            provider_context,
                            bootstrap_context,
                            runtime_properties)
        self._instance = MockNodeInstanceContextRelationships(
                                                node_id,
                                                runtime_properties, 
                                                relationships)


''' How to use the MockCloudifyContextRelationships :

    New Property: relationships, Mandatory: No
    Required inputs: 
        - 'node_id': the id of the node (str),
        - 'relationship_type': the type of the relationship (str),
        - 'relationship_properties': a dict of properties

    ctx = MockCloudifyContextRelationships(
				node_id='id_nod',
                node_name='mock',
                blueprint_id='id_blue',
                properties={'prop_1': 'prop_1'},
                runtime_properties={'run_prop_1': 'run_prop_1'},
                relationships=[ {'node_id': 'id_nod',
                				 'relationship_type': 'type',
                				 'relationship_properties': 
                				 	{'runtime_relation': 'runtime_relation'}
                				 },
                				 {'node_id': 'id_nod_2',
                				 'relationship_type': 'type_2',
                				 'relationship_properties': 
                				 	{'runtime_relation': 'runtime_relation_2'}
                				 }
                                ]
                )
'''