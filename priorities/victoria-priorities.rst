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


.. _su zhengwei: https://launchpad.net/~sue.sam


Rollback Mechanism
------------------
After every audit, there would be one actionplan to execute.
Sometimes, the users want to rollback the actionplan or part of the actionplan
after one audit.
For host maintenance, it will migrate all instances from the maintaining host
to others. Aften the host maintenance and active again, there is no mechanism
to migrate the instances automatically back to the maintaining host.
