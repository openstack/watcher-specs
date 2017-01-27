..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=====================
Make Applier parallel
=====================

https://blueprints.launchpad.net/watcher/+spec/parallel-applier

Problem description
===================

Watcher `Applier`_ starts `Action plan`_ with set of `Actions`_, which
are executed in a sequence. After `planner-storage-action-plan`_ is
implemented, we have new ``parents`` field that contains list of action's
uuid child action is connected to. Having ``parents`` field Watcher can build
Directed Acyclic Graph where each independent Action can be run in parallel
while actions with some dependencies should fulfill them to be executed.

Use Cases
----------

As an administrator, I would like to be able to run Action plan that will
launch actions for every node (compute, network, storage) in parallel.

Proposed change
===============

We can launch several concurrent actions in accordance with their parents.

Workflow engine of Watcher Applier will still use ``watcher_flow`` flow, but
edges between nodes should be established in accordance with action parents.
Unlinked actions with no parents should be connected directly to the
``watcher_flow`` and executed firstly.

Main class to modify is DefaultWorkFlowEngine, that defines workflow of
actions executing. Since Watcher Default Planner adds actions to DB
in accordance with weights (i.e. all migrate actions will be added firstly,
then resize actions and so on), Applier will get ordered by weight actions
that can be added to ``watcher_flow`` flow and linked in one ``for loop``.
In this case algorithm of building directed acyclic graph should have O(n)
complexity.

There is estimated pseudocode to show part of default planner's workflow::

    flow = gf.Flow("watcher_flow")
    for a in actions:
        task = TaskFlowActionContainer(a, self)
        flow.add(task)
        if a.parents:
            for parent_id in action.parents:
                parent_action = get_action(actions, parent_id)
                flow.link(parent_action, action, decider=self.decider)

    e = engines.load(flow)
    e.run()


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
Since it is perfomance related patch, it is expected to have perfomance
improvements because of parallel executing of actions instead of sequence.
In order to reduce the impact on system performance and stability,
it is better to set the maximum number of concurrent.


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
Alexander Chadin <a.chadin@servionica.ru>


Work Items
----------
* Modify watcher/applier/workflow_engine/default.py to build new parallel
  workflow engine.
* Update the documentation.
* Add appropriate unit tests.


Dependencies
============
https://blueprints.launchpad.net/watcher/+spec/planner-storage-action-plan

Testing
=======
* Unit tests will be added to validate these modifications.

Documentation Impact
====================

Update the `Applier`_ documentation in accordance with new changes.


References
==========

.. _Applier: http://docs.openstack.org/developer/watcher/glossary.html#watcher-applier
.. _Action plan: http://docs.openstack.org/developer/watcher/glossary.html#action-plan
.. _Actions: http://docs.openstack.org/developer/watcher/glossary.html#action
.. _planner-storage-action-plan: https://blueprints.launchpad.net/watcher/+spec/planner-storage-action-plan

History
=======
None