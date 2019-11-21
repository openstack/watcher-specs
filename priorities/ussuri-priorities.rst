.. ussuri-priorities:

=========================
Ussuri Project Priorities
=========================

List of priorities the Watcher drivers team is prioritizing in Ussuri.

+------------------------------------------------+------------------------+
| Priority                                       | Owner                  |
+================================================+========================+
| `General purpose decision engine threadpool`_  | `Corne Lukken`_        |
+------------------------------------------------+------------------------+
| `Kubernetes helm charts and docker images`_    | `Corne Lukken`_        |
+------------------------------------------------+------------------------+
| `Rollback Mechanism`_                          | `su zhengwei`_         |
+------------------------------------------------+------------------------+
| `Provide scenario jobs for each strategy`_     | `Li Canwei`_           |
+------------------------------------------------+------------------------+
| `Event-driven optimization based`_             | `Li Canwei`_           |
+------------------------------------------------+------------------------+
| `the community-wide goals`_                    |  TBD                   |
+------------------------------------------------+------------------------+


.. _Corne Lukken: https://launchpad.net/~dantalion
.. _Li Canwei: https://launchpad.net/~li-canwei2
.. _su zhengwei: https://launchpad.net/~sue.sam


General purpose decision engine threadpool
------------------------------------------
Watcher spends a large portion of time waiting for I/O operations such as
writing to disc or waiting for responses to network requests. The time it
takes to perform such operations can typically be reduced significantly
by implementing parallelism. The general purpose threadpool for the decision
engine will allow arbitrary methods to be executed in parallel.
The amount of workers in the threadpool should be user configurable.

Kubernetes helm charts and docker images
----------------------------------------
Blueprint to track all activities related to being able to deploy Watcher
on K8s using helm charts. Also requires that the appropriate docker images
are created and uploaded to a registry.

Rollback Mechanism
------------------
After every audit, there would be one actionplan to execute.
Sometimes, the users want to rollback the actionplan or part of the actionplan
after one audit.
For host maintenance, it will migrate all instances from the maintaining host
to others. Aften the host maintenance and active again, there is no mechanism
to migrate the instances automatically back to the maintaining host.

Provide scenario jobs for each strategy
---------------------------------------
We have provided some tempest tests in Train release, and will continue to
improve the scenario tests for strategies.

Event-driven optimization based
-------------------------------
We propose an event-driven optimization-based audit control.
We wants to select among a list of events which may trigger the audit :
- React to a predicted situation.
- React to a critical situations and changes in system (e.g: threshold)
- A new compute node has been added to the cluster
- A compute node has been removed from the cluster
- A new virtual machine has been created

The events can be created by AODH, congress, ceilometer,
scoring engine (long term).

the community-wide goals
------------------------
https://governance.openstack.org/tc/goals/ussuri/index.html
