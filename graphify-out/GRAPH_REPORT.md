# Graph Report - .  (2026-06-28)

## Corpus Check
- Corpus is ~5,890 words - fits in a single context window. You may not need a graph.

## Summary
- 121 nodes · 146 edges · 28 communities (16 shown, 12 thin omitted)
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 38 edges (avg confidence: 0.55)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Records Admin and Models|Records Admin and Models]]
- [[_COMMUNITY_Events Admin and Models|Events Admin and Models]]
- [[_COMMUNITY_Events Soft Delete Admin|Events Soft Delete Admin]]
- [[_COMMUNITY_Accounts and User Models|Accounts and User Models]]
- [[_COMMUNITY_Django App Configurations|Django App Configurations]]
- [[_COMMUNITY_Admin Index Templates|Admin Index Templates]]
- [[_COMMUNITY_Django Manage Script|Django Manage Script]]
- [[_COMMUNITY_Accounts DB Migrations|Accounts DB Migrations]]
- [[_COMMUNITY_Login Authentication Templates|Login Authentication Templates]]
- [[_COMMUNITY_Event Frontend Templates|Event Frontend Templates]]
- [[_COMMUNITY_Record Frontend Templates|Record Frontend Templates]]
- [[_COMMUNITY_ASGI Deployment Config|ASGI Deployment Config]]
- [[_COMMUNITY_Django Project Settings|Django Project Settings]]
- [[_COMMUNITY_Root URL Routing|Root URL Routing]]
- [[_COMMUNITY_WSGI Deployment Config|WSGI Deployment Config]]
- [[_COMMUNITY_Events DB Migrations|Events DB Migrations]]
- [[_COMMUNITY_Records DB Migrations|Records DB Migrations]]

## God Nodes (most connected - your core abstractions)
1. `Event` - 15 edges
2. `Registration` - 12 edges
3. `Record` - 12 edges
4. `DeletedEvent` - 11 edges
5. `InputFilter` - 9 edges
6. `EventAdmin` - 8 edges
7. `DeletedEventAdmin` - 8 edges
8. `InputFilter` - 7 edges
9. `SchoolYearInputFilter` - 6 edges
10. `YearInputFilter` - 6 edges

## Surprising Connections (you probably didn't know these)
- `Login Template` --conceptually_related_to--> `Accounts Module`  [INFERRED]
  templates/registration/login.html → activity.md
- `Event List Template` --conceptually_related_to--> `Events Module`  [INFERRED]
  templates/events/event_list.html → activity.md
- `Record List Template` --conceptually_related_to--> `Records Module`  [INFERRED]
  templates/records/record_list.html → activity.md
- `Admin Index Template` --conceptually_related_to--> `Admin Features`  [INFERRED]
  templates/admin/index.html → activity.md
- `Admin Index Template` --conceptually_related_to--> `Soft Delete Mechanism`  [INFERRED]
  templates/admin/index.html → activity.md

## Import Cycles
- None detected.

## Communities (28 total, 12 thin omitted)

### Community 0 - "Records Admin and Models"
Cohesion: 0.10
Nodes (12): InputFilter, Media, Meta, RecordAdmin, RecordAdminForm, SchoolYearInputFilter, SoftDeleteFilter, YearInputFilter (+4 more)

### Community 1 - "Events Admin and Models"
Cohesion: 0.21
Nodes (11): InputFilter, Media, RegistrationAdmin, RegistrationInline, SchoolYearInputFilter, YearInputFilter, ActiveManager, DeletedEvent (+3 more)

### Community 4 - "Accounts and User Models"
Cohesion: 0.32
Nodes (5): AbstractUser, CustomUserAdmin, CustomUser, Meta, UserAdmin

### Community 5 - "Django App Configurations"
Cohesion: 0.29
Nodes (4): AccountsConfig, AppConfig, EventsConfig, RecordsConfig

### Community 6 - "Admin Index Templates"
Cohesion: 0.67
Nodes (3): Admin Index Template, Admin Features, Soft Delete Mechanism

## Knowledge Gaps
- **14 isolated node(s):** `Migration`, `Meta`, `Migration`, `Meta`, `Migration` (+9 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Event` connect `Events Admin and Models` to `Records Admin and Models`, `Events Soft Delete Admin`, `Events Views and URLs`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Why does `InputFilter` connect `Events Admin and Models` to `Records Admin and Models`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `Event` (e.g. with `DeletedEventAdmin` and `EventAdmin`) actually correct?**
  _`Event` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Registration` (e.g. with `DeletedEventAdmin` and `EventAdmin`) actually correct?**
  _`Registration` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Record` (e.g. with `InputFilter` and `Media`) actually correct?**
  _`Record` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `DeletedEvent` (e.g. with `DeletedEventAdmin` and `EventAdmin`) actually correct?**
  _`DeletedEvent` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `InputFilter` (e.g. with `DeletedEvent` and `Event`) actually correct?**
  _`InputFilter` has 3 INFERRED edges - model-reasoned connections that need verification._