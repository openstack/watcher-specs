..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=====================================================
Define a grammar able to compose consolidation rules
=====================================================

https://blueprints.launchpad.net/watcher/+spec/watcher-consolidation-grammar

The way VMs are placed on nodes is crucial for optimizing many aspects of a 
data centre (energy consumption, network latency, QoS, maintenance 
operations...).
Furthermore, many criteria can influence this VM placement: computational 
resources such as CPU, RAM and disk, security constraints, data centre 
policies...
It is thus needed to express each of those criteria in an independent manner 
using a specific language.
In this blueprint we define a grammar able to create such consolidation rules 
within Watcher.

*This BP is W.I.P.*

Problem description
===================

A detailed description of the problem. What problem is this blueprint
addressing?

Use Cases
----------

What use cases does this address? What impact on actors does this change have?
Ensure you are clear about the actors in each use case: Developer, End User,
Deployer etc.

Project Priority
-----------------

Does this blueprint fit under one of the :ref:`mitaka-priorities`? If so which
one and how?

Proposed change
===============

Selectors
---------

VM selectors:

+-----------------+-----------------------+-----------------------------------+
| **Name**        | **Parameters**        | **Description**                   |
+=================+=======================+===================================+
| AllVMs          | None                  | Selects all the VMs in the cluster|
+-----------------+-----------------------+-----------------------------------+
| getVMbyName     | n: the name of the VM | Selects the VM corresponding to   |
|                 |                       | the name.  Note that an identifier|
+-----------------+-----------------------+-----------------------------------+
| getVMbyProperty | p: a property name    | Select the VM group responding to |
|                 | v: the value to be    | the criterias                     |
|                 | matched               |                                   |
+-----------------+-----------------------+-----------------------------------+

Node selectors:

+-----------------+-----------------------+-----------------------------------+
| ** Name**       | **Parameters**        | **Description**                   |
+=================+=======================+===================================+
| AllNodes        | None                  | Selects all the Nodes in the      |
|                 |                       | cluster                           |
+-----------------+-----------------------+-----------------------------------+
| getNodebyName   | n: the name of the    | Selects the node corresponding to |
|                 | node                  | the name                          |
+-----------------+-----------------------+-----------------------------------+
| getNodeby       | p: a property name    | Select the node group coresponding| 
| Property        | v: a property value   | to the property                   |
+-----------------+-----------------------+-----------------------------------+


Serialization
-------------

The consolidation constraints are serialized as a list in YAML. For
example:

.. code::

	-  Root: VM1
	-  Ba:
	    vms: VM1, VM2
	    nodes: @N1, @N2
	-  Preserve:
	    nodes: allNodes
	    resource: “pcpu”
	    value: 80%

Note that any identifier not recognized as a keyword will be
deserialized as a VM name.

An identifier beginning with “@” will be deserialized as a node name.

Constraints
-----------

The following tables sums up the base constraints to build relations
between VMs and servers, respect the characteristics of the DC model,
the SLA and the policies.


Base constraints
~~~~~~~~~~~~~~~~

This section contains a summary of the constraints from BtrPlace.

Full description of constraints can be found here:

`*http://www-sop.inria.fr/members/Fabien.Hermenier/btrpcc/index.html* <http://www-sop.inria.fr/members/Fabien.Hermenier/btrpcc/index.html>`__

Those constraints establishes constraints on the relation VM-servers
(inspired from set theory). Some other constraints also establishes
criterias over the resources (Preserve, OverSubscription…) or the status
of the nodes (Online, Offline).


+-----------+--------------------------+---------------------------------------+
| **Name**  | **Parameters**           | **Description**                       |
+-----------+--------------------------+---------------------------------------+
| Root      | s : a set of VMs.        | The root constraint forces each       |
|           |                          | running VM in s to not move from its  |
|           |                          | current location.                     |
+-----------+--------------------------+---------------------------------------+
| Ban       | vs : a set of VMs.       | The ban constraint disallows each     |
|           | ns : a set of servers.   | running VM in vs to be hosted on any  |
|           |                          | of the online servers in ns.          |
+-----------+--------------------------+---------------------------------------+
| Fence     | s1 : a set of VMs.       | The fence constraint forces each      |
|           | s2 : a set of servers.   | running VM in s1 to be running on one |
|           |                          | of the online servers in s2.          |
+-----------+--------------------------+---------------------------------------+
| Quarantine| s : a set of servers.    | The quarantine constraint disallows   |
|           |                          | any VM running on servers other than  |
|           |                          | those in s to be relocated into a     |
|           |                          | server in s. In addition, every VM    |
|           |                          | running on a server in s cannot be    |
|           |                          | relocated to another server.          |
+-----------+--------------------------+---------------------------------------+
| Among     | vs : a set of VMs.       | The among constraint forces each      |
|           | ns : a set of set of     | running VM in vs to be hosted on one  |
|           | servers.                 | of the set of servers in ns.          |
+-----------+--------------------------+---------------------------------------+
| Lonely    | s : a set of VMs.        | The lonely constraint forces all the  |
|           |                          | running VMsin s to be running on      |
|           |                          | dedicated servers. Each of the used   |
|           |                          | servers can still host multiple Vms   |
|           |                          | but they have to be in s.             |
+-----------+--------------------------+---------------------------------------+
| Split     | vs : a set of set of     | The split constraint forces the given |
|           | VMs.                     | sets of Vms in vs to not share hosting|
|           | Sets inside vs must be   | servers. Each of the used servers can |
|           | disjoint.                | still host multiple VMs but they have |
|           |                          | to be in the same set.                |
+-----------+--------------------------+---------------------------------------+
| SplitAmong| vs : a set of set of     | The splitAmong constraint forces the  |
|           | Vms.                     | sets of VMs inside vs to be hosted on |
|           | Sets inside vs must be   | distinct set of servers in ns. Vms    |
|           | disjoint.                | inside a same set may still be        |
|           | ns : a set of set of     | collocated.                           |
|           | servers that is composed |                                       |
|           | of more sets than vs.    |                                       |
|           | Sets composing ns must   |                                       |
|           | be disjoint.             |                                       |
+-----------+--------------------------+---------------------------------------+
| Gather    | s : a set of at least 2  | The gather constraint forces all the  |
|           | VMs.                     | running Vms in the set s to be hosted |
|           |                          | on the same server.                   |
+-----------+--------------------------+---------------------------------------+
| Spread    | s : a set of at least 2  | The spread constraint forces all the  |
|           | VMs.                     | running Vms in s to be hosted on      |
|           |                          | distinct servers at any time,         |
|           |                          | even during the reconfiguration       |
|           |                          | process.                              |
+-----------+--------------------------+---------------------------------------+
| LazySpread| s : a set of at least 2  | The lazySpread constraint forces all  |
|           | VMs.                     | the running VMs in s to be hosted on  |
|           |                          | distinct servers at the end of a      |
|           |                          | reconfiguration process.              |
+-----------+--------------------------+---------------------------------------+
| Mostly    | s : a non-empty set of   | The mostlySpread constraint ensures   |
| Spread    | VMs.                     | the running virtual machines in s will|
|           | n: a positive number,    | be running on at least n              |
|           | inferior to the number   | distinct servers.                     |
|           | of virtual machines in s |                                       |
+-----------+--------------------------+---------------------------------------+
| Preserve  | s: a set of VMs.         | The preserve constraint ensures each  |
|           | r : a resource           | running VM in s is hosted on a server |
|           | identifier such as mem,  | having at minimum an amount of        |
|           | ucpu, pcpu to identify   | resource of type r equals to n        |
|           | the physical memory, the | dedicated to the VM.                  |
|           | computational capacity,  |                                       |
|           | the physical CPUs,       |                                       |
|           | respectively.            |                                       |
|           | n: a positive amount of  |                                       |
|           | resources                |                                       |
+-----------+--------------------------+---------------------------------------+
| Over      | s : a non-empty set of   | The oversubscription constraint       |
| subscript | servers                  | ensures the online servers in s have  |
| ion       | r : a resource           | for each hosted VM, an amount of free |
|           | identifier such as mem,  | resources at least equals to a given  |
|           | ucpu, pcpu to identify   | factor of a physical resource. Servers|
|           | the physical memory, the | not in the Online state and VMs not in|
|           | computational capacity,  | the Running state are ignored.        |
|           | the physical CPUs,       |                                       |
|           | respectively.            |                                       |
|           | x : a positive           |                                       |
|           | percentage               |                                       |
+-----------+--------------------------+---------------------------------------+
| Cumulated | s: a non-empty set of    | The cumulatedCapacity constraint      |
| Capacity  | servers.                 | restricts to a maximum of nb, the     |
|           | r : a resource           | total amount of a specific resource of|
|           | identifier such as vm,   | type r that can be used on the online |
|           | mem, ucpu, pcpu or nodes | servers in s to run VMs.              |
|           | to identify the number   |                                       |
|           | of virtual machines, the |                                       |
|           | physical memory, the     |                                       |
|           | computational capacity,  |                                       |
|           | the physical CPUs,       |                                       |
|           | respectively.            |                                       |
|           | nb: a positive amount of |                                       |
|           | resources.               |                                       |
+-----------+--------------------------+---------------------------------------+
| Single    | s: a non-empty set of    | The singleCapacity constraint         |
| Capacity  | servers.                 | restricts to a maximum of nb, the     |
|           | r : a resource           | amount of a specific resource of type |
|           | identifier such as mem,  | r that can be used on each of the     |
|           | ucpu, pcpu or vm to      | online servers in s to run VMs.       |
|           | identify the physical    |                                       |
|           | memory, the              |                                       |
|           | computational capacity,  |                                       |
|           | the physical CPUs or the |                                       |
|           | number of hosted Vms,    |                                       |
|           | respectively.            |                                       |
|           | nb: a positive amount of |                                       |
|           | resources.               |                                       |
+-----------+--------------------------+---------------------------------------+
| MinSpare  | s : a non-empty set of   | The minSpareResources restricts to at |
| Resources | servers.                 | least n, the number of free resources |
|           | rc : a resource          | directly available for VMs on the     |
|           | identifier such as mem,  | online servers in s. Servers in the   |
|           | ucpu, pcpu or nodes to   | Offline state are ignored.            |
|           | identify the physical    |                                       |
|           | memory, the              |                                       |
|           | computational capacity,  |                                       |
|           | the physical CPUs or the |                                       |
|           | node itself,             |                                       |
|           | respectively.            |                                       |
|           | n : a positive number    |                                       |
+-----------+--------------------------+---------------------------------------+
| MaxSpare  | s : a non-empty set of   | The maxSpareResources restricts to at |
| Resources | servers.                 | most n, the number of free resources  |
|           | rc : a resource          | directly available for VMs on the     |
|           | identifier such as mem,  | online servers in s. Servers in the   |
|           | ucpu, pcpu or nodes to   | Offline state are ignored.            |
|           | identify the physical    |                                       |
|           | memory, the              |                                       |
|           | computational capacity,  |                                       |
|           | the physical CPUs or the |                                       |
|           | node itself,             |                                       |
|           | respectively.            |                                       |
|           | n : a positive number    |                                       |
+-----------+--------------------------+---------------------------------------+
| MaxOnlines| s : a non-empty set of   | The maxOnlines ensures the number of  |
|           | servers.                 | online servers in s is inferior or    |
|           | n : a positive number,   | equals to n.                          |
|           | inferior to the number   |                                       |
|           | of servers in s.         |                                       |
+-----------+--------------------------+---------------------------------------+
| Offline   | s : a non-empty set of   | The offline constraint forces every   |
|           | servers.                 | server in s to be set in the Offline  |
|           |                          | state.                                |
+-----------+--------------------------+---------------------------------------+
| Online    | s : a non-empty set of   | The online constraint forces every    |
|           | servers.                 | server in s to be set in the Online   |
|           |                          | state.                                |
+-----------+--------------------------+---------------------------------------+

