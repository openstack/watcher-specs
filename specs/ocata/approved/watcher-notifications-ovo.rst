..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

========================
Notifications in Watcher
========================

https://blueprints.launchpad.net/watcher/+spec/watcher-notifications-ovo

Provide a notification mechanism into Watcher that supports versioning.

Whenever a Watcher object (i.e. Goal_, Strategy_, AuditTemplate_, Audit_,
ActionPlan_, Action_, `EfficacyIndicator`_ or `ScoringEngine`_) is created,
updated or deleted, a versioned notification should, if it's relevant, be
automatically sent to notify in order to allow an event-driven style of
architecture within Watcher. Moreover, it will also give other services and/or
3rd party softwares (e.g. monitoring solutions or rules engines) the ability
to react to such events.

This blueprint is heavily inspired on similar blueprints made on other
projects:

- Nova: `versioned-notification-api blueprint`_
- Ironic: `notifications blueprint`_

Problem description
===================

As of now, Watcher does not emit any notification whenever performing some
actions such as an update of an object. These information should be notified
so that Watcher services can inter-operate on an event-based basis instead of
having to rely on data polling. Moreover, these notifications may find
themselves useful to other OpenStack services which can also make use of them,
especially `Congress`_, `Vitrage`_, `Monasca`_ or `Aodh`_.

Therefore, the purpose of this blueprint is to give Watcher the ability to send
versioned notifications.

Use Cases
----------

As an OpenStack developer, I want to be able to listen to notifications coming
from Watcher. I also want to know what is the format of the notifications.

As an OpenStack developer, I want to be able to detect and follow up the
changes in the notification format later on.

As an OpenStack operator, I want to be able to disable notifications in
Watcher.

As an OpenStack operator, I want to be able to define the topic(s) to which
Watcher will send its notifications.

Project Priority
-----------------

N/A

Proposed change
===============

Based on the `oslo.versionedobjects`_ library, the objective is to create
versioned objects that will later on be serialized and sent as payload for the
notifications, each one of these objects will hence be able to hold a version
number that will facilitate retro-compatibility whenever adding new fields.

The basic structure for all notifications will be the same as the one that is
used in Nova for the `versioned-notification-api blueprint`_, i.e.:

.. code-block:: json

    {
        "priority": "INFO",
        "event_type": "infra-optim.audit.update",
        "timestamp": "2016-10-07 09:31:10.895274",
        "publisher_id": "watcher-api",
        "message_id": "a13cb7a6-8fae-4e20-8fc8-1c4e851fa6f5",
        "payload": {
          // [...]
        }
    }

In order to send the versioned notification, we will use the `oslo.messaging`_
library which is a standard OpenStack library. Already used within Watcher to
listen to notifications emitted by other projects (e.g. Nova),
`oslo.messaging`_ will help us declare a `notifier`_ that allows us to
`configure the topics`_ all notifications will be sent to.

Alternatives
------------

Instead of using `oslo.versionedobjects`_, we can define the payload of our
notifications without any support for versioning.

Data model impact
-----------------

The following base objects will be defined:

.. code-block:: python

    class NotificationPriorityType(Enum):
        AUDIT = 'audit'
        CRITICAL = 'critical'
        DEBUG = 'debug'
        INFO = 'info'
        ERROR = 'error'
        SAMPLE = 'sample'
        WARN = 'warn'

        ALL = (AUDIT, CRITICAL, DEBUG, INFO, ERROR, SAMPLE, WARN)


    class NotificationPhase(BaseWatcherEnum):
        START = 'start'
        END = 'end'
        ERROR = 'error'

        ALL = (START, END, ERROR)


    class NotificationAction(BaseWatcherEnum):
        CREATE = 'create'
        UPDATE = 'update'
        EXCEPTION = 'exception'
        DELETE = 'delete'

        ALL = (CREATE, UPDATE, EXCEPTION, DELETE)


    class NotificationPriorityField(BaseEnumField):
        AUTO_TYPE = NotificationPriority()


    class NotificationPhaseField(BaseEnumField):
        AUTO_TYPE = NotificationPhase()


    class NotificationActionField(BaseEnumField):
        AUTO_TYPE = NotificationAction()


    @base.WatcherObjectRegistry.register_notification
    class EventType(NotificationObject):
        VERSION = '1.0'

        fields = {
            'object': fields.StringField(nullable=False),
            'action': fields.NotificationActionField(nullable=False),
            'phase': fields.NotificationPhaseField(nullable=True),
        }


    @base.WatcherObjectRegistry.register_if(False)
    class NotificationBase(NotificationObject):
        VERSION = '1.0'

        fields = {
            'priority': fields.NotificationPriorityField(),
            'event_type': fields.ObjectField('EventType'),
            'publisher': fields.ObjectField('NotificationPublisher'),
        }

        def emit(self, context):
            """Send the notification."""


REST API impact
---------------

None.

Security impact
---------------

None.

Notifications impact
--------------------

None, although this blueprint introduces the required building blocks necessary
to implement any notification.

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

The following configuration option will be added:

- A ``notification_level`` string parameter will be added to indicate the
  minimum priority level for which notifications will be sent. Available
  options will be ``DEBUG``, ``INFO``, ``WARN``, ``ERROR``, or ``None`` to
  disable notifications. ``INFO`` will be the default.

Note that some already existing configuration options coming from
`oslo.messaging`_ that were auto-generated into the ``watcher.conf.sample``
configuration sample will now be taken into account. For more information,
refer to the `oslo.messaging configuration options`_ documentation.

Developer impact
----------------

Developers should adhere to proper versioning guidelines and use the
notification base classes when creating new notifications.

Implementation
==============

Assignee(s)
-----------

Primary assignee:
    vincent-francoise

Work Items
----------

- Implement all base objects presented in `Data model impact`_
- Add new sphinx directive that will help documenting the Watcher notifications
  by giving a notification sample.

Dependencies
============

watcher-versioned-objects_

Testing
=======

Unit tests should be added to ascertain the good behavior of the newly
implemented notifications.

Documentation Impact
====================

Create a new documentation section in Watcher that will automatically expose
all the implemented notifications with a complete notification sample that
can be used as a reference by the developers trying to consume them.

References
==========

None.

.. _ScoringEngine: http://docs.openstack.org/developer/watcher/glossary.html#scoring-engine
.. _Goal: http://docs.openstack.org/developer/watcher/glossary.html#goal
.. _Strategy: http://docs.openstack.org/developer/watcher/glossary.html#strategy
.. _AuditTemplate: http://docs.openstack.org/developer/watcher/glossary.html#audit-template
.. _Audit: http://docs.openstack.org/developer/watcher/glossary.html#audit
.. _ActionPlan: http://docs.openstack.org/developer/watcher/glossary.html#action-plan
.. _Action: http://docs.openstack.org/developer/watcher/glossary.html#action
.. _EfficacyIndicator: http://docs.openstack.org/developer/watcher/glossary.html#efficacy-indicator
.. _notifications blueprint: https://specs.openstack.org/openstack/nova-specs/specs/mitaka/implemented/versioned-notification-api.html
.. _oslo.versionedobjects: http://docs.openstack.org/developer/oslo.versionedobjects/
.. _oslo.messaging: http://docs.openstack.org/developer/oslo.messaging/
.. _versioned-notification-api blueprint: https://specs.openstack.org/openstack/nova-specs/specs/mitaka/implemented/versioned-notification-api.html
.. _watcher-versioned-objects: https://blueprints.launchpad.net/watcher/+spec/watcher-versioned-objects
.. _notifier: http://docs.openstack.org/developer/oslo.messaging/notifier.html
.. _configure the topics: http://docs.openstack.org/developer/oslo.messaging/opts.html#oslo-messaging-notifications
.. _oslo.messaging configuration options: http://docs.openstack.org/developer/oslo.messaging/opts.html
.. _Congress: http://docs.openstack.org/developer/congress/
.. _Vitrage: https://wiki.openstack.org/wiki/Vitrage
.. _Monasca: https://github.com/openstack/monasca-api/blob/master/docs/monasca-api-spec.md
.. _Aodh: http://docs.openstack.org/developer/aodh/
