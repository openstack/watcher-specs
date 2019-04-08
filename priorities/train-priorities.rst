.. train-priorities:

========================
Train Project Priorities
========================

List of priorities the Watcher drivers team is prioritizing in Train.

+------------------------------------------------+------------------------+
| Priority                                       | Owner                  |
+================================================+========================+
| `File based Metric Map`_                       | `Sumit Dilip Jamgade`_ |
+------------------------------------------------+------------------------+
| `Global datasource preference`_                | `Corne Lukken`_        |
+------------------------------------------------+------------------------+
| `Add resource_name in action input parameter`_ | `chen ke`_             |
+------------------------------------------------+------------------------+
| `Add Show Datamodel API`_                      | `chen ke`_             |
+------------------------------------------------+------------------------+
| `Add force field to Audit`_                    | `Li Canwei`_           |
+------------------------------------------------+------------------------+
| `Support Placement API`_                       | `Li Canwei`_           |
+------------------------------------------------+------------------------+


.. _Sumit Dilip Jamgade: https://launchpad.net/~sumitjami
.. _Corne Lukken: https://launchpad.net/~dantalion
.. _Li Canwei: https://launchpad.net/~li-canwei2
.. _chen ke: https://launchpad.net/~chenker


File based Metric Map
---------------------
Allow watcher to load a yaml file which contains a map of internal metrics
names (as expected by watcher) to real metrics names in use in the
datasources.

Global datasource preference
----------------------------
Some clouds might only have a single datasource available setting the
datasource preference for every individual strategy is error prone and
time consuming. A global datasource preference prevents errors and
simplifies configuring watcher.

Add resource_name in action input parameter
-------------------------------------------
Currently watcher has only UUIDs for users to distinguish different actions
which is not friendly. This BP will add a resource_name field in action
input parameters which is more user friendly.

Add Show Datamodel API
----------------------
Add Show Datamodel API to see the information of the instance in
the specified scope.

Add force field to Audit
------------------------
As now, Watcher doesn't allow to launch a new audit when there is actionplan
ongoing. This is because if the new audit has the same data model as the
ongoing actionplan, the new audit may create a wrong actionplan.
But if there are different data model scope, we should allow the new audit
to run. We want to give the choice to User, if User set force to True when
launching audit, Watcher will execute the audit even other actionplan is
ongoing.

Support Placement API
---------------------
Placement provides a service for managing, selecting, and claiming available
resources in a cloud. Many Watcher strategies need to select a target host
for VM migrating. Watcher can improve the process by the help of placement.
