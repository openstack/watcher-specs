..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

===================================================
Define the scope of an Audit as a pool of resources
===================================================

Include the URL of your launchpad blueprint:

https://blueprints.launchpad.net/watcher/+spec/define-the-audit-scope

Watcher aims at providing a flexible solution for auditing any pool of
resources and optimizing it.

This blueprint aims at providing a generic way to define the scope of an
`Audit`_.

The set of audited resources will be called "*Audit scope*" and will be defined
in each `Audit Template`_ (which contains the Audit settings).

Problem description
===================

So far, when an Audit is launched, the whole `OpenStack cluster`_ is audited
and there is no way for the admin to provide a logical subset of the
infrastructure (host aggregate, availability zone, network, Hadoop cluster,
storage volume, ...).

It should be possible to define the set of resources that needs to be
optimized independently from the goal of the audit and from the underlying
OpenStack services (Nova, Neutron, Sahara, ...).

Use Cases
----------

As an operator with an admin role
I want to be able to define in an Audit Template the scope of the Audit
so that I can optimize some subset of the infrastructure

As an operator with an admin role
I want to be notified when a resource UUID that I have added to an Audit scope
does not exist or can not be handled by any optimization strategy
so that I know whether my audit scope is valid or not

As a developer
I want to be able to define the scope of an Audit with a generic description
mechanism
so that I can develop optimization strategies for any kind of OpenStack
resource

Project Priority
-----------------

Not relevant because Watcher is not in the big tent so far.

Proposed change
===============

The `Audit Template`_ should have a new attribute, named "*scope*", which
contains the list of resources to optimize during the audit. If this attribute
is not defined, the whole default availability zone is taken by default.

The scope is defined as an array of resource types and for each resource type
an array of resource uuid(s):

::

  "scope": [
            {"OS::Nova::HostAggregate": [
              {"id": "2ba3ba40-c377-11e5-9912-ba0be0483c18"},
              {"id": "3eb70308-cabc-f1e5-7652-ba0be0483c18"},
              {"id": "30f3cc36-1fcc-4230-8907-042cdc4d4f75"}
            ]},
            {"OS::Cinder::Volume": [
              {"id": "25a145d1-a9bc-4e08-afe0-d9cd3a864a26"},
              {"id": "ddac9f1b-0666-47d8-a49b-3be89fc14a24"}
            ]}
          ]

For consistency with the other OpenStack services, the resource type can be any
type belonging to the list provided in the Heat orchestration project and
Watcher will use the same naming as Heat:
http://docs.openstack.org/developer/heat/template_guide/openstack.html

The advantage of using this naming conventions for resource types is that it
enables Watcher to know which OpenStack service is in charge of a given type of
resource (Nova, Neutron,...).

It should be possible to indicate all resources of a given type by using some
wildcard character, instead of an array of specific UUIDs. For example, to
select all Nova compute nodes and all Cinder volumes, the scope would be
defined like this:

::

  "scope": [
            {"OS::Nova::Server": [
              {"id": "*"}
            ]},
            {"OS::Cinder::Volume": [
              {"id": "*"}
            ]}
          ]

When a scope is created or updated, all the resource UUIDs are verified in
order to make sure that the resource exists and can be handled by the strategy
associated to the `Goal`_ of the `Audit Template`_.

There should also be a periodic task which regularly checks the validity of
all the audit scopes. If a resource UUID does not exist any more, a warning
should be added to the Watcher logs.

Estimated changes are going to be in the following places:

* in the `Watcher Decision Engine`_, the `Strategies`_ will receive the audit
  scope as an input parameter
* in the `Watcher API`_, the audit template object must be updated with a
  new scope field and some verifications must be added regarding the existence
  of resource types and UUIDs added to the audit scope.

Alternatives
------------

None

Data model impact
-----------------

The following data object will be impacted:

* **AuditTemplate**:

  * We should be able to store in the database the scope defined as an array
    of resource types and for each resource type an array of resource uuid(s).

REST API impact
---------------

There will be an impact on every REST resource URLs that starts with
**/v1/audit_template/** and that uses the type **AuditTemplate**:

* GET /v1/audit_template
* GET /v1/audit_template/(audit_template_uuid)
* POST /v1/audit_template
* PATCH /v1/audit_template
* GET /v1/audit_template/detail

The type **AuditTemplate** will contain a new **Scope** object with an array
of resource types and for each resource type, an array of resource uuid(s).

Here is a sample of the new JSON payload for an audit template which includes
the **Scope** object composed of three Nova Host Aggregates and two Cinder
volumes:

::

  {
      "created_at": "2016-01-07T13:23:52.761933",
      "deleted_at": null,
      "description": "Description of my audit template",
      "extra": {
          "automatic": true
      },
      "goal": "MINIMIZE_ENERGY",
      "scope": [
        {"OS::Nova::HostAggregate": [
        {"id": "2ba3ba40-c377-11e5-9912-ba0be0483c18"},
        {"id": "3eb70308-cabc-f1e5-7652-ba0be0483c18"},
        {"id": "30f3cc36-1fcc-4230-8907-042cdc4d4f75"}
        ]},
        {"OS::Cinder::Volume": [
        {"id": "25a145d1-a9bc-4e08-afe0-d9cd3a864a26"},
        {"id": "ddac9f1b-0666-47d8-a49b-3be89fc14a24"}
        ]}
      ]
      "links": [
          {
              "href": "http://localhost:9322/v1/audit_templates/27e3153e-d5bf-4b7e-b517-fb518e17f34c",
              "rel": "self"
          },
          {
              "href": "http://localhost:9322/audit_templates/27e3153e-d5bf-4b7e-b517-fb518e17f34c",
              "rel": "bookmark"
          }
      ],
      "name": "My Audit Template",
      "updated_at": "2016-01-07T13:23:52.761937",
      "uuid": "27e3153e-d5bf-4b7e-b517-fb518e17f34c"
  }


Security impact
---------------

None

Notifications impact
--------------------

An alarm should be sent whenever an audit scope is no longer valid for one of
the following reasons:

* a resource type does not exist
* a resource UUID does not exist
* a resource type can not be handled by any optimization strategy associated
  to the goal of the audit template

Other end user impact
---------------------

* The **python-watcherclient audit-template-create** command will be updated to
  handle the scope definition provided in a JSON file
* The **python-watcherclient audit-template-show** command will be updated to
  display the audit scope JSON definition
* The **python-watcherclient audit-template-list --detail** command will be
  updated to display every audit scope JSON definition

Performance Impact
------------------

None

Other deployer impact
---------------------

The operator may have to configure the frequency of the periodic task that
regularly checks the validity of all the audit scopes.

Developer impact
----------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  None

Other contributors:
  jed56
  vincent-francoise
  david-tardivel

Work Items
----------

Here is the list of foreseen work items:

* Create a new **watcher/objects/scope.py** class to handle the new data object
  that contains the array of resource types and for each resource type an array
  of UUIDs.
* Add a **scope** field to the  **watcher/objects/audit_template.py** class
* Update the **AuditTemplate** class in **watcher/db/sqlalchemy/models.py**
* Add the **scope** object as an input parameter of **execute()** method of
  the **BaseStrategy** class. Update the **execute_strategy()** method of
  **watcher/decision_engine/strategy/context/default.py** consequently.
* Update the **watcher/api/controllers/v1/audit_template.py** class to handle
  the new **scope** field and the verifications of resource types and UUIDs.
* Add some verification code to make sure a resource type or resource UUID
  added to an audit scope exists.
* Implement the code of the periodic task which makes sure every audit scope
  is still valid.
* Update unit tests and integration tests (Tempest scenarios)
* Provide the database migration script

Dependencies
============

This blueprint is related to the following blueprint:

* Today, the `Audit Template`_ has to be populated by hand. In this blueprint:
  https://blueprints.launchpad.net/watcher/+spec/query-list-of-auditable-resource-types-for-a-goal
  we would like to add some helpers which enable the admin to get the list of
  auditable ressources for a given goal, depending on which `Strategies`_ are
  installed on the `Watcher Decision Engine`_.

  Each strategy will be able to return the list of auditable resource types
  and therefore it will be possible to get a list of auditable resource UUIDs
  from Nova, Neutron, ...

  The admin will just need to select the auditable ressources he/she wants to
  add to the Audit Template, just like a customer would add products in a
  basket.

We should also submit a blueprint to the Heat project so that it would be
possible to get the list of available resource types in the
`OpenStack cluster`_ from the Heat API. This list would depend on what
OpenStack services have been installed on the infrastructure (Nova, Neutron,
Sahara,...). It would enable Watcher to check whether a resource type, that is
used in the audit scope, exists or not.

Testing
=======

Of course, the unit tests will have to be updated.

Need to update existing tempest scenarios which create an Audit Template and
define an Audit scope in it.

It would be interesting to create a test scenario which creates two Host
Aggregates in the test environment and make sure that the Audit only affects
the resources of the Host Aggregate which belongs to the Audit scope and
ignores the resources of the other Host Aggregate.

Another test should be written handling the case when a resource UUID used in
an audit scope does not exist any more.


Documentation Impact
====================

* need to define the concept of *Audit scope* in the Watcher glossary
* need to update the REST API documentation and show the JSON payload for
  defining an audit scope
* need to update the user's guide to show how to define the audit scope in a
  json file and create an Audit template with this file provided as input
  parameter for the scope.

References
==========

* List of OpenStack resource types defined for the Heat orchestration service:
  http://docs.openstack.org/developer/heat/template_guide/openstack.html
* Links to IRC discussions:

  * http://eavesdrop.openstack.org/meetings/watcher/2016/watcher.2016-01-27-14.00.log.html

History
=======

None


.. _Audit: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#audit
.. _Audit Template: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#audit-template
.. _managed resource: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#managed-resource
.. _OpenStack cluster: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#cluster
.. _Strategies: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#strategy
.. _Watcher Decision Engine: https://factory.b-com.com/www/watcher/doc/watcher/architecture.html#watcher-decision-engine
.. _Watcher API: https://factory.b-com.com/www/watcher/doc/watcher/architecture.html#watcher-api
.. _Goal: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#goal
