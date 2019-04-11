..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

=====================
File based Metric Map
=====================

https://blueprints.launchpad.net/watcher/+spec/file-base-metric-map


Problem description
===================

Watcher supports loading metrics for various datasources however the
metrics it uses to retrieve data are stored directly in the codebase and do
not allow flexibly changing these names. And customers/admin/user are
forced to use a naming scheme expected by watcher. Also it hinders Watcher
ease of integration if a particular metric is already in use under a
different name.

Use Cases
----------

As a Watcher user, I want that Watcher should be allow choosing a metric
name as defined in current datasource being used.

As a Watcher user, I want that Watcher to be able to change the metrics
names as required.


Proposed change
===============

An option of metric_map_path should be added to watcher_decision_engine
section of watcher.conf

Allow Watcher to load a yaml file which contains a map of internal metric
names (as expected by Watcher) to real metrics names in use in the
datasources.

The file is optional and needs to contain only those metrics names that
the user expects to override.

A method in DataSourceManager class could be called in its __init__ method.

For example:

.. code-block:: ini


    [watcher_decision_engine]
    # ...
    metric_map_path = /etc/watcher/metricmap.yaml
    # ...



.. code-block:: yaml


   monasca:
     - instance_cpu_usage: VM_CPU
   gnocchi:
     - instance_cpu_usage: cpu_vm_util



.. code-block:: python


    class DataSourceManager(object):
        def __init__(self):
            #...
            # 1. Initial loading is necessary to initialize the correct defaults
            self.metric_map = {
                mon.MonascaHelper.NAME: mon.MonascaHelper.METRIC_MAP,
                gnoc.GnocchiHelper.NAME: gnoc.GnocchiHelper.METRIC_MAP,
                ceil.CeilometerHelper.NAME: ceil.CeilometerHelper.METRIC_MAP
            }
            new_metric_map = self.metrics_from_file():
            # 2. overide the loaded default by using yaml
            # update self.metric_map recursively using new_metric_map

        def get_backend(self, metrics):
            #...
            if not no_metric:
                ds = getattr(self, datasource)
                # 3. Pass the re-loaded metric map to the datasource
                ds.METRIP_MAP.update(self.metric_map[ds.NAME])
                return ds

        def metrics_from_file(self):
            """Load metrics from the config.metric_map_path"""
            if not os.path.exists(config.metric_map_path or ''):
                return {}
            with open(config.metric_map_path, 'r') as f:
                try:
                    return yaml.safe_load(f.readall())
                except yaml.YAMLERROR as e:
                    log.info('Could not load %(s): %s' % (
                        config.metric_map_path, str(e)))
                    return {}



Comments about implementation:

Step 1:
This loading can be avoided if the defaults are to be never stored in python
files. But that is outside the scope of this spec as that will make the
yaml file mandatory.

Step 2:
self.metric_map is a nested dict so will need special handling for recursive
update to datasources.

Step 3:
This loading can be moved to the individual `getter`'s we have already defined
an "API for metric_map communication" by making `METRIC_MAP` dictionary a class
variable.


Alternatives
------------

Instead of updating the METRIC_MAP directly in the datasource, the
map could be passed to each datasoruce classes, but that spills the
change over to other classes and files and also this delegation of
responsibility is not contributing to any reasonable advantage.

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

A configuration option should be added to the 'watcher_decision_engine'
section, however this is not a requirement, but rather a good-to-have
as this can lead to potential name conflict.

A user/admin can configure a new parameter in the config, but this is a
non-binding config.

Performance Impact
------------------

None

Other deployer impact
---------------------

No impact as the file creation/existence is optional

Developer impact
----------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  <sumitjami>

Work Items
----------

* Add a configuration option 'metric_map_file'

* Add new method to DataSourceManager class

* Load the file and update the metric_map variable

* update the METRIC_MAP dict of datasource in get_backend method



Dependencies
============

None


Testing
=======

* Add unit test for file existance error check.

* Add unit test for checking if file contents are loaded correctly.


Documentation Impact
====================

Update Watcher developer documents.


References
==========

None


History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - Train
     - Introduced

