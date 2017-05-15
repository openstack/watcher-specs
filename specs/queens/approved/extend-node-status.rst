..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==================================
extend node status in compute CDM
==================================

https://blueprints.launchpad.net/watcher/+spec/extend-node-status


Problem description
===================
We can get a node status through CDM(cluster data model) in watcher. Most of
the strategies rely on the node's status. But the existing status just meets
existing strategies. We need to extend nodes status description for new
strategies.
Moreover, there are some potential problems in usage. For example, to activate
one compute node which is disabled not by watcher, it will conflict.

Use Cases
---------
As an end user, I want watcher to enable a compute node which is
disabled by watcher not by others.

Proposed change
===============

Now we just use for words(up/down/enabled/disabled) to describe one compute
node. That is not enough.

This spec will add 'disabled_reason' field into 'ComputeNode' resource.
It will avoid potential usage problems, if we distinguish which nodes are
disabled by Watcher and which are not by Watcher. If a node is "disabled"
by Watcher(with "disabled_reason" "watcher_disabled"), then it is in the
optimize scope. If a node is "disabled" not by Watcher(without specific
"disabled_reason"), then it is out of the optimize scope, Wather shouldn't
do any optimization to it.


Alternatives
------------

None

Data model impact
-----------------

None

REST API impact
---------------

None

Security impact
---------------
None

Notifications impact
--------------------

None

Other end user impact
---------------------

None

Performance Impact
------------------

None

Other deployer impact
---------------------

None

Developer impact
----------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
sue

Work Items
----------

 * add 'disabled_reason' filed into 'ComputeNode' resource, to distinguish
   which nodes are disabled by Watcher and which are not by Watcher.

Dependencies
============

Testing
=======

Unit tests

Documentation Impact
====================

None

References
==========

None

History
=======

None

