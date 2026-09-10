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


Problem Description
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

Proposed Change
===============

This spec proposes the introduction of an ``Audit Pipeline`` API resource,
which models the composition of multiple strategies executed in sequence.
Each stage is evaluated based on the projected outcome of the prior stages.
A mutable cluster data model, and optionally a transparent metric data cache,
will be passed to each stage to allow simulation of the future state.

This functionality will be implemented through a new ``Audit Pipeline``
resource with dedicated APIs. It builds on the existing Audit Template
``default_parameters`` field, which is already available and is used to define
the strategy parameters of each pipeline stage.

The initial implementation is intentionally scoped to ONESHOT audit pipelines
using cascade execution (where each stage runs sequentially on the projected
state produced by the previous stage). CONTINUOUS and EVENT audit pipelines,
composite execution, and recurring pipeline scheduling are out of scope for the
first implementation and may be proposed in a future spec.

Audit Pipeline Resource
-----------------------

A new ``Audit Pipeline`` resource will be introduced. The first implementation
will support ONESHOT pipelines only. A pipeline starts in ``PENDING`` state and
is triggered by the decision engine in the same general way as an ONESHOT
Audit. The result of a successful pipeline planning run is one Action Plan.

The Audit Pipeline state machine will reuse the existing Audit states. The
initial ONESHOT implementation will expose this reduced transition set:

* PENDING -> ONGOING, CANCELLED
* ONGOING -> SUCCEEDED, FAILED, CANCELLING
* CANCELLING -> CANCELLED
* SUCCEEDED -> DELETED
* FAILED -> DELETED
* CANCELLED -> DELETED

All pipelines start in ``PENDING`` state. ``DELETED`` is the final soft-delete
state. ``SUSPENDED`` remains an Audit state only, and suspending and resuming
pipelines is out of scope until recurring CONTINUOUS or EVENT pipelines are
supported.

``CANCELLING`` is an intermediate cancellation state for pipelines that are
already ``ONGOING``. When a cancel request arrives for an ``ONGOING`` pipeline,
the state is set to ``CANCELLING`` and the Pipeline Handler detects this
between stages, aborts the remaining stages without interrupting the strategy
that is currently executing, and then sets the pipeline to ``CANCELLED``. A
``PENDING`` pipeline is moved directly to ``CANCELLED`` without passing through
``CANCELLING`` because no strategy is executing.

An Audit Pipeline is similar to an Audit, with these differences:

* It accepts a list of stage objects. Each stage references one Audit Template.
  The goal, strategy, scope, and parameters used by the stage are snapshotted
  from that Audit Template when the pipeline is created.
* Unlike an Audit, an Audit Pipeline will not accept strategy
  ``input_parameters`` directly. Strategy parameters must be defined as
  ``default_parameters`` in the Audit Template for each stage.
* It does not directly accept a goal or strategy. Those are defined by the
  referenced Audit Templates.
* It supports only ``CASCADE`` execution mode in the initial implementation.
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

Both the pipeline ``name`` and each stage ``name`` are persisted as non-null
values. When the request omits them, the API generates a default. Pipeline
names are unique among non-deleted pipelines, and stage names are unique
within a pipeline; a collision is rejected at create time.

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

The CDM simulation layer applies actions from previous stage solutions to
project the expected cluster state. It does not alter anything beyond what
those solutions explicitly define. Preventing later stages from reverting
earlier decisions is the responsibility of the strategies themselves: a
strategy must include in its solution any actions needed to make the projected
state durable. For example, a host-maintenance strategy should emit a
``change_nova_service_state`` action to disable the maintained node; once
that action is reflected in the projected CDM, the next stage will treat the
node as disabled and will not schedule instances back onto it. Without that
action in the solution, the simulated CDM would still show the node as
available, and a subsequent balancing stage could undo the intended
evacuation.

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

The cache itself is a ``MetricDataCache`` keyed on the tuple of resource id,
meter name, aggregate, period, and granularity. Entries are tagged as either
observed or simulated, which lets handlers drop only the projected values
while retaining real datasource reads.

This approach keeps the strategy interface unchanged and makes caching
transparent to both existing and future strategies. The same mechanism applies
to normal Audits, where the cache acts as a lightweight per-audit cache.

Strategy Execution Context
--------------------------

``BaseStrategy`` is extended to allow the Pipeline Handler to inject
pre-populated cluster data models before executing each stage. Setter methods
are added for ``compute_model`` and ``storage_model`` so the Pipeline Handler
can supply projected CDMs directly. When a setter has been used, the property
returns the injected model instead of invoking the collector. If no model has
been injected, the existing lazy collector behaviour is preserved.

The Pipeline Handler initialises the compute CDM from the stage-0 strategy on
the first stage, then injects a deep copy into every subsequent stage. After
each stage, the compute CDM is mutated to reflect ``migrate`` and
``change_nova_service_state`` actions based on the stage's solution.

The Pipeline Handler also initialises the storage CDM from the stage-0
strategy on the first stage and injects a deep copy into every subsequent
stage. After each stage, the storage CDM is mutated to reflect ``move_volume``
actions based on the stage's solution.

Injection for ``baremetal_model`` is deferred to a future iteration.

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
  stage each action originated from for the duration of the merge;
* aggregating the per-stage efficacy indicators into pipeline-level indicators;
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

    def trigger_audit_pipeline(self, context, audit_pipeline_uuid=None):
        if not utils.is_uuid_like(audit_pipeline_uuid):
            raise exception.InvalidUuidOrName(name=audit_pipeline_uuid)
        cctxt = self.conductor_client.prepare(version='1.1')
        cctxt.cast(
            context, 'trigger_audit_pipeline',
            audit_pipeline_uuid=audit_pipeline_uuid)

The decision-engine ``AuditEndpoint`` RPC interface is bumped from ``1.0`` to
``1.1`` to add ``trigger_audit_pipeline``.

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
Because different goals use different indicator names for the same concept
(e.g. ``zone_migration`` reports ``planned_live_migrate_instance_count``
while consolidation strategies report ``instance_migrations_count``), the
Pipeline Planner normalises the per-stage indicators through a grouping
layer before persisting them.

A ``PipelineIndicatorGroup`` declares a set of source indicator names that
are semantically equivalent and sums their values across all stage
solutions into a single combined pipeline-level indicator.  The default
groups are:

* ``pipeline_instance_migrations_count`` — aggregates
  ``instance_migrations_count``, ``planned_live_migrate_instance_count``,
  and ``planned_cold_migrate_instance_count``.
* ``pipeline_released_compute_nodes_count`` — aggregates
  ``released_compute_nodes_count``.
* ``pipeline_volume_migrations_count`` — aggregates
  ``planned_volume_migrate_count``.

The combined indicators are stored as ``EfficacyIndicator`` rows linked to
the Action Plan, using the existing data model without requiring new
database columns or per-stage storage.

Additionally, when the pipeline optimiser collapses or removes redundant
migration chains, the number of eliminated migrations is recorded in the
Action Plan's ``global_efficacy`` field as
``pipeline_migrations_collapsed_count``.

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
    |     - Fetch initial scoped compute and storage CDMs               |
    |     - Initialize transparent metric cache                         |
    |                                                                   |
    |  2. Cascade simulation loop, stage 1 to N                         |
    |     +---------------------------------------------------------+   |
    |     | (check for CANCELLING; abort remaining stages if set)   |   |
    |     |                                                         |   |
    |     | a. Project current world (pre-stage steps)              |   |
    |     |    - Apply previous solution to compute and storage CDM |   |
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

Data Model Impact
-----------------

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
        id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                    primary_key=True, autoincrement=True)
        uuid = Column(String(36), nullable=False)
        name = Column(String(63), nullable=False)
        description = Column(String(255), nullable=True)
        execution_mode = Column(String(20), nullable=False)
        state = Column(String(20), nullable=False)
        audit_type = Column(String(20), nullable=False)
        auto_trigger = Column(Boolean, nullable=False, default=False)
        hostname = Column(String(255), nullable=True)
        status_message = Column(String(255), nullable=True)

        stages = orm.relationship(
            'AuditPipelineStage',
            foreign_keys='AuditPipelineStage.audit_pipeline_id',
            order_by='AuditPipelineStage.position',
            back_populates='audit_pipeline',
            lazy=None)

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
            UniqueConstraint('name', 'audit_pipeline_id', 'deleted',
                             name='uniq_audit_pipeline_stages0name'),
            UniqueConstraint('position', 'audit_pipeline_id',
                             name='uniq_audit_pipeline_stages0position'),
            table_args()
        )
        id = Column(BigInteger().with_variant(Integer, 'sqlite'),
                    primary_key=True, autoincrement=True)
        uuid = Column(String(36), nullable=False)
        audit_pipeline_id = Column(
            BigInteger().with_variant(Integer, 'sqlite'),
            ForeignKey('audit_pipelines.id'), nullable=False)
        position = Column(Integer, nullable=False)
        name = Column(String(63), nullable=False)
        description = Column(String(255), nullable=True)
        goal_id = Column(Integer, ForeignKey('goals.id'), nullable=False)
        strategy_id = Column(
            Integer, ForeignKey('strategies.id'), nullable=True)
        scope = Column(JSONEncodedList, nullable=True)
        parameters = Column(JSONEncodedDict, nullable=True)

        audit_pipeline = orm.relationship(
            AuditPipeline, foreign_keys=audit_pipeline_id,
            back_populates='stages', lazy=None)
        goal = orm.relationship(Goal, foreign_keys=goal_id, lazy=None)
        strategy = orm.relationship(
            Strategy, foreign_keys=strategy_id, lazy=None)

The stage stores a snapshot of the referenced Audit Template's goal, strategy,
scope, and default parameters at pipeline creation time. Later edits or deletes
of the Audit Template do not change existing pipelines. The source template
reference is intentionally not stored because the Audit Template may be updated
or deleted independently after the pipeline is created.

``Action Plan Changes``

Update the existing ``ActionPlan`` model to make ``audit_id`` and
``strategy_id`` nullable and add a foreign key to ``AuditPipeline``::

    class ActionPlan(Base):
        ...
        audit_id = Column(Integer, ForeignKey('audits.id'), nullable=True)
        strategy_id = Column(
            Integer, ForeignKey('strategies.id'), nullable=True)
        audit_pipeline_id = Column(
            BigInteger().with_variant(Integer, 'sqlite'),
            ForeignKey('audit_pipelines.id'), nullable=True)

        audit_pipeline = orm.relationship(
            'AuditPipeline', foreign_keys=audit_pipeline_id, lazy=None)

For normal Audit-created Action Plans, ``audit_id`` and ``strategy_id`` remain
populated. This feature does not deprecate ``strategy_id`` for normal Audits.

The ``ActionPlan`` object version is bumped to ``2.4``: ``audit_id`` and
``strategy_id`` become nullable, and the ``audit_pipeline_id`` field plus the
``audit_pipeline`` object field are added.

The ``Action`` model is left unchanged. Stage provenance is tracked in memory
while the Pipeline Planner merges stage solutions, but it is not persisted per
action.

The object save path will enforce that exactly one of ``audit_id`` or
``audit_pipeline_id`` is set. This invariant is enforced in the object layer,
which raises an exception when neither or both are set. When ``audit_id``
is set, ``strategy_id`` must also be set.

When listing Action Plans in an older microversion, pipeline-created Action
Plans are excluded (the list is filtered on ``audit_pipeline_id`` being null)
because their ``audit_id`` and ``strategy_id`` fields cannot be represented by
the older response contract, and the ``audit_pipeline_uuid`` field is unset in
the response. In the new microversion, Action Plan responses include
``audit_pipeline_uuid`` for pipeline-created Action Plans, with ``audit_uuid``
and ``strategy_uuid`` null, and the list API accepts an
``audit_pipeline_uuid`` filter.

The database migration adds the nullable columns and new tables in a
backwards-compatible way, and relaxes ``action_plans.audit_id`` and
``action_plans.strategy_id`` to nullable. No data migration is required for
existing Audits, Action Plans, or Actions.

REST API Impact
---------------

``Audit Pipeline - New Resource APIs``

All Audit Pipeline endpoints are gated behind API microversion ``1.8``.
Clients negotiating an older microversion get ``404 Not Found`` for every
``/v1/audit_pipelines`` route.

Create Audit Pipeline:

* Method: POST
* URL: ``/v1/audit_pipelines``
* Normal response: 201 Created
* Error responses: 400 Bad Request, 404 Not Found

Request body::

    {
        "name": "maintenance-pipeline",
        "description": "Maintenance and rebalance pipeline",
        "audit_type": "ONESHOT",
        "execution_mode": "CASCADE",
        "auto_trigger": false,
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
``execution_mode`` only accepts ``CASCADE``. ``stages`` must contain at least
two and no more than ten entries. ``name``, ``description``, and
``auto_trigger`` are optional, and ``auto_trigger`` defaults to ``false``.
Stage ``audit_template`` is required. Stage ``name`` and ``description`` are
optional. Additional properties are rejected at the pipeline and stage levels.

When ``name`` is omitted at either level, the API generates one. A
pipeline name that collides with an existing non-deleted pipeline is rejected,
and duplicate stage names within one request are rejected with
``400 Bad Request``.

ONESHOT pipelines are triggered automatically by the API at creation time,
mirroring the behavior of ONESHOT Audits. The ``auto_trigger`` field controls
whether the resulting Action Plan is automatically launched after the pipeline
execution succeeds. When ``auto_trigger`` is ``false`` (the default), the
Action Plan is created in ``RECOMMENDED`` state and the operator must launch
it manually.

Response body::

    {
        "uuid": "pipeline-uuid",
        "name": "maintenance-pipeline",
        "description": "Maintenance and rebalance pipeline",
        "audit_type": "ONESHOT",
        "execution_mode": "CASCADE",
        "state": "PENDING",
        "auto_trigger": false,
        "hostname": null,
        "status_message": null,
        "stage_uuids": ["stage-uuid-1", "stage-uuid-2"],
        "stages": [
            {
                "uuid": "stage-uuid-1",
                "position": 0,
                "name": "maintenance",
                "description": "Move workloads from compute-1",
                "audit_pipeline_uuid": "pipeline-uuid",
                "goal_uuid": "goal-uuid-1",
                "goal_name": "hardware_maintenance",
                "strategy_uuid": "strategy-uuid-1",
                "strategy_name": "zone_migration",
                "scope": [],
                "parameters": {"compute_nodes": [{"src_node": "compute-1"}]},
                "created_at": "2026-07-14T10:00:00+00:00",
                "updated_at": null,
                "deleted_at": null
            },
            {
                "uuid": "stage-uuid-2",
                "position": 1,
                "name": "rebalance",
                "description": null,
                "audit_pipeline_uuid": "pipeline-uuid",
                "goal_uuid": "goal-uuid-2",
                "goal_name": "workload_balancing",
                "strategy_uuid": "strategy-uuid-2",
                "strategy_name": "workload_balance",
                "scope": [],
                "parameters": {},
                "created_at": "2026-07-14T10:00:00+00:00",
                "updated_at": null,
                "deleted_at": null
            }
        ],
        "created_at": "2026-07-14T10:00:00+00:00",
        "updated_at": null,
        "deleted_at": null,
        "links": []
    }

``stage_uuids`` is always returned and gives the ordered list of stage UUIDs.
The expanded ``stages`` list is returned by the create, show, and detail views;
it is omitted from the summary list view.

The API will reject unsupported ``audit_type`` values, unsupported
``execution_mode`` values, fewer than two stages, more than ten stages, and
duplicate or over-long names with ``400 Bad Request``. A missing Audit Template
returns ``404 Not Found``. If stage persistence fails after the pipeline row is
created, the pipeline is destroyed so no orphaned rows remain.

List Audit Pipelines:

* Method: GET
* URL: ``/v1/audit_pipelines``
* Normal response: 200 OK

The list API supports the common pagination and sorting query parameters used
by other Watcher collection APIs (``marker``, ``limit``, ``sort_key``,
``sort_dir``), plus filtering by ``state``, ``audit_type``, and
``execution_mode``. The summary view returns ``stage_uuids`` but not the
expanded ``stages`` list.

List Audit Pipelines Detailed:

* Method: GET
* URL: ``/v1/audit_pipelines/detail``
* Normal response: 200 OK

Same query parameters as the list API, with the expanded ``stages`` list
included for every pipeline, following the existing Watcher ``detail``
collection pattern.

Get Audit Pipeline:

* Method: GET
* URL: ``/v1/audit_pipelines/{audit_pipeline}``
* Normal response: 200 OK
* Error responses: 404 Not Found

The response body has the same shape as the create response. As with other
Watcher resources, ``{audit_pipeline}`` may be either the UUID or the name of
the pipeline; this applies to the show, update, cancel, and delete endpoints.

Update Audit Pipeline:

* Method: PUT
* URL: ``/v1/audit_pipelines/{audit_pipeline}``
* Normal response: 200 OK
* Error responses: 400 Bad Request, 404 Not Found, 409 Conflict

PUT updates the mutable user fields. The mutable pipeline fields are ``name``,
``description``, and ``auto_trigger``; all are optional in the request body
and only the supplied fields are changed. ``name`` and ``description`` may be
updated in any pipeline state. ``auto_trigger`` may only be updated while the
pipeline is in ``PENDING`` state; supplying it in any other state returns
``409 Conflict``. All other fields, including stage fields, are immutable.
Stage name and description updates are not supported in the initial
implementation. Renaming to a name already used by another non-deleted pipeline
is rejected.

Cancel Audit Pipeline:

* Method: POST
* URL: ``/v1/audit_pipelines/{audit_pipeline}/cancel``
* Normal response: 202 Accepted
* Error responses: 404 Not Found, 409 Conflict

Cancel is valid for ``PENDING`` and ``ONGOING`` pipelines and returns the
updated pipeline representation. A ``PENDING`` pipeline is moved directly to
``CANCELLED``. An ``ONGOING`` pipeline is moved to ``CANCELLING``; the
Pipeline Handler detects that state between stages and before persisting the
final Action Plan, aborts the remaining stages without interrupting the
currently executing strategy, and then sets the pipeline to ``CANCELLED``.
Cancelling a pipeline already in the terminal ``SUCCEEDED``, ``FAILED``, or
intermediate ``CANCELLING`` state returns ``409 Conflict``.

Suspend and resume actions are intentionally not part of the initial ONESHOT
pipeline API.

Delete Audit Pipeline:

* Method: DELETE
* URL: ``/v1/audit_pipelines/{audit_pipeline}``
* Normal response: 204 No Content
* Error responses: 404 Not Found, 409 Conflict

Delete is allowed from ``SUCCEEDED``, ``FAILED``, and ``CANCELLED``, and
performs a soft delete. Pipelines in ``PENDING`` or ``ONGOING`` state cannot be
deleted and return ``409 Conflict``; they must be cancelled first.

Audit Pipeline is introduced in API microversion ``1.8``.

Security Impact
---------------

The security posture remains the same as a normal Audit. New policy rules are
added for Audit Pipeline API endpoints and follow the same pattern as the Audit
API, requiring administrator privileges (``RULE_ADMIN_API``).

Notifications Impact
--------------------

Watcher currently sends versioned notifications for Audit lifecycle operations.
Audit Pipeline should mirror that behavior.

A new ``watcher.notifications.audit_pipeline`` module will define payloads and
notifications equivalent to the Audit notifications::

    class AuditPipelineStagePayload(NotificationPayloadBase):
        VERSION = '1.0'
        fields = {
            'uuid': wfields.UUIDField(),
            'position': ovo_fields.IntegerField(),
            'name': ovo_fields.StringField(nullable=True),
            'goal_uuid': wfields.UUIDField(),
            'strategy_uuid': wfields.UUIDField(nullable=True),
        }

    class TerseAuditPipelinePayload(NotificationPayloadBase):
        VERSION = '1.0'
        fields = {
            'uuid': wfields.UUIDField(),
            'name': ovo_fields.StringField(nullable=True),
            'audit_type': ovo_fields.StringField(),
            'execution_mode': ovo_fields.StringField(),
            'state': ovo_fields.StringField(),
            'auto_trigger': ovo_fields.BooleanField(),
            'hostname': ovo_fields.StringField(nullable=True),
            'status_message': ovo_fields.StringField(nullable=True),
            'created_at': ovo_fields.DateTimeField(nullable=True),
            'updated_at': ovo_fields.DateTimeField(nullable=True),
            'deleted_at': ovo_fields.DateTimeField(nullable=True),
        }

    class AuditPipelinePayload(TerseAuditPipelinePayload):
        VERSION = '1.0'
        fields = {
            'stages': ovo_fields.ListOfObjectsField(
                'AuditPipelineStagePayload')}

    class AuditPipelineStateUpdatePayload(NotificationPayloadBase):
        VERSION = '1.0'
        fields = {
            'old_state': ovo_fields.StringField(nullable=True),
            'state': ovo_fields.StringField(nullable=True),
            'status_message': ovo_fields.StringField(nullable=True),
        }

    class AuditPipelineCreatePayload(AuditPipelinePayload):
        VERSION = '1.0'
        fields = {}

    class AuditPipelineUpdatePayload(TerseAuditPipelinePayload):
        VERSION = '1.0'
        fields = {
            'state_update': ovo_fields.ObjectField(
                'AuditPipelineStateUpdatePayload')}

    class AuditPipelineActionPayload(TerseAuditPipelinePayload):
        VERSION = '1.0'
        fields = {'fault': ovo_fields.ObjectField(
            'ExceptionPayload', nullable=True)}

    class AuditPipelineDeletePayload(AuditPipelinePayload):
        VERSION = '1.0'
        fields = {}

The stage list is carried only by the create and delete payloads, which
describe the full pipeline. Update and state-transition events derive from
``TerseAuditPipelinePayload`` and omit the stages, because stages are immutable
after creation and would only repeat data the consumer already has.

The corresponding notification wrappers are
``AuditPipelineCreateNotification``, ``AuditPipelineUpdateNotification``,
``AuditPipelineDeleteNotification``, and ``AuditPipelineActionNotification``.
The action notification covers the ``start``, ``end``, and ``error`` phases of
a pipeline execution.

The Action Plan notification payloads are bumped to version ``1.3``:
``audit_uuid`` and ``strategy_uuid`` become nullable, ``audit_pipeline_uuid``
is added to ``TerseActionPlanPayload``, and a nested ``audit_pipeline`` object
field is added to ``ActionPlanPayload``. For pipeline-created Action Plans the
nested Audit payload is absent and the nested Audit Pipeline payload is
populated; for Audit-created Action Plans the reverse holds.

Other End User Impact
---------------------

python-watcherclient will need updates for the new Audit Pipeline API
resource.

Performance Impact
------------------

* Cascade planning adds computational overhead because multiple strategies are
  evaluated during one planning run.
* The metric data cache reduces redundant datasource API calls by caching
  metrics retrieved during strategy execution.
* The cache increases memory usage during the pipeline planning run. The cache
  is bounded by a single pipeline execution and is discarded when planning
  completes or fails.

Other Deployer Impact
---------------------

None

Developer Impact
----------------

None

Upgrade Impact
--------------

None

Implementation
==============

Assignee(s)
-----------

Primary assignee:
  dviroel

Work Items
----------

``Phase 1: Metric Data Cache``

* Refactor ``statistic_aggregation`` in each datasource to a private method.
* Implement the caching logic in the base-class ``statistic_aggregation``.
* Ensure caching happens transparently when strategies call datasource methods.
* Make the cache usable by normal Audits and Audit Pipelines.
* Add unit tests and documentation with the implementation changes.

``Phase 2: Audit Pipeline Database Changes``

* Create the Audit Pipeline database model.
* Create the Audit Pipeline Stage database model.
* Update Action Plan to reference either an Audit or an Audit Pipeline.
* Add backwards-compatible database migrations for the new tables and nullable
  columns.
* Add object and database API tests for the new models and invariants.

``Phase 3: Object and RPC Changes``

* Add Audit Pipeline and Audit Pipeline Stage objects.
* Add state transition handling for Audit Pipeline.
* Add ``trigger_audit_pipeline`` RPC method to the decision-engine API.
* Add a decision-engine messaging endpoint for Audit Pipeline operations.
* Record the decision-engine hostname that owns an ONGOING pipeline run.
* Add notifications for Audit Pipeline lifecycle and action phases.
* Extend Action Plan notifications for pipeline-created Action Plans.
* Add unit tests with each object and RPC change.

``Phase 4: Pipeline Handler and Planner``

* Implement the Pipeline Handler for orchestrating cascade stage execution.
* Implement mutable CDM updates and metric cache projection between stages.
* Inject scoped CDM into strategy execution via ``BaseStrategy`` setter
  methods.
* Implement the Pipeline Planner for conservative action consolidation and
  conflict detection.
* Implement cancellation checkpoints between pipeline stages.
* Track stage origin while merging actions and aggregate per-stage efficacy
  indicators into pipeline-level indicators.
* Add unit tests and developer documentation with the implementation changes.

``Phase 5: Pipeline API Changes and Integration Tests``

* Implement Audit Pipeline POST, GET, detail, PUT, DELETE, and cancel
  endpoints behind API microversion 1.8.
* Add policy rules for every Audit Pipeline endpoint.
* Expose ``audit_pipeline_uuid`` on Action Plan responses and as a list filter,
  and hide pipeline-created Action Plans from older microversions.
* Add API sample tests for request and response formats.
* Add integration or functional tests for the end-to-end ONESHOT cascade flow.
* Update API reference and user documentation.

``Phase 6: Client Support``

* Update python-watcherclient with Audit Pipeline commands.
* Add client-side tests and documentation.


Dependencies
============

* No new external dependencies required


Testing
=======

Unit tests will be added with each implementation phase. API sample tests will
cover all new request and response formats, including Audit Pipeline create,
show, list, update, delete, and cancel endpoints.

Functional or integration tests will cover a full ONESHOT cascade pipeline
flow that creates a pipeline, triggers planning, and verifies that one Action
Plan is created. Tempest scenario coverage should be added for the full
user-visible workflow when the feature is available end to end.


Documentation Impact
====================

``User Documentation``

* New section in the User Guide: "Audit Pipeline".
* Audit Pipeline lifecycle and state transitions.
* Cascade execution examples for strategy combinations.
* Known limitations section describing which action types are fully simulated
  by the CDM mutation layer and which are carried as constraints.

``API Reference``

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
   * - 2027.1
     - Re-proposed. Dropped the Audit Template ``default_parameters``
       extension, which shipped in 2026.2, and aligned the data model,
       notifications, and REST API sections with the implementation.
