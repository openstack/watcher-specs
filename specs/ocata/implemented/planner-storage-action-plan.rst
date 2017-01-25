..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=====================================
Improve the storage of the ActionPlan
=====================================

https://blueprints.launchpad.net/watcher/+spec/planner-storage-action-plan

Problem description
===================

`Action plan`_ is built by the default `planner`_ of the `decision-engine`_
service. Every `Action`_ is linked to the next one so we have linked list
of Actions as result of default planner's work. `Applier`_ service executes
the action plan. Launching actions in a sequence has negative influence
on performance, especially if there are a lot of actions. Every action
must be completed before next action will be run, so it will take
a lot of time to launch migration actions in sequence.

Use Cases
----------

As an administrator, I would like to be able to run an action plan that will
launch actions for every node (compute, network, storage) in parallel.

Proposed change
===============

We can launch several concurrent actions with the same action weight in
parallel.

This specification defines two different planners with the same input/output
dataflow: weight planner and workload stabilization planner. Each planner
should use new ``parents`` attribute that will store list of actions the
action is linked to, but there are different ways to fill up this attribute.

Weight planner is designed to get unified way to parallelize execution
of actions. It knows nothing about structure of specified actions and how they
are related to each other. The main goal is to build sets of actions ordered by
their weights. High weight actions will be planned before the low weight ones.
Parallelization is the availability to execute several actions, with the same
action type, in parallel. Parallelization factor is limited by another taskflow
parameter named max_worker. Administrator can specify each action type's weight
and its parallelization ability in the watcher configuration file.
Let's show example of acyclic directed graph for this planner:

::

    ---sleep2    ---migration1     ---resize1
   /         \  /             \   /          \
  I----sleep1-------migration2------resize2----resize3----E
                \             /
                 ---migration3

This graph is built with the following settings:

+-----------+--------+-----------------+
|           | Weight | Parallelization |
+===========+========+=================+
| Sleep     |   70   |        2        |
+-----------+--------+-----------------+
| Migration |   60   |        3        |
+-----------+--------+-----------------+
| Resize    |   50   |        2        |
+-----------+--------+-----------------+

Since there are three resize actions and only two are allowed to be executed
at the same time, the third resize action will be executed only when
the previous actions are done.

Weight planner is easy to configure and has to be considered
as new default planner.

Workload Stabilization planner respects features of action types by allowing
to affect on building of ``parents``. Some action types like resizing
the instance should be run only before/after migration of the same instance,
not in parallel. There are to be specified some constraints:

* Unlinked actions are to be performed in parallel.
* Only one action can be performed per instance at one time
* If there are more than one action per instance, linked actions must be
  executed in sequence with respect to action weights.

So we can add new attribute ``parents`` that will store list of actions
the current action is linked to. It can be shown using
the acyclic directed graph:

::

      ----------------a1(t=dis)-----------
     /                                    \
    |                                      \
    | ----------------a2(t=mig)-------------\
    |/                                       \
  I-----a3(t=mig) -- a31(t=res)---------------E
    |\                                       /
    | ----------a4(t=resize)----------------/
    |                                      /
     \                                    /
      a5(resource=123, -- a51(resource=123,
         t=mig)               t=resize)

Here we can see the following links:

* a1 action disables the compute node and is not linked with another action.
  It can be run in parallel with other action (there is no constraint).
* a2 action migrates the instance and is not linked with another action.
  It can be run in parallel with other action (there is no constraint).
* a3 action migrates the instance and is parent to a31 action.
  It can be run in parallel with other action.
* a31 action resizes an instance after this last one had been migrated
  by action a3.
* a4 action resizes the instance and is not linked with another action.
  It can be run in parallel with other action (there is no constraint).
* a5 action migrates the instance and is parent to a51 action.
  It can be run in parallel with other action.
* a51 action resizes the same instance after this last one had been migrated
  by action a5.

As we can see, all actions that are independent to each other can be performed
in parallel. Meanwhile, if some actions are linked to the same resource then
they are to be performed with respecting to action weights. Currently, we can
define the following weights:

* End of graph - 0
* Disable Compute Node - 1
* Resize instance - 2
* Migrate instance - 3
* Initial point - 4

There is estimated pseudocode to show part of workload stabilization
planner's workflow::

    action = [uuid, type, resource_id, metadata]

    init = Flow()

    action_weights = {
        'turn_host_to_acpi_s3_state': 0,
        'resize': 1,
        'migrate': 2,
        'sleep': 3,
        'change_nova_service_state': 4,
        'nop': 5,
    }

    actions = sorted_by_weights(descended)

    for action in actions:
        a_type = action['action_type']
        if a_type != 'turn_host_to_acpi_s3_state':
            db_action = self._create_action(context, action)
            plugin_action = self.load_child_class(
                db_action.action_type)
            parents = plugin_action.validate_parents(
                resource_action_map, action)
            if parents:
                db_action.parents = parents
                db_action.save()
        else:
            # if we have an action that will make host unreachable, we need to
              complete all actions (resize and migration type) related to the
              host.
            parent_actions = get_actions(metadata=action[metadata][host])
            resize_actions = [x for x in parent_actions if x[type] == resize]
            migration_actions = [x for x in parent_actions if x[type] == mig]
            resize_migration_parents = [x[parents] for x in resize_actions]
            # Since resize actions have less weight than migration, they may
              have migration actions as parents and must be connected to the
              turn_host_to_acpi_s3_state action firstly.
            action_parents = []
            action_parents.extend([x[uuid] for x in resize_actions])
            # Add migrations that aren't linked to resize type actions
            action_parents.extend([x[uuid] for x in migration_actions
                                  if [x[uuid]] not in resize_migration_parents)
            db_action = create_action(action, parents=action_parents)

This spec is limited to simple chained list of actions as action plan. The
second part of modifying action plan's executing will contain graph for
parallel executing of action plans.


Alternatives
------------
None

Data model impact
-----------------
* ``next`` column should be removed from the Action table.
* ``parents`` column should be added to the Action table. Type: JSON.
* ``first_action_id`` column should be removed from Action Plan table.
* ActionPlan object major version should probably be updated to 2.0

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
New configuration parameters in watcher.conf:

[watcher_planner]
planner = weight
#planner = workload_stabilization

[watcher_planners.weight]
#weights = turn_host_to_acpi_s3_state:10,resize:20,migrate:30,sleep:40,
change_nova_service_state:50,nop:60
#parallelization = turn_host_to_acpi_s3_state:2,resize:2,migrate:2,sleep:1,
change_nova_service_state:1,nop:1

[watcher_planners.workload_stabilization]
#weights = turn_host_to_acpi_s3_state:10,resize:20,migrate:30,sleep:40,
change_nova_service_state:50,nop:60

Performance Impact
------------------
None


Other deployer impact
---------------------
We will have 2 new planner extensions.
We should reinstall properly watcher by running pip install [-e].


Developer impact
----------------
None


Implementation
==============

Assignee(s)
-----------
Primary assignee:
Alexander Chadin <a.chadin@servionica.ru>

Other contributors:
Vincent Francoise <Vincent.FRANCOISE@b-com.com


Work Items
----------
* Update data model in accordance with proposed changes
  (in fact API and objects).
* Remove default planner.
* Add watcher/decision_engine/planner/weight.py and
  watcher/decision_engine/planner/workload_stabilization.py
* Make weight planner as default.
* Update the documentation.
* Add appropriate unit tests.


Dependencies
============
https://blueprints.launchpad.net/watcher/+spec/plugins-parameters

Testing
=======
* Unit tests will be added to validate these modifications.

Documentation Impact
====================

Update the `defaultplanner`_ documentation in accordance with new changes.


References
==========

.. _Applier: http://docs.openstack.org/developer/watcher/glossary.html#watcher-applier
.. _Action plan: http://docs.openstack.org/developer/watcher/glossary.html#action-plan
.. _Action: http://docs.openstack.org/developer/watcher/glossary.html#action
.. _defaultplanner: https://github.com/openstack/watcher/blob/master/watcher/decision_engine/planner/default.py#L31
.. _decision-engine: http://docs.openstack.org/developer/watcher/glossary.html#watcher-decision-engine
.. _planner: http://docs.openstack.org/developer/watcher/glossary.html#watcher-planner


History
=======
None