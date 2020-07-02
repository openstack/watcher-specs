.. victoria-priorities:

===========================
Victoria Project Priorities
===========================

List of priorities the Watcher drivers team is prioritizing in Victoria.

+------------------------------------------------+------------------------+
| Priority                                       | Owner                  |
+================================================+========================+
| `Rollback Mechanism`_                          | `su zhengwei`_         |
+------------------------------------------------+------------------------+
| `Kubernetes helm charts and docker images`_    | `Corne Lukken`_        |
+------------------------------------------------+------------------------+
| `time series framework`_                       | `Corne Lukken`_        |
+------------------------------------------------+------------------------+
| `the community-wide goals`_                    |  `Li Canwei`_          |
+------------------------------------------------+------------------------+

.. _su zhengwei: https://launchpad.net/~sue.sam
.. _Corne Lukken: https://launchpad.net/~dantalion
.. _Li Canwei: https://launchpad.net/~li-canwei2


Rollback Mechanism
------------------
After every audit, there would be one actionplan to execute.
Sometimes, the users want to rollback the actionplan or part of the actionplan
after one audit.
For host maintenance, it will migrate all instances from the maintaining host
to others. Aften the host maintenance and active again, there is no mechanism
to migrate the instances automatically back to the maintaining host.

Kubernetes helm charts and docker images
----------------------------------------
Blueprint to track all activities related to being able to deploy Watcher
on K8s using helm charts. Also requires that the appropriate docker images
are created and uploaded to a registry.

time series framework
---------------------
Strategies are currently limited to obtain information about metrics in
an aggregated form for the most recent measurements. This limits what
strategies can achieve as they are unable to retrieve information about past
occurrences or information about periodic patterns. A time series framework
will allow datasources to provide metrics over specific periods without
aggregation, allowing strategies to detect periodic patterns such as a weekly
contention and resolve these accordingly.

the community-wide goals
------------------------
https://governance.openstack.org/tc/goals/selected/victoria/index.html
