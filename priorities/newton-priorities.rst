.. _newton-priorities:

=========================
Newton Project Priorities
=========================

List of priorities the Watcher drivers team is prioritizing in Newton.

+-----------------------------+-----------------------+
| Priority                    | Owner                 |
+=============================+=======================+
| `Cluster Object Wrapper`_   | `Vincent Francoise`_  |
+-----------------------------+-----------------------+
| `Persistent Audit Param`_   | `Prashanth Hari`_     |
+-----------------------------+-----------------------+
| `Watcher Policies`_         | `Charlotte Han`_      |
+-----------------------------+-----------------------+
| `Nova Policies`_            | `Jean-Emile Dartois`_ |
+-----------------------------+-----------------------+
| `Define Audit Scope`_       | `Alexander Chadin`_   |
+-----------------------------+-----------------------+
| `Scoring module`_           | `Tomasz Kaczynski`_   |
+-----------------------------+-----------------------+
| `Auto Triggering  Audit`_   | `Digambar`_           |
+-----------------------------+-----------------------+
| `Dynamic Action Desc`_      | `Charlotte Han`_      |
+-----------------------------+-----------------------+
| `Planner Storage Action`_   | `Jinquan Ni`_         |
+-----------------------------+-----------------------+
| `Notifications`_            | `Vincent Francoise`_  |
+-----------------------------+-----------------------+
| `Uniform Airflow Strategy`_ | `Junjie Huang`_       |
+-----------------------------+-----------------------+
| `Overload Strategy`_        | `Alexander Chadin`_   |
+-----------------------------+-----------------------+
| `Plugins parameters`_       | `Vincent Francoise`_  |
+-----------------------------+-----------------------+
| `Get Goal from Strategy`_   | `Vincent Francoise`_  |
+-----------------------------+-----------------------+
| `Efficacy Indicator`_       | `Vincent Francoise`_  |
+-----------------------------+-----------------------+
| `Default Planner Generic`_  | `Jinquan Ni`_         |
+-----------------------------+-----------------------+
| `Continuous Optimization`_  | `Alexander Chadin`_   |
+-----------------------------+-----------------------+


.. _Jean-Emile Dartois: https://launchpad.net/~jed56
.. _Vincent Francoise: https://launchpad.net/~vincent-francoise
.. _David Tardivel: https://launchpad.net/~david-tardivel
.. _Tomasz Kaczynski: https://launchpad.net/~tom-kaczynski
.. _Edwin Zhai: https://launchpad.net/~edwin-zhai
.. _Prashanth Hari: https://launchpad.net/~hvprash
.. _Charlotte Han: https://launchpad.net/~hanrong
.. _Alexander Chadin: https://launchpad.net/~joker946
.. _Kevin Mullery: https://launchpad.net/~kmullery
.. _Digambar: https://launchpad.net/~digambarpatil15
.. _Jinquan Ni: https://launchpad.net/~ni-jinquan
.. _Grigorios Katsaros: https://launchpad.net/~gregory-katsaros
.. _Junjie Huang: https://launchpad.net/~junjie.huang


Cluster Object Wrapper
----------------------

`Watcher Decision Engine`_  must provide a way to get cluster objects that can
be used directly within a `Strategy`_ . These objects will be refreshed
periodically.

Persistent Audit Param
----------------------

Watcher must ensure that the Audit parameters are persistent in Db.

Watcher Policies
----------------

Admin can use policies to allow or not users to invoke Watcher API
methods.

Nova Policies
-------------

Watcher `Strategy`_  must conform with the Nova polices.

Define Audit Scope
------------------

Watcher python clients must validate resources instead of Heat.

Scoring module
--------------

Watcher scoring module is a generic machine learning service. It will provide
for example predictions or classifications that can be used by the selected
`Strategy`_.

Auto Triggering  Audit
----------------------

Watcher will carry out 'Action Plans'_ automatically during Continous
Optimization.

Dynamic Action Desc
-------------------

'Watcher Decision Engine'_ must support Strategy with new customized
actions.

Planner Storage Action
----------------------

Watcher must store 'Action Plans'_ as a directed graph or Directed Acyclic
Graph in its database. The 'Watcher Applier'_ can then run each independent
Action in the graph in parallel when its dependencies have been satisfied.

Notifications
-------------

Watcher must be compliant with the new notification logic (versionned
payload and one topic).

Action Plan Conso
-----------------

Watcher must support a consolidation mechanism which combine all
'Action Plans'_ generated from an Audit into a single flow of Actions
to be executed.

Uniform Airflow Strategy
------------------------

This `Strategy`_ trigger migration of VMs based on the airflow of
servers. This strategy makes decisions to migrate VMs to make the
airflow uniform.

Overload Strategy
-----------------

This 'Strategy'_ chooses the pair VM:dest_host that minimizes the
standard deviation in a cluster best.

Plugins parameters
------------------

Watcher must give the possibility to the developer to add some
parameters depending on the configuration of OpenStack cluster
on the plugins

Get Goal from Strategy
----------------------

Achieved goal should be returned by each `Strategy`_

Efficacy Indicator
------------------

Provide efficacy indicators

Default Planner Generic
-----------------------

An admin needs to be able to add a new Action without having
to amend the source code of the default planner.

Continuous Optimization
-----------------------

Watcher Audit must support an active mode

.. _Strategy: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#strategy
.. _Watcher Decision Engine: https://factory.b-com.com/www/watcher/doc/watcher/architecture.html#watcher-decision-engine
.. _Action Plan: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#action-plan
.. _Watcher Applier: https://factory.b-com.com/www/watcher/doc/watcher/glossary.html#watcher-applier
