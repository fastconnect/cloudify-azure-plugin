# -*- coding: utf-8 -*-
########
# Copyright (c) 2015 Fastconnect - Atost. All rights reserved
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

from cloudify.mocks import (MockCloudifyContext,
                            MockNodeInstanceContext,
                            MockNodeContext,
                            MockContext
                           )


class MockNodeInstanceContextRelationships(MockNodeInstanceContext):
    '''
    This class is used to mock the ctx.instance by adding a relationships
    property.
    '''

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
    

class MockRelationshipSubjectContext(object):
    '''
    This class is a mock for the ctx.source and ctx.target, it is used to fully
    mock a relationship context in Cloudify.
    To use this class you need to provide the properties and/or the runtime_
    properties of the source/target with dict:

        source = MockRelationshipSubjectContext(
                            properties={'prop_1_source': 'value_1'},
                            runtime_properties={'runtime_prop_1': value} 
                            )
    
        target = MockRelationshipSubjectContext(
                            properties={'prop_target_1': value}
                            )
    
    Then, place them in the MockCloudifyContextRelationship:

        mock_ctx = MockCloudifyContextRelationships(
                                 node_id='test',
                                 source=source,
                                 target=target
                                )
    '''

    def __init__(self, context=None, properties=None, runtime_properties=None):
        self.context = MockContext()
        self.node = MockNodeContext(id=None, properties=properties)
        self.instance = MockNodeInstanceContext(id=None, runtime_properties=runtime_properties)


class MockRelationshipContext(object):
    '''
    This class mock the context placed within ctx.instance to add
    the target property.
    '''

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
    '''
    This class is used to complete the Cloudify's mock context with
    relationships.
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
                            node_id=node_id,
                            node_name=node_name,
                            blueprint_id=blueprint_id,
                            deployment_id=deployment_id,
                            execution_id=execution_id,
                            properties=properties,
                            capabilities=capabilities,
                            related=related,
                            source=source,
                            target=target,
                            operation=operation,
                            resources=resources,
                            provider_context=provider_context,
                            bootstrap_context=bootstrap_context,
                            runtime_properties=runtime_properties)
        self._instance = MockNodeInstanceContextRelationships(
                                                node_id,
                                                runtime_properties, 
                                                relationships)
