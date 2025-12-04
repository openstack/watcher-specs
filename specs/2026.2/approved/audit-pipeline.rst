..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==============
Audit Pipeline
==============

https://blueprints.launchpad.net/watcher/+spec/audit-pipeline

This specification proposes the introduction of ``Audit Pipeline``, a new
feature that allows administrators to define an ordered set of strategy stages
that are evaluated against a projected cluster state. The first implementation
will support ONESHOT pipelines using cascade planning and will produce one
optimized action plan.


Problem description
===================

Currently, Watcher supports three audit types: ONESHOT, CONTINUOUS, and EVENT.
Each audit executes a single strategy targeting a single goal. However, complex
optimization scenarios often require multiple strategies to be executed in
sequence, where each subsequent strategy operates on the expected state of the
cluster after the previous strategy's proposed actions are applied.

Cloud operators may need to combine optimization strategies to achieve their
operational goals. For example, for maintenance purposes, an operator may need
to migrate workloads from specific hosts and then rebalance workloads. To save
energy, an operator may need to consolidate workloads, power off unused nodes,
and still keep enough capacity available for future workloads.

Use Cases
---------

As a cloud operator, I need to perform scheduled maintenance on specific hosts
without affecting the running workloads. As a result, I need to migrate those
workloads without pessimizing the workload distribution by using workload
balancing strategies after the maintenance evacuation. This requires
coordinating multiple optimization strategies in sequence to achieve a
composite goal. Each strategy needs to operate on a scoped and updated state
of the cluster based on the future state created by the previous strategy.

As a cloud operator, I want to save energy by consolidating workloads while
also ensuring enough nodes remain online to support new workloads. To achieve
this, the workloads first need to be consolidated using server or VM
consolidation goals. Then compute nodes can be powered off based on the Saving
Energy strategy.

Proposed change
===============

This spec proposes the introduction of an ``Audit Pipeline`` API resource,
which models the composition of multiple strategies executed in sequence.
Each stage is evaluated based on the projected outcome of the prior stages.
A mutable cluster data model, and optionally a transparent metric data cache,
will be passed to each stage to allow simulation of the future state.

This functionality will be implemented through a new ``Audit Pipeline``
resource with dedicated APIs and an extension to the existing Audit Template
resource to support strategy default parameters. The Audit Template extension
will be introduced in a dedicated microversion before the pipeline APIs.

The initial implementation is intentionally scoped to ONESHOT audit pipelines
using cascade execution. CONTINUOUS and EVENT audit pipelines, composite
execution, and recurring pipeline scheduling are out of scope for the first
implementation and may be proposed in a future spec.

Audit Template Extension
------------------------

The existing Audit Template resource will be extended to support input
parameters for the selected strategy. This allows operators to define reusable
templates with pre-configured strategy parameters that can be used as stages in
a pipeline or as defaults for normal audits.

A new optional ``default_parameters`` field will be added to Audit Template.
This field is a dictionary of strategy parameters. The API schema will treat
it as an opaque dictionary, because goals and strategies are pluggable.
After schema validation, the API will validate the dictionary against the
selected strategy's parameter schema. Invalid parameters will cause a
``400 Bad Request`` response.

When creating a normal Audit from an Audit Template, explicit Audit
``parameters`` override values from the template ``default_parameters``. This
preserves the template as a reusable default while still allowing per-audit
customization.

The ``default_parameters`` field can be updated via the existing PATCH API.
If an Audit Template has a non-null ``default_parameters`` and a PATCH request
updates ``goal`` or ``strategy`` without also providing an updated
``default_parameters``, the API will return ``409 Conflict``. This prevents
stale parameters from silently becoming invalid after a goal or strategy
change.

This extension will be introduced in a dedicated API microversion before the
Audit Pipeline APIs, so operators can adopt default parameters independently of
the pipeline feature.

Audit Pipeline Resource
-----------------------

A new ``Audit Pipeline`` resource will be introduced. The first implementation
will support ONESHOT pipelines only. A pipeline starts in ``PENDING`` state and
is triggered by the decision engine in the same general way as an ONESHOT
Audit. The result of a successful pipeline planning run is one Action Plan.

The Audit Pipeline state machine will reuse the existing Audit states. The
initial ONESHOT implementation will expose this reduced transition set:

* PENDING -> ONGOING, CANCELLED
* ONGOING -> SUCCEEDED, FAILED, CANCELLED
* SUCCEEDED -> DELETED
* FAILED -> DELETED
* CANCELLED -> DELETED

All pipelines start in ``PENDING`` state. ``DELETED`` is the final soft-delete
state. ``SUSPENDED`` remains an Audit state only, and suspending and resuming
pipelines is out of scope until recurring CONTINUOUS or EVENT pipelines are
specified.

An Audit Pipeline is similar to an Audit, with these differences:

* It accepts a list of stage objects. Each stage references one Audit Template.
  The goal, strategy, scope, and parameters used by the stage are snapshotted
  from that Audit Template when the pipeline is created.
* Unlike Audit, Audit Pipeline will not accept strategy ``input_parameters``
  directly. Strategy parameters must be defined as ``default_parameters`` in
  the Audit Template for each stage.
* It does not directly accept a goal or strategy. Those are defined by the
  referenced Audit Templates.
* It supports only ``cascade`` execution mode in the initial implementation.
* It supports a minimum of two stages and a hard-coded maximum of ten stages.
  This limit is not configurable in this first implementation.

The stage object accepted by the create API will have this shape::

    {
        "name": "maintenance",
        "description": "Migrate instances away from compute-1",
        "audit_template": "zone-migration-template"
    }

``name`` and ``description`` are optional user-facing metadata. The
``audit_template`` field may be the UUID or name of an existing Audit Template.
The response representation will also include a stable stage ``uuid``.
Stage-specific ``input_parameters`` are not part of the initial API. The stage
object leaves room to add them in a later microversion if a future use case
requires per-pipeline parameter overrides.

Cascade Execution Mode
----------------------

Cascade execution runs each stage sequentially. Before each stage, the
Pipeline Handler performs two pre-stage steps: it applies the previous stage's
solution to a mutable copy of the cluster data model, and it updates the metric
cache with projected values derived from that solution. This ensures each
strategy receives an up-to-date context reflecting the expected cluster state
after prior stages.

Each stage strategy reads the injected context as if it were the current
cluster state. Strategies remain pipeline-agnostic: they should not need to
know whether they are being evaluated as part of a normal Audit or an Audit
Pipeline. The pipeline implementation is responsible for injecting the scoped
CDM used by each stage and for pre-populating the metric cache with projected
values before each stage executes.

Mutable Cluster Data Model
--------------------------

The Pipeline Handler will manage CDM mutation between stages. In cascade mode,
before each stage, a copy of the CDM is updated based on the previous stage's
solution. The lifecycle of the mutable CDM is tied to a single Audit Pipeline
execution. It is created at the start of the pipeline workflow and discarded
after the final Action Plan is generated. The CDM is not persisted and is not
reused by any other pipeline execution.

The simulation layer must preserve constraints introduced by earlier stages.
For example, if a host-maintenance stage requires instances to leave a
maintenance host, later stages must not move those instances back to that host
or eliminate the required migration. The simulation layer will mark such hosts
or actions as constrained so that later stages and the Pipeline Planner can
distinguish required moves from collapsible optimization moves.

Metric Data Cache
-----------------

The metric data cache is an in-memory data structure scoped to one Audit
Pipeline execution. It is not stored in the database and is discarded after
the final Action Plan is generated or the pipeline planning run fails.

The cache will be implemented transparently inside the datasource layer without
requiring any changes to existing strategies. The public
``statistic_aggregation`` method, currently implemented independently by each
datasource, will be refactored:
each datasource will rename its current implementation to a private method, and
``statistic_aggregation`` will become a base-class method that implements the
caching logic and delegates to that private method on a cache miss. When a
strategy calls ``statistic_aggregation``, the base implementation will first
check the per-execution cache for a matching result. If a cached or projected
value is present it is returned immediately; otherwise the private datasource
method is called and the result is stored in the cache before being returned.

This approach keeps the strategy interface unchanged and makes caching
transparent to both existing and future strategies. The same mechanism applies
to normal Audits, where the cache may act as a lightweight per-audit cache or
be skipped entirely with a no-op implementation. Projected metric values can be
injected into the cache by the Pipeline Handler before each stage, so that
subsequent strategy queries reflect the expected cluster state after prior
stages.

Strategy Execution Context
--------------------------

``BaseStrategy`` will be extended to allow the Pipeline Handler to inject
pre-populated cluster data models before executing each stage. Setter methods
will be added for ``compute_model``, ``storage_model``, and
``baremetal_model`` so the Pipeline Handler can supply the projected CDM
directly. When a setter has been used, the corresponding property returns the
injected model instead of invoking the collector. If no model has been
injected, the existing lazy collector behavior is preserved.

This makes pipeline support transparent to strategies that use the documented
``BaseStrategy`` accessors. Requiring a concrete strategy to opt in to Audit
Pipeline execution is not acceptable. If an existing strategy bypasses those
accessors and talks directly to a collector or service client, that is a
compatibility gap to fix in the framework or strategy implementation, not a
separate pipeline-compatibility mode.

Pipeline Planner
----------------

The Pipeline Planner will combine all stage solutions into the final Action
Plan. It is responsible for:

* merging the solutions from all stages into a single one, tracking which
  stage each action originated from;
* preserving stage origin metadata for actions and efficacy indicators;
* detecting conflicts between stage solutions;
* collapsing only actions that are explicitly safe to collapse;
* removing circular migrations (e.g., A->B followed by B->A, both eliminated);
* ordering actions and preserving dependencies in the final Action Plan.

Migration chain optimization must be conservative. For example, an optimization
sequence such as A -> B followed by B -> C may be collapsed to A -> C only when
no earlier stage constraint is violated. A B -> A move must not be generated or
kept if A was removed from the valid candidate set by a host maintenance stage.
If the planner cannot prove that a collapse is safe, it must keep the required
actions or fail planning with a clear status message.

RPC and Service Routing
-----------------------

Starting a pipeline requires RPC coordination with the decision engine. The
API service will add a decision-engine RPC cast method that mirrors the
existing ``trigger_audit`` asynchronous pattern while passing the pipeline
UUID instead of an Audit UUID::

    def trigger_audit_pipeline(self, context, audit_pipeline_uuid):
        self.conductor_client.cast(
            context, 'trigger_audit_pipeline',
            audit_pipeline_uuid=audit_pipeline_uuid)

Because the method is a cast, the corresponding REST action endpoint returns
``202 Accepted`` when the request is accepted for asynchronous processing.

The decision engine will add an Audit Pipeline endpoint that loads the pipeline
object, records the worker hostname for the ONGOING run, and executes the
Pipeline Handler in the decision-engine worker pool.

Strategy Scopes
---------------

Each Audit Template may define a scope. In cascade mode, stage scopes are
snapshotted into the pipeline stage records when the pipeline is created. The
first stage establishes the initial scoped CDM. Later stages are evaluated
against the projected CDM after previous stage solutions have been applied. The
Pipeline Handler may further restrict later-stage candidate sets based on
constraints introduced by earlier stages.

Efficacy Indicators
-------------------

Each stage strategy produces efficacy indicators as part of its solution.
The Pipeline Planner will collect all indicators from all stages and merge
them into a single list when creating the final Action Plan. Indicators with
the same name from different stages will be concatenated rather than
deduplicated, so that no information about individual stage contributions is
lost. The merged list is stored in the Action Plan's ``global_efficacy``
field using the existing data model, without requiring any new database
columns or per-stage storage.

Future Work
-----------

The initial implementation is limited to ONESHOT cascade pipelines. The
following items describe the expected future evolution of the feature, but are
out of scope for this spec:

* Composite execution mode: group independent stages that do not require CDM or
  metric simulation between them. This would allow operators to schedule a set
  of independent audits as one unit, for example workload stabilization scoped
  separately to multiple availability zones.
* CONTINUOUS and EVENT pipeline triggers: extend pipelines beyond ONESHOT
  execution, including interval handling, webhook or event triggering,
  ``next_run_time`` management, and interaction with the existing audit
  scheduler.
* Stage-specific input parameters: allow per-pipeline overrides for a stage
  without editing the source Audit Template.
* Additional action simulation handlers: expand the set of actions whose
  projected effects can be represented in the mutable CDM and metric cache.

Architecture Overview
---------------------

The following diagram shows the sequence of processes that happen when an
Audit Pipeline using cascade execution is triggered::

    +-------------------------------------------------------------------+
    |                         PIPELINE HANDLER                          |
    |                   Orchestrator and Simulator                      |
    +-------------------------------------------------------------------+
    |                                                                   |
    |  1. Set up execution context                                      |
    |     - Fetch initial scoped CDM                                    |
    |     - Initialize transparent metric cache                         |
    |                                                                   |
    |  2. Cascade simulation loop, stage 1 to N                         |
    |     +---------------------------------------------------------+   |
    |     | a. Project current world (pre-stage steps)              |   |
    |     |    - Apply previous solution to CDM                     |   |
    |     |    - Update projected metric values in cache            |   |
    |     |    - Stage 1 applies null updates to both               |   |
    |     |                                                         |   |
    |     | b. Execute isolated strategy                            |   |
    |     |    +-----------------------------------------------+    |   |
    |     |    |           WATCHER STRATEGY                    |    |   |
    |     |    | - Reads injected CDM as current state         |    |   |
    |     |    | - Calls statistic_aggregation on datasource   |    |   |
    |     |    +----------------------+------------------------+    |   |
    |     |                           |                             |   |
    |     |                           v                             |   |
    |     |    +-----------------------------------------------+    |   |
    |     |    |    DATASOURCE (statistic_aggregation)         |    |   |
    |     |    | - Hit: return cached or projected metric      |    |   |
    |     |    | - Miss: call private impl and store result    |    |   |
    |     |    +-----------------------------------------------+    |   |
    |     |                                                         |   |
    |     | c. Capture solution                                     |   |
    |     |    - Store solution for final planning                  |   |
    |     |    - Use solution to drive next stage context           |   |
    |     +---------------------------------------------------------+   |
    +--------------------------------+----------------------------------+
                                     |
                                     v
    +-------------------------------------------------------------------+
    |                         PIPELINE PLANNER                          |
    |                                                                   |
    |  - Merge stage solutions                                          |
    |  - Preserve constraints and dependencies                          |
    |  - Optimize only safe action chains                               |
    |  - Generate the final Action Plan                                 |
    +--------------------------------+----------------------------------+
                                     |
                                     v
    +-------------------------------------------------------------------+
    |                         FINAL ACTION PLAN                         |
    |                 Ready for persistence and execution               |
    +-------------------------------------------------------------------+

Alternatives
------------

* An external tool could orchestrate the execution of multiple Audits. This is
  an alternative to the current manual process of executing strategies one by
  one. However, this approach still requires each Action Plan to be executed
  before computing the next strategy solution, so later planning cannot use a
  projected future state before execution.
* Watcher could be extended to support Audit creation as a final Action from a
  given Action Plan. This still requires a first Action Plan to execute before
  calculating the next one, and it does not provide a single optimized plan.
* For each use case, a new strategy could implement the combination of the
  required strategy algorithms. This duplicates existing strategy logic and
  does not provide a reusable composition mechanism.

Data model impact
-----------------

``Audit Template Extension``

Add a new optional column to the ``AuditTemplate`` model, following the same
pattern as ``Audit.parameters``::

    class AuditTemplate(Base):
        ...
        default_parameters = Column(Text, nullable=True)

The column stores default strategy parameters as a JSON-encoded text value.
The ``AuditTemplate`` object version will be bumped to include a new
``default_parameters`` field.

``New Audit Pipeline Resource``

Create a new ``AuditPipeline`` database model::

    class AuditPipeline(Base):
        """Represents an audit pipeline for multi-strategy execution."""

        __tablename__ = 'audit_pipelines'
        __table_args__ = (
            UniqueConstraint('uuid', name='uniq_audit_pipelines0uuid'),
            UniqueConstraint('name', 'deleted',
                             name='uniq_audit_pipelines0name'),
            table_args()
        )
        id = Column(Integer, primary_key=True, autoincrement=True)
        uuid = Column(String(36))
        name = Column(String(63), nullable=True)
        execution_mode = Column(String(20), nullable=False)
        state = Column(String(20), nullable=True)
        audit_type = Column(String(20))
        auto_trigger = Column(Boolean, nullable=False, default=True)
        hostname = Column(String(255), nullable=True)
        status_message = Column(String(255), nullable=True)

The model intentionally omits ``interval``, ``next_run_time``,
``start_time``, and ``end_time`` because recurring CONTINUOUS and EVENT
pipelines are out of scope for the initial implementation.

``Audit Pipeline Stage Resource``

Create a new ``AuditPipelineStage`` model to store the ordered stage list
as a normalised table::

    class AuditPipelineStage(Base):
        """Represents one stage in an audit pipeline."""

        __tablename__ = 'audit_pipeline_stages'
        __table_args__ = (
            UniqueConstraint('uuid', name='uniq_audit_pipeline_stages0uuid'),
            table_args()
        )
        id = Column(Integer, primary_key=True, autoincrement=True)
        uuid = Column(String(36))
        audit_pipeline_id = Column(
            Integer, ForeignKey('audit_pipelines.id'), nullable=False)
        position = Column(Integer, nullable=False)
        name = Column(String(63), nullable=True)
        description = Column(String(255), nullable=True)
        source_audit_template_id = Column(
            Integer, ForeignKey('audit_templates.id'), nullable=True)
        goal_id = Column(Integer, ForeignKey('goals.id'), nullable=False)
        strategy_id = Column(
            Integer, ForeignKey('strategies.id'), nullable=True)
        scope = Column(Text, nullable=True)
        parameters = Column(Text, nullable=True)

        audit_pipeline = orm.relationship(
            AuditPipeline, foreign_keys=audit_pipeline_id, lazy=None)
        goal = orm.relationship(Goal, foreign_keys=goal_id, lazy=None)
        strategy = orm.relationship(
            Strategy, foreign_keys=strategy_id, lazy=None)

The stage stores a snapshot of the referenced Audit Template's goal, strategy,
scope, and default parameters at pipeline creation time. Later edits or deletes
of the Audit Template do not change existing pipelines. The
``source_audit_template_id`` is retained only for traceability and may become
null if the template is deleted.

``Action Plan Changes``

Update the existing ``ActionPlan`` model to make ``audit_id`` and
``strategy_id`` nullable and add a foreign key to ``AuditPipeline``::

    class ActionPlan(Base):
        ...
        audit_id = Column(Integer, ForeignKey('audits.id'), nullable=True)
        strategy_id = Column(
            Integer, ForeignKey('strategies.id'), nullable=True)
        audit_pipeline_id = Column(
            Integer, ForeignKey('audit_pipelines.id'), nullable=True)

        audit_pipeline = orm.relationship(
            AuditPipeline, foreign_keys=audit_pipeline_id, lazy=None)

For normal Audit-created Action Plans, ``audit_id`` and ``strategy_id`` remain
populated. This feature does not deprecate ``strategy_id`` for normal Audits.

The ``ActionPlan`` object version will be bumped. The existing ``audit_id``
and ``strategy_id`` object fields will become nullable, and the following
column will be added::

    audit_pipeline_id = Column(
        Integer, ForeignKey('audit_pipelines.id'), nullable=True)

The existing ``Action`` model will also gain a nullable
``audit_pipeline_stage_id`` foreign key::

    class Action(Base):
        ...
        audit_pipeline_stage_id = Column(
            Integer, ForeignKey('audit_pipeline_stages.id'), nullable=True)

        audit_pipeline_stage = orm.relationship(
            AuditPipelineStage, foreign_keys=audit_pipeline_stage_id,
            lazy=None)

Pipeline-created actions will set ``audit_pipeline_stage_id`` to the stage
that produced the action. Normal Audit-created actions will leave it null.
The ``Action`` object version will be bumped to include this new column.

The object save path will enforce that exactly one of ``audit_id`` or
``audit_pipeline_id`` is set. This invariant will be enforced in the object
and database API layers.

When retrieving Action Plans in an older microversion, pipeline-created Action
Plans will not be included because their ``audit_id`` and ``strategy_id``
fields cannot be represented by the older response contract. In the new
microversion, Action Plan responses will include ``audit_pipeline_uuid`` for
pipeline-created Action Plans, with ``audit_uuid`` and ``strategy_uuid`` null
or omitted.

The database migration will add the nullable columns and new tables in a
backwards-compatible way. No data migration is required for existing Audits,
Audit Templates, Action Plans, or Actions.

REST API impact
---------------

``Audit Template - Add default_parameters``

Update the Audit Template API to support the new ``default_parameters`` field:

* Method: POST, PATCH
* URL: ``/v1/audit_templates``, ``/v1/audit_templates/{uuid}``
* Error responses: 400 Bad Request, 404 Not Found, 409 Conflict

The ``default_parameters`` value is schema-validated only as an object because
goal and strategy plugins are dynamic. After schema validation, the API
validates those parameters against the selected strategy and returns
``400 Bad Request`` when they are not accepted by that strategy.

Request body for create or update::

    {
        "name": "zone-migration-template",
        "goal": "hardware_maintenance",
        "strategy": "zone_migration",
        "default_parameters": {
            "compute_nodes": [{"src_node": "compute-1"}]
        }
    }

A new API microversion will be introduced to support the new
``default_parameters`` field independently of the Audit Pipeline APIs.

``Audit Pipeline - New Resource APIs``

Create Audit Pipeline:

* Method: POST
* URL: ``/v1/audit_pipelines``
* Normal response: 201 Created
* Error responses: 400 Bad Request, 404 Not Found

Request body::

    {
        "name": "maintenance-pipeline",
        "audit_type": "ONESHOT",
        "execution_mode": "cascade",
        "auto_trigger": true,
        "stages": [
            {
                "name": "maintenance",
                "description": "Move workloads from compute-1",
                "audit_template": "zone-migration-template"
            },
            {
                "name": "rebalance",
                "audit_template": "workload-balance-template"
            }
        ]
    }

The create schema requires ``audit_type``, ``execution_mode``, and ``stages``.
``audit_type`` only accepts ``ONESHOT`` in the initial microversion.
``execution_mode`` only accepts ``cascade``. ``stages`` must contain at least
two and no more than ten entries. ``name`` and ``auto_trigger`` are optional,
and ``auto_trigger`` defaults to ``true``. Stage ``audit_template`` is
required. Stage ``name`` and ``description`` are optional. Additional
properties are rejected at the pipeline and stage levels.

Response body::

    {
        "uuid": "pipeline-uuid",
        "name": "maintenance-pipeline",
        "audit_type": "ONESHOT",
        "execution_mode": "cascade",
        "state": "PENDING",
        "auto_trigger": true,
        "stages": [
            {
                "uuid": "stage-uuid-1",
                "position": 0,
                "name": "maintenance",
                "description": "Move workloads from compute-1",
                "audit_template_uuid": "template-uuid-1",
                "goal_uuid": "goal-uuid-1",
                "strategy_uuid": "strategy-uuid-1"
            },
            {
                "uuid": "stage-uuid-2",
                "position": 1,
                "name": "rebalance",
                "audit_template_uuid": "template-uuid-2",
                "goal_uuid": "goal-uuid-2",
                "strategy_uuid": "strategy-uuid-2"
            }
        ],
        "links": []
    }

The API will reject unsupported ``audit_type`` values, unsupported
``execution_mode`` values, fewer than two stages, more than ten stages, missing
Audit Templates, and invalid template default parameters with
``400 Bad Request`` or ``404 Not Found`` as appropriate.

List Audit Pipelines:

* Method: GET
* URL: ``/v1/audit_pipelines``
* Normal response: 200 OK

The list API will support the common pagination and sorting query parameters
used by other Watcher collection APIs. It will also support filtering by
``state``, ``audit_type``, and ``execution_mode``.

Get Audit Pipeline:

* Method: GET
* URL: ``/v1/audit_pipelines/{uuid}``
* Normal response: 200 OK
* Error responses: 404 Not Found

The response body has the same shape as the create response.

Update Audit Pipeline:

* Method: PUT
* URL: ``/v1/audit_pipelines/{uuid}``
* Normal response: 200 OK
* Error responses: 400 Bad Request, 404 Not Found, 409 Conflict

PUT is a full-resource update for mutable user fields and is allowed only
while the pipeline is in ``PENDING`` state. The mutable pipeline fields are
``name`` and ``auto_trigger``. The mutable stage fields are ``name`` and
``description``, identified by the stable stage ``uuid`` returned by create or
show. All other fields are immutable. The update schema rejects attempts to add
or remove stages, change stage order, or change a stage ``audit_template``.

Start Audit Pipeline:

* Method: POST
* URL: ``/v1/audit_pipelines/{uuid}/start``
* Normal response: 202 Accepted
* Error responses: 404 Not Found, 409 Conflict

The start action triggers planning for a ``PENDING`` pipeline. It is required
when ``auto_trigger`` is false. It returns ``409 Conflict`` if the pipeline is
not in ``PENDING`` state.

Cancel Audit Pipeline:

* Method: POST
* URL: ``/v1/audit_pipelines/{uuid}/cancel``
* Normal response: 202 Accepted
* Error responses: 404 Not Found, 409 Conflict

Cancel is valid for ``PENDING`` and ``ONGOING`` pipelines. Cancelling a
``PENDING`` pipeline moves it directly to ``CANCELLED``. Cancelling an
``ONGOING`` pipeline records a cancellation request in the database. The
Pipeline Handler checks for that request between stages and before persisting
the final Action Plan. The currently running strategy is not interrupted.

Suspend and resume actions are intentionally not part of the initial ONESHOT
pipeline API.

Delete Audit Pipeline:

* Method: DELETE
* URL: ``/v1/audit_pipelines/{uuid}``
* Normal response: 204 No Content
* Error responses: 404 Not Found, 409 Conflict

Delete is allowed from ``SUCCEEDED``, ``FAILED``, and ``CANCELLED``. Pipelines
in ``ONGOING`` state cannot be deleted and will return ``409 Conflict``. To
delete an ONGOING pipeline, it must first be cancelled.

A new API microversion will be introduced to support Audit Pipeline.

Security impact
---------------

The security posture remains the same as a normal Audit. New policy rules will
be added for Audit Pipeline API endpoints and will follow the same pattern as
the Audit API, requiring administrator privileges for create, read, update,
delete, and action operations.

Notifications impact
--------------------

Watcher currently sends versioned notifications for Audit lifecycle operations.
Audit Pipeline should mirror that behavior.

A new ``watcher.notifications.audit_pipeline`` module will define payloads and
notifications equivalent to the Audit notifications::

    class TerseAuditPipelineStagePayload(NotificationPayloadBase):
        VERSION = '1.0'
        fields = {
            'uuid': wfields.UUIDField(),
            'position': wfields.IntegerField(),
            'name': wfields.StringField(nullable=True),
            'goal_uuid': wfields.UUIDField(),
            'strategy_uuid': wfields.UUIDField(nullable=True),
        }

    class TerseAuditPipelinePayload(NotificationPayloadBase):
        VERSION = '1.0'
        fields = {
            'uuid': wfields.UUIDField(),
            'name': wfields.StringField(nullable=True),
            'audit_type': wfields.StringField(),
            'execution_mode': wfields.StringField(),
            'state': wfields.StringField(),
            'auto_trigger': wfields.BooleanField(),
            'hostname': wfields.StringField(nullable=True),
            'status_message': wfields.StringField(nullable=True),
            'stages': wfields.ListOfObjectsField(
                'TerseAuditPipelineStagePayload'),
        }

    class AuditPipelinePayload(TerseAuditPipelinePayload):
        VERSION = '1.0'
        fields = {}

    class AuditPipelineStateUpdatePayload(NotificationPayloadBase):
        VERSION = '1.0'
        fields = {
            'old_state': wfields.StringField(nullable=True),
            'state': wfields.StringField(nullable=True),
            'status_message': wfields.StringField(nullable=True),
        }

    class AuditPipelineCreatePayload(AuditPipelinePayload):
        VERSION = '1.0'
        fields = {}

    class AuditPipelineUpdatePayload(AuditPipelinePayload):
        VERSION = '1.0'
        fields = {
            'state_update': wfields.ObjectField(
                'AuditPipelineStateUpdatePayload')}

    class AuditPipelineActionPayload(AuditPipelinePayload):
        VERSION = '1.0'
        fields = {'fault': wfields.ObjectField(
            'ExceptionPayload', nullable=True)}

    class AuditPipelineDeletePayload(AuditPipelinePayload):
        VERSION = '1.0'
        fields = {}

The corresponding notification wrappers are
``AuditPipelineCreateNotification``, ``AuditPipelineUpdateNotification``,
``AuditPipelineDeleteNotification``, and ``AuditPipelineActionNotification``.

Action Plan notifications will be extended in a new version to include
``audit_pipeline_uuid`` when an Action Plan is created by a pipeline. The
nested Audit payload will be absent for pipeline-created Action Plans.

Other end user impact
---------------------

Users will be able to define default parameters for Audit Templates, which can
simplify creating Audits and Audit Pipeline stages.

python-watcherclient will need updates for the new Audit Template field and
the new Audit Pipeline API resource.

Performance Impact
------------------

* Cascade planning adds computational overhead because multiple strategies are
  evaluated during one planning run.
* The metric data cache reduces redundant datasource API calls by caching
  metrics retrieved during strategy execution.
* The cache increases memory usage during the pipeline planning run. The cache
  is bounded by a single pipeline execution and is discarded when planning
  completes or fails.

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
  dviroel

Work Items
----------

``Phase 1: Audit Template Enhancement``

* Extend Audit Template model with ``default_parameters``.
* Update Audit Template API with a new microversion.
* Validate ``default_parameters`` against the selected strategy schema.
* Adapt Audit creation to merge template defaults with Audit parameters.
* Update python-watcherclient, tests, and documentation for the Audit Template
  changes.

``Phase 2: Metric Data Cache``

* Refactor ``statistic_aggregation`` in each datasource to a private method.
* Implement the caching logic in the base-class ``statistic_aggregation``.
* Ensure caching happens transparently when strategies call datasource methods.
* Make the cache usable by normal Audits and Audit Pipelines.
* Add unit tests and documentation with the implementation changes.

``Phase 3: Audit Pipeline Database Changes``

* Create the Audit Pipeline database model.
* Create the Audit Pipeline Stage database model.
* Update Action Plan to reference either an Audit or an Audit Pipeline.
* Update Action to reference the Audit Pipeline Stage that produced it.
* Add backwards-compatible database migrations for the new tables and nullable
  columns.
* Add object and database API tests for the new models and invariants.

``Phase 4: Object and RPC Changes``

* Add Audit Pipeline and Audit Pipeline Stage objects.
* Add state transition handling for Audit Pipeline.
* Add ``trigger_audit_pipeline`` RPC method to the decision-engine API.
* Add a decision-engine messaging endpoint for Audit Pipeline operations.
* Record the decision-engine hostname that owns an ONGOING pipeline run.
* Add notifications for Audit Pipeline lifecycle and action phases.
* Extend Action Plan notifications for pipeline-created Action Plans.
* Add unit tests with each object and RPC change.

``Phase 5: Pipeline Handler and Planner``

* Implement the Pipeline Handler for orchestrating cascade stage execution.
* Implement mutable CDM updates and metric cache projection between stages.
* Inject scoped CDM into strategy execution via ``BaseStrategy`` setter
  methods.
* Implement the Pipeline Planner for conservative action consolidation and
  conflict detection.
* Implement cancellation checkpoints between pipeline stages.
* Preserve stage origin metadata for actions and efficacy indicators.
* Add unit tests and developer documentation with the implementation changes.

``Phase 6: Pipeline API Changes and Integration Tests``

* Implement Audit Pipeline POST, GET, PUT, DELETE, start, and cancel endpoints.
* Add API sample tests for request and response formats.
* Add integration or functional tests for the end-to-end ONESHOT cascade flow.
* Update API reference and user documentation.

``Phase 7: Client Support``

* Update python-watcherclient with Audit Pipeline commands.
* Add client-side tests and documentation.


Dependencies
============

* No new external dependencies required


Testing
=======

Unit tests will be added with each implementation phase. API sample tests will
cover all new request and response formats, including Audit Template
``default_parameters`` POST and PATCH handling, plus Audit Pipeline create,
show, list, update, delete, start, and cancel endpoints.

Functional or integration tests will cover a full ONESHOT cascade pipeline
flow that creates a pipeline, triggers planning, and verifies that one Action
Plan is created. Tempest scenario coverage should be added for the full
user-visible workflow when the feature is available end to end.


Documentation Impact
====================

``User Documentation``

* New section in the User Guide: "Audit Pipeline".
* Audit Template ``default_parameters`` usage.
* Audit Pipeline lifecycle and state transitions.
* Cascade execution examples for strategy combinations.
* Known limitations section describing which action types are fully simulated
  by the CDM mutation layer and which are carried as constraints.

``API Reference``

* Document the Audit Template ``default_parameters`` field.
* Document the Audit Pipeline resource and APIs.
* Include request and response examples for all new API methods.

``Developer Documentation``

* Describe the Pipeline Handler and Pipeline Planner design.
* Describe transparent metric cache and datasource refactor.
* Describe mutable CDM simulation and supported action types.
* Explain that strategies should remain pipeline-agnostic.


References
==========

* `Watcher Architecture`_
* `Strategy Plugin Development`_
* `Planner Plugin Development`_

.. _Watcher Architecture:
   https://docs.openstack.org/watcher/latest/architecture.html
.. _Strategy Plugin Development:
   https://docs.openstack.org/watcher/latest/contributor/plugin/strategy-plugin.html
.. _Planner Plugin Development:
   https://docs.openstack.org/watcher/latest/contributor/plugin/planner-plugin.html


History
=======

.. list-table:: Revisions
   :header-rows: 1

   * - Release Name
     - Description
   * - 2026.2
     - Introduced
