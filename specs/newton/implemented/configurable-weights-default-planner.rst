..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

============================
Make default Planner generic
============================

https://blueprints.launchpad.net/watcher/+spec/configurable-weights-default-planner

Problem description
===================

Watcher provides a very modular architecture that currently allows anyone
to provide custom plugins:

  - Strategy
  - Planner
  - Action
  - Workflow Engine

In most of the above, their related implementation(s) are generic enough so
that they can work with any 3rd party plugin out of the box.
However, this is currently not the case for the `defaultplanner`_ which
defines a hardcoded set of priorities for each action type.

Hence, this means that adding a new `Action`_ via an action plugin and
reference it in a strategy would result in an error and the only solution
is to create a planner plugin that would adapt to this new action.

This is not very user friendly for the Watcher users because this means that
every time someone adds a new action, the source code of the
planner will have to be amended.

Use Cases
----------

As an administrator, I would like to be able to add a new `Action`_ without
having to amend the source code of the `defaultplanner`_.

Project Priority
----------------
* Medium

Proposed change
===============

This specification suggests modifying the DefaultPlanner class
``watcher/decision_engine/planner/default.py`` in order to avoid having to
implement a new planner whenever adding a new action plugin to
the mix.
A simple solution to this would be to leverage the `plugins-parameters`_
blueprint so that we can configure weights via the configuration file.

Currently in watcher, the weights are defined as below:
::

    priorities = {
            'nop': 0,
            'sleep': 1,
            'change_nova_service_state': 2,
            'migrate': 3
    }

We have to replace this by the code below :

::

    self.weights_dict = {'nop': 0,
                    'sleep': 1,
                    'change_nova_service_state': 2,
                    'migrate':3}
    def get_config_opts(self):
    return [
    cfg.DictOpt('weights', help="These weights are used to schedule
        the Actions.",
        default=self.weights_dict),
        ]

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
The user will have to modify the configurable file and reboot
the decision engine.

Performance Impact
------------------
None


Other deployer impact
---------------------
We are adding a new field in the configuration file. So, we should revisit the
puppet scripts.


Developer impact
----------------
None


Implementation
==============

Assignee(s)
-----------
Primary assignee:
Jinquan Ni <ni.jinquan@zte.com.cn>


Work Items
----------
* Replace the the storage of the weights in the default planner
* Update the documentation
* add unit tests


Dependencies
============
None

Testing
=======
* Unit tests will be added to validate these modifications.

Documentation Impact
====================

Update the `defaultplanner`_ documentations to now mention that the weights of
the planner can be specified in the configuration file.


References
==========

.. _defaultplanner: https://github.com/openstack/watcher/blob/master/watcher/decision_engine/planner/default.py#L38
.. _Action: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#action
.. _plugins-parameters: https://blueprints.launchpad.net/watcher/+spec/plugins-parameters
.. _base planner: https://github.com/openstack/watcher/blob/master/watcher/decision_engine/planner/base.py#L57

History
=======
None