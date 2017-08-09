..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

====================================
Versioned notifications for services
====================================

https://blueprints.launchpad.net/watcher/+spec/service-versioned-notifications-api

Following the implementation of the `watcher-notifications-ovo blueprint`_,
Watcher now has all the necessary prerequisites in order to provide versioned
notifications throughout its codebase. This blueprint will focus on describing
the notifications to implement in Watcher concerning the Service object.

Problem description
===================

As of now, there is no way for any service (Watcher included) to know when a
service of Watcher has been failed or whether it has been reactivated
afterwards. This prevents any form of event-based reaction which may be useful
for 3rd party services or plugins.

Use Cases
---------

As an OpenStack developer, I want to be able to listen to notifications coming
from Watcher about service.

As an OpenStack developer, I want to know what the format of the service
notifications are.

As an OpenStack developer, I want to be notified whenever a service has been
failed or whether it has been reactivated afterwards.

Proposed change
===============

In order to implement the above use cases, one notification will
be needed:

- ``service.update`` whenever a service has been failed.
- ``service.update`` whenever a service has been reactivated afterwards.

Monitoring the status of the services will be performed through the background
job, which will be performed periodicaly (60 seconds) by the watcher-api
service.

Here below is suggestion of background job structure:

**scheduling**

.. code-block:: python

    class APISchedulingService(scheduling.BackgroundSchedulerService):

        def __init__(self, gconfig=None, **options):
            self.services_status = {}
            gconfig = None or {}
            super(APISchedulingService, self).__init__(gconfig, **options)

        def get_services_status(self, context):
            services = objects.service.Service.list(context)
            for service in services:
                result = self.get_service_status(context, service.name)
                if service.id not in self.services_status.keys():
                    self.services_status[service.id] = result
                    continue
                if self.services_status[service.id] != result:
                    self.services_status[service.id] = result
                    notifications.service.send_service_update(context, service,
                                                              state=result)

        def get_service_status(self, context, name):
            service = objects.Service.get(context, id)
            last_heartbeat = (service.last_seen_up or service.updated_at
                              or service.created_at)
            if isinstance(last_heartbeat, six.string_types):
                last_heartbeat = timeutils.parse_strtime(last_heartbeat)
            else:
                last_heartbeat = last_heartbeat.replace(tzinfo=None)
            elapsed = timeutils.delta_seconds(last_heartbeat, timeutils.utcnow())
            is_up = abs(elapsed) <= CONF.service_down_time
            if not is_up:
                LOG.warning(_LW('Seems service %(name)s on host %(host)s is down. '
                                'Last heartbeat was %(lhb)s.'
                                'Elapsed time is %(el)s'),
                            {'name': service.name,
                             'host': service.host,
                             'lhb': str(last_heartbeat), 'el': str(elapsed)})
                return objects.service.ServiceStatus.FAILED

            return objects.service.ServiceStatus.ACTIVE

        def start(self):
            """Start service."""
            context = watcher_context.make_context(is_admin=True)
            self.add_job(self.get_services_status, name='service_status',
                         trigger='interval', jobstore='default', args=[context],
                         next_run_time=datetime.datetime.now(), seconds=60)
            super(APISchedulingService, self).start()

        def stop(self):
            """Stop service."""
            self.shutdown()

        def wait(self):
            """Wait for service to complete."""

        def reset(self):
            """Reset service."""


Moreover, we will rely on `oslo.versionedobjects`_ to version the payloads of
service-related notifications.

Here below is suggestion of notification structure of the aforementioned
events:

**service.update**

.. code-block:: json

    {
      "payload": {
        "watcher_object.name": "ServiceUpdatePayload",
        "watcher_object.namespace": "watcher",
        "watcher_object.data": {
          "status_update": {
            "watcher_object.name": "ServiceStatusUpdatePayload",
            "watcher_object.namespace": "watcher",
            "watcher_object.data": {
              "old_state" :"ACTIVE",
              "state": "FAILED"
            },
            "watcher_object.version": "1.0"
          },
          "last_seen_up": "2016-09-22T08:32:06Z",
          "name": "watcher-service",
          "sevice_host": "controller"
        },
        "watcher_object.version": "1.0"
      },
      "event_type": "service.update",
      "priority": "INFO",
        "message_id": "3984dc2b-8aef-462b-a220-8ae04237a56e",
        "timestamp": "2016-10-18 09:52:05.219414",
        "publisher_id": "infra-optim:node0"
    }


Alternatives
------------

Instead of using versioned objects, we can define the payload of our service
notifications without any support for versioning.

Data model impact
-----------------

New versioned objects will be created although none of them are to be persisted
as they will be used to structure the content of the notifications.

Here are some of the payloads to be declared:

.. code-block:: python

    @base.WatcherObjectRegistry.register_notification
    class ServicePayload(notificationbase.NotificationPayloadBase):

        VERSION = '1.0'
        fields = {
            'sevice_host': wfields.StringField(),
            'name': wfields.StringField(),
            'last_seen_up': wfields.DateTimeField(),
        }


    @base.WatcherObjectRegistry.register_notification
    class ServiceStatusUpdatePayload(notificationbase.NotificationPayloadBase):

       VERSION = '1.0'
        fields = {
            'old_state': wfields.StringField(nullable=True)
            'state': wfields.StringField(nullable=True)
        }


    @base.WatcherObjectRegistry.register_notification
    class ServiceUpdatePayload(ServicePayload):

        VERSION = '1.0'
        fields = {
            'status_update': wfields.ObjectField('ServiceStatusUpdatePayload'),
        }


REST API impact
---------------

None.

Security impact
---------------

None.

Notifications impact
--------------------

This blueprint will implement the following notifications:

- ``service.update``

Other end user impact
---------------------

None.

Performance Impact
------------------

When enabled, code to send the notification will be called each time an event
occurs that triggers a notification. This shouldn’t be much of a problem for
Watcher itself, but the load on whatever message bus is used should be
considered.

Other deployer impact
---------------------

In order for the notifications to be emitted, the deployer will have to
configure the notification topics using `oslo.messaging`_. Other configuration
options exposed via `oslo.messaging`_ may also be tuned.

Developer impact
----------------

Developers should add here proper versioning guidelines and use the
notification base classes when creating/updating notifications.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  Vladimir Ostroverkhov <ostroverkhov@servionica.ru>

Work Items
----------

- Implement ``service.update``

Dependencies
============

- `watcher-versioned-objects`_
- `watcher-notifications-ovo`_

Testing
=======

These notifications will have to be tested mainly via unit testing.

Documentation Impact
====================

A notification sample should be provided and made dynamically available in the
online documentation.

The sequence diagrams in the `Watcher architecture`_.

References
==========

None.

.. _watcher-notifications-ovo blueprint: https://blueprints.launchpad.net/watcher/+spec/watcher-notifications-ovo
.. _watcher-versioned-objects: https://blueprints.launchpad.net/watcher/+spec/watcher-versioned-objects
.. _watcher-notifications-ovo: https://blueprints.launchpad.net/watcher/+spec/watcher-notifications-ovo
.. _oslo.versionedobjects: http://docs.openstack.org/developer/oslo.versionedobjects/
.. _configure the notification topics: http://docs.openstack.org/developer/oslo.messaging/opts.html#oslo-messaging-notifications
.. _oslo.messaging: http://docs.openstack.org/developer/oslo.messaging/
.. _Watcher architecture: http://docs.openstack.org/developer/watcher/architecture.html#watcher-applier
