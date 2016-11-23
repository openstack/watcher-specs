..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode


=============================================================================
Provide a graph model describing virtual & physical elements in a data center
=============================================================================

https://blueprints.launchpad.net/watcher/+spec/graph-based-cluster-model


To support a rich set of graph analysis methods during strategy determination
we want to have a simple graph model. The graph model should describe how VMs
are associated to compute hosts, how virtual networks entities are mapped to
physical networks devices, objects/block storage objects to physical storage
devices. Furthermore this shows how all these entities are interconnected (e.g.
showing how two VMs are connected virtually and subsequently through the
physical network). This allows for seeing relationships upfront between the
entities and hence can be used to identify hot/cold spots in the data center
and hence influence a strategy decision.


Problem description
===================

The information that represent the state and topology of a Cluster is derived
from different sources. Thus, the relation and association of different pieces
of data in order to effectively produce an optimization Strategy is a
challenging task. To this end, the Cluster Data Model is a vital source of
knowledge that contributes to the decision making. Relational data modeling
approaches do not capture efficiently the correlations of resource
deployments, network attributes, etc.

In this specification we propose a graph based data model that would aggregate
resource information for the Cluster and allow for the effective
representation of the topology (landscape) of workload deployments.
Through this model graph analysis techniques could be employed in the
context of the Strategy definition.

Use Cases
----------

The graph model representation of the virtual and physical resource of a
Cluster in Watcher would enhance the Cluster Data Model and allow powerful
analysis to be applied during the Strategy definition. For example, a goal
strategy developer would use the graph model to decide on a destination
hypervisor for a VM, which is not connected to the network of hypervisors
supporting the tenant/project VMs. Therefore, the use case that the proposed
solution affects the Strategy definition and the development of goals in
the context of Watcher. The affected actor in that use case is the Watcher
developer who has to suggest the appropriate Strategy for a Goal. He would
use the graph model included into the Cluster Data Model in order to acquire
information regarding the topology of the VMs, attributes of the physical
nodes etc.

Project Priority
-----------------

Not defined.

Proposed change
===============

The proposed model is a representation of the physical and virtual structure
of the resource existing in a data centre. It gives us an overview of where
a service is placed in the data centre, the underlying hardware, the network
components through which resources communicate, details about the virtual
servers and the virtual components that constitute an entire deployment etc.

Retrieval of the graph model will be real-time and the structure will mirror
that of the infrastructure topology. The information of the cluster will be
gathered by polling the Openstack services (e.g. Nova, Neutron) in a
predefined time interval. The implemented service will keep in cache the
latest graph in order to minimize the interaction with the Openstack
services in continous requests.

Each application stack will be mapped with resources in the virtual layer
and each virtual layer resources will be mapped with physical layer nodes.
A mesh structure of the service, virtual and physical resource will be
captured. Each component will also have attributes attached, for example,
CPUs would have an attribute for the chipset family and VMs would have an
attribute for the flavor. The nodes in the physical layer will cover the
compute, network and storage nodes and will all contain attributes that
capture their specification. Similar approach will be followed for the
virtual layer with virtual compute, storage and network nodes to capture the
deployments on the Cluster.

Below we have presented what we believe is a good level of abstraction and
have categorized these components into layers:
Physical layer
* Machines
* Switches
* Memory
* Disks
* CPUs
* NICs
* Physical Bay
* Network link
* Router
* Storage NAS

Virtual Layer
* Virtual Machines
* VNICs
* VCPUs
* Virtual networks
* Virtual Storage
* Containers
* Virtual Bay (used by Magnum)

This is an indicative list of nodes that could populate the graph. The
exist type of nodes that will be offered is depended from the platfrom
services (e.g. Nova, Neutron, ODL etc.) available in the testbed.
Components in the landscape/topology will be represented as nodes and
connections to other components will be represented as edges between these
nodes. By doing this across all components, a graph outlining the structure
of a service will be built, which will visually show how a service in the data
centre looks and also allow paths to be easily traced. In addition, each node
has relationships with other nodes within the same layer (intra-layer) as well
as across the layers (inter-layer). By following such modeling we can capture
complex topologies and express various dependencies of the components of the
Cluster. Also, heterogenous components can be expressed in each layer and
therefore workloads with different requirements at the virtual or physical
layers can be captured.

The acquisition of the information regarding the topology of the Data Center
resource will be realized through the RESTful APIs exposed by OpenStack such
as Nova, Neutron etc.

Additionally using graphs to structure resource information will allow the
use of well researched and defined graph algorithms to derive further insights
from the graph model, an example of this would be the shortest path algorithm,
which could be used to improve performance across a data-center and more
immediately a given deployment.

Alternatives
------------

The effectiveness of the proposed solution is based on the graph
representation of the underlying resources and infrastructure.
Alternative approaches would be the use of simple relational modeling
and structures where the relationships of the objects are captures in a
separate entity or class. Such approach could be supported with relational
database schemes but in large scale Clusters it would result in high
complexity and inefficiency.

Data model impact
-----------------

There is no direct impact of the Watcher Data Model regarding the dependencies
of the entities in the Architecture.
The graph model will be provided by an independent module upon request and
could accompany (be a part of) the Cluster Data Model created by the Watcher
Decision Engine.


REST API impact
---------------

There is no impact on the core Watcher REST API. The graph cluster model
will expose its own APIs for retrieving the graph object.

Security impact
---------------

There is no impact on the Security.

Notifications impact
--------------------

There is no impact on the notifications.

Other end user impact
---------------------

There is no other impact.

Performance Impact
------------------

The generation of the graph model will be performed in realtime and upon
request. There is no significant performance impact estimated. In case the
on-demand graph creation is slow, the task will be triggered on the
background upon Watcher start-up and/or event realization.

Other deployer impact
---------------------

No specific deployer impact is envisaged.

Developer impact
----------------

It will not impact other developers working on OpenStack.


Implementation
==============

Assignee(s)
-----------

Intel is leading this work.
Main assignee: Kevin Mullery <kmullery>
Secondary assignees: Gregory Katsaros <gregory-katsaros>,
Thijs Metsch <tmetsch>

Work Items
----------

Workplan:
* Finalization of the conceptual methodology
* Definition of information to be captured and service APIs.
* Implementation of the graph model service:
Implementation of the graph model server from building
the NetworkX model.
Implementation of the RESTful endpoints and APIs for
graph extraction (json) and model acquisition.
* Integration and testing.


Dependencies
============

The cluster-model-objects-wrapper is a potential dependency and the efforts
on these two BP should be aligned.


Testing
=======

Several unit tests will be provided to test scenarios using a mock-up
cluster models.

Testing approaches comprising of unit tests and integration tests in which a
specific input is given and compared against the expected output.


Documentation Impact
====================

It will be necessary to add new content relating to the Cluster Data Model
operation of the Watcher Decision Engine.


References
==========

This work is related with research activities in the context
of the CloudWave FP7 EU project (www.cloudwave-fp7.eu). See also Apex Lake
(http://dl.acm.org/citation.cfm?id=2830016) for further information on the
modeling concept. The CloudSim (https://github.com/Cloudslab/cloudsim)
and SimGrid (http://simgrid.gforge.inria.fr/) can be cited as related
infrastructure models.


History
=======

No history.
