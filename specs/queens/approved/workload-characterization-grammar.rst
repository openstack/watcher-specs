..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

============================================
Define grammar for workload characterization
============================================

https://blueprints.launchpad.net/watcher/+spec/workload-characterization-grammar


Problem description
===================
When applications are deployed in cloud, they compete for
resources and it becomes a challenge for "cloud operators to
ensure" and "tenants to get" desired performance and quality of
service (QoS) for the workloads.

When we run several workloads in cloud, we need to characterize
these workloads as input to watcher for profiling, fingerprinting,
application QoS, placements and consolidation. `Audit`_ can refer to these
grammars and implement QoS `Strategy`_

Also, from a cloud infrastructure standpoint, these workload
characteristics can also be used to gauge SLAs and decisions
for killing or rebalancing workloads elsewhere.

An example of workload characterization is a weighted
combination of CPU, Memory or any other resource attributes
like High IOPs, Network latency etc.

Scope of this blueprint is -

* A definition of a grammar for characterizing workload specific targeting at
  composite metrics for a VM.
* A lightweight solution for parsing the defined grammar using the
  `TOSCA-Parser`_ library.
* A solution for persisting the grammar for VMs leveraging VM metadata.


Use Cases
---------
As an OpenStack administrator or user, I want to be able to create a TOSCA
structured workload character.
As an OpenStack administrator or user, I want to be able to build an
optimization strategy using the defined workload character grammar.

Project Priority
----------------
Pike

Proposed change
===============
Workload characterization is important for QoS to achieve
performance goals and SLAs. Building optimization strategies or
workload placement based on the defined workload character.

**Defining a workload character**


A workload character will constitute one or more Performance
Units.

A Performance Unit will have a resource name (Example - vcpus, cpu_util,
memory, memory.usage, disk.device.iops), Value (Number of CPU Cores, Memory
in MB, Number of IOPs), Unit, an Operator (>, <, =), and Weight (priority
ranging from -20 to 19 for highest and lowest priorities respectively).
Weights are used to create a threshold to optimally run the workload.


Resource name and units should be in compliance with Nova and any strategy
supported metric services.


Example of a performance unit:

* vcpus = 2 Cores
* cpu_util > 90 %
* memory.usage > 2000 MB
* disk.device.iops > 1500 counts/s

Examples of Workload Characters

* cpu_bound_workload: (vcpus = 2 Cores OR cpu_util > 90)
* big_data_workload = (memory.usage > 2000 MB AND disk.device.iops < 1500
  counts/s)

**Represent workload character using TOSCA**


The above can be represented in a TOSCA structure

Example :

::

 cpu_bound_workload =
     watcher:
       derived_from: tosca.nodes.Root
         description: '{vcpus} or {cpu_util}'
           properties:
             vcpus:
               required: true
               weight: -20
               type: integer
               constraints:
                 - equal: 2
             cpu_util:
               required: true
               weight: 19
               type: integer
               constraints:
                 - greater_than: 90


 disk_io_workload=
     watcher:
       derived_from: tosca.nodes.Root
         properties:
           disk_iops:
             required: true
             weight: 5
             type: integer
             constraints:
               - greater_than: 1200

**Parse and validate workload grammar**


Use `TOSCA-Parser`_  module to parse a TOSCA serialized workload
grammar and validate it by applying values from telemetry
or other metrics.

Snippet to parse a grammar -

::

    from toscaparser.nodetemplate import NodeTemplate

    custom_snippet = '''
    watcher:
      derived_from: tosca.nodes.Root
      description: '{vcpus} or {cpu_util}'
      properties:
        vcpus:
          required: true
          weight: -20
          type: integer
          constraints:
            - equal: 2
        cpu_util:
          required: true
          weight: 19
          type: integer
          constraints:
            - greater_than: 90
    '''
    custom_def = yamlparser.simple_parse(custom_snippet)
    equation = custom_def['watcher']['description']
    data = '''
    server:
      type: watcher
      properties:
        vcpus: 2
        cpu_util: 89
    '''
    parsed_data = yamlparser.simple_parse(data)
    nodetemplate = NodeTemplate('server', parsed_data, custom_def)
    p_names = {}
    for p in nodetemplate.get_properties_objects():
        try:
            p.validate()
            p_names[p.name] = True
        except:
            p_names[p.name] = False

    print(equation.format(**p_names))

Output -

::

  True


Here is more examples and documentation -
https://pypi.python.org/pypi/tosca-parser/0.7.0


**Store Grammar in VM Metadata**

The grammar should be added as VM Metadata. Watcher will then poll this data
and make it available in the cluster data model for `Audit`_  and `Strategy`_
to refer.  This metadata addition will be watcher specific and should have an
identifiable key like "watcher-workload-grammar".

Example to store grammar in VM Metadata -

::

  {
  "meta": {
    "workload_character":
    "watcher:
       derived_from: tosca.nodes.Root
       description: '{vcpus} or {cpu_util}'
       properties:
         vcpus:
           required: true
           weight: -20
           type: integer
           constraints:
             - equal: 2
         cpu_util:
           required: true
           weight: 19
           type: integer
           constraints:
             - greater_than: 90"
   }
  }


  curl -H 'Content-Type: application/json' -H "X-Auth-Token: token" -X PUT -d '{
  "meta": {
    "workload_character":
    "watcher:
       derived_from: tosca.nodes.Root
       description: '{vcpus} or {cpu_util}'
       properties:
         vcpus:
           required: true
           weight: -20
           type: integer
           constraints:
             - equal: 2
         cpu_util:
           required: true
           weight: 19
           type: integer
           constraints:
             - greater_than: 90"
   }
  }'
  https://openstack_controller:8774/v2.1/tenant_id/servers/9b4daf23-c01c-44ad-a
  f7-4c20a7b382d6/metadata/workload_character




Alternatives
------------
No Alternatives

Data model impact
-----------------

Modifications will be made to the cluster data model to read and store VM
metadata in memory for strategies and audits to reference.


REST API impact
---------------
None.

Security impact
---------------
None.

Notifications impact
--------------------
None.

Other end user impact
---------------------
None.

Performance Impact
------------------
None.

Other deployer impact
---------------------
None.

Developer impact
----------------
None.

Implementation
==============

Assignee(s)
-----------
Intel and Walmart are working together on this blueprint.

Primary assignee:

  Chris Spencer(chrisspencer)
  Prashanth Hari (hvprash)
  Susanne Balle (sballe)


Other contributors:

Work Items
----------
* Create module for parsing the grammar
* Modify cluster data model to read VM Metadata and store in memory for
  strategies and audits to refer
* Refactor the code to populate workload grammar from vm_metadata in cluster
  data model
  - Model Root - https://git.io/vXSbA
  - Nova cluster data model - https://git.io/vXS9N



Dependencies
============
None.


Testing
=======
None.


Documentation Impact
====================
None.


References
==========
None.


History
=======

.. _Strategy: http://docs.openstack.org/developer/watcher/glossary.html#strategy
.. _Audit: http://docs.openstack.org/developer/watcher/glossary.html#audit
.. _TOSCA-Parser: https://wiki.openstack.org/wiki/TOSCA-Parser
.. _ceilometer measurements: http://docs.openstack.org/admin-guide/telemetry-measurements.html
.. _gnocchi metrics: https://docs.openstack.org/developer/gnocchi/rest.html#metrics
