---
title: "Two patterns that make production database changes boring"
date: 2026-06-02
type: explanation
summary: "Two patterns that make production database changes safe, auditable, and boring. How SCD Type 2 and maker-checker work — and why config data belongs in a database, not your git repo."
tags:
  - databases
  - architecture
  - software-engineering
  - compliance
  - production
  - configuration-management
draft: false
---

Imagine a restaurant where changing the daily special requires a full kitchen renovation. New permits. Contractor review. A week of construction. The fish market calls at 6 AM with beautiful halibut, but the chef can't put it on the board until the renovation crew finishes, the inspector signs off, and the general manager reviews the blueprints.

That's how some teams treat production configuration changes. A prompt template needs a tweak? Pull request. Code review from an engineer who doesn't evaluate prompts. CI pipeline. Deployment. Change request ticket. The works. By the time the change is live, the moment has passed — like telling the chef the halibut is approved three days after it stopped being fresh.

The daily special exists because restaurants figured out something important: the kitchen infrastructure and the menu are two different things. You build the kitchen once, to code, with proper ventilation and fire suppression and health inspections. Then the chef changes the specials board whenever the market delivers something worth serving. The kitchen doesn't change. The specials board does.

Production configuration works the same way. Application logic, database schemas, API contracts — those are the kitchen. Prompt templates, feature flags, business rules, agent skill configs — those are the daily special. And regulated industries figured out how to change the daily special safely decades before most of us wrote our first `SELECT` statement.

Two patterns do most of the work: SCD Type 2 and maker-checker.

---

## The two problems people conflate

When someone says "put it in code so it goes through the SDLC," they're conflating two different concerns:

1. **Change safety**: preventing bad changes from reaching production
2. **Change auditability**: knowing who changed what, when, and why

Code review solves both for *code*. But for runtime configuration — the daily specials — it solves neither well. A prompt template buried in a YAML file gets the same review process as a critical algorithm change. The reviewer is checking for merge conflicts and syntax, not whether the prompt actually classifies orders better. And the audit trail is git history, which tells you when the file changed but not which version was active at 3:47 PM on Tuesday when the system started behaving strangely.

The SDLC is the right process for building the kitchen. It's the wrong process for deciding what goes on the specials board.

This isn't theoretical:

- In 2008, Jérôme Kerviel cost Société Générale €4.9 billion by accumulating enough system entitlements to approve his own trades — one person, both maker and checker. A database constraint enforcing that the proposer and approver must be different people would have made that physically impossible.
- In 2012, Knight Capital lost $440 million in 45 minutes because a configuration deployment reactivated dormant code and no second person signed off on the change.
- And the classic that every DBA has nightmares about: an UPDATE without a WHERE clause on Black Friday that zeroed out a production table and cost $47M — because the old values were gone the moment the UPDATE committed. With SCD2, there is no UPDATE. Every change is a new row. The previous values are always there.
---

## The litmus test: kitchen vs. specials board

Here's the question I use: **does this thing change on the same cadence as a code deployment?**

If yes — it's part of the kitchen. Put it in your repo. Review it. Deploy it.

If no — it's on the specials board. Put it in a database with SCD2 and maker-checker.

| Thing | Changes with deploys? | Verdict |
|-------|----------------------|---------|
| Application logic | Yes | Kitchen |
| Database schema | Yes | Kitchen (migrations) |
| API contracts | Yes | Kitchen |
| Prompt templates | No — tuned weekly, sometimes daily | Specials board |
| Feature flags | No — toggled at runtime | Specials board |
| Business rules / thresholds | No — adjusted by business users | Specials board |
| Agent skill configs | No — updated as capabilities evolve | Specials board |
| Notification templates | No — marketing changes them | Specials board |
| Pricing tiers | No — product changes them quarterly | Specials board |

When a prompt engineer needs to tweak a classifier prompt on Thursday afternoon, they shouldn't need a PR, a code review from an engineer who doesn't understand prompts, a CI pipeline, and a production deployment. They should propose the change, have another prompt engineer approve it, and have the system apply it — with a full audit trail, instant rollback, and zero downtime.

That's not less rigorous than the SDLC. It's *more* rigorous — because the controls are systemic, not procedural. The database constraint enforces dual authorization whether it's Tuesday morning or 2 AM on a holiday. A code review process depends on humans following the rules every time.

---

## Pattern 1: SCD Type 2 — the chef's notebook

Slowly Changing Dimension Type 2 comes from data warehousing, but the pattern applies anywhere you need a complete history of changes to a record. The idea is simple: you never update or delete. Every change inserts a new row.

Think of it as the chef's notebook — the one where every daily special ever served is recorded with the date, what was in it, and why it was chosen. The chef doesn't erase yesterday's entry when today's special changes. They write a new line. Six months from now, when someone asks "what were we running the week that got all those compliments," the answer is right there.

```sql
CREATE TABLE prompt_templates (
    id              SERIAL PRIMARY KEY,
    prompt_key      TEXT NOT NULL,
    template_body   TEXT NOT NULL,
    version         INT NOT NULL,

    -- audit columns (inherited from base model in practice)
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by      TEXT NOT NULL,
    approved_by     TEXT,
    approved_at     TIMESTAMPTZ,
    change_reason   TEXT NOT NULL,

    -- temporal columns
    start_date      TIMESTAMPTZ,            -- set on approval
    end_date        TIMESTAMPTZ,            -- NULL = current
    is_current      BOOLEAN NOT NULL DEFAULT FALSE
);
```

When you change a prompt, you don't `UPDATE`. You propose a new row, a second person approves it, and the system expires the old version and activates the new one:

```sql
-- Step 1: Propose (created_by fills in, approved_by stays NULL)
INSERT INTO prompt_templates
  (prompt_key, template_body, version, created_by, change_reason)
VALUES
  ('order_classifier', 'Classify the following order...', 3,
   'gordon', 'Reduced false positives on international orders');

-- Step 2: Approve (a different user)
BEGIN;
  UPDATE prompt_templates
     SET end_date = now(), is_current = FALSE
   WHERE prompt_key = 'order_classifier' AND is_current = TRUE;

  UPDATE prompt_templates
     SET approved_by = 'marco', approved_at = now(),
         start_date = now(), is_current = TRUE
   WHERE prompt_key = 'order_classifier' AND version = 3;
COMMIT;
```

What you get for free:

- **Full audit trail**: every version that was ever active, who created it, when it was live, and why it changed. Not in a log file somewhere — in the data itself.
- **Point-in-time queries**: "What prompt was active at 2026-05-15 14:30 UTC?" is a one-liner: `WHERE prompt_key = 'order_classifier' AND start_date <= '2026-05-15 14:30+00' AND (end_date IS NULL OR end_date > '2026-05-15 14:30+00')`.
- **Instant rollback**: expire the current row and copy any previous version forward. One transaction. No deployment pipeline.
- **Zero data loss**: nothing is ever physically deleted. Every state the system has ever been in is recoverable.

Compare this to the git-based approach: to answer "what prompt was active during that incident at 3:47 PM," you'd need to correlate git commit timestamps with deployment timestamps with the actual moment the running application picked up the new config. With SCD2, the answer is one query.

### When today's special isn't working: rollback

Thursday's halibut special isn't moving. The chef doesn't tear out the stove and reinstall last week's kitchen. They flip back two pages in the notebook and bring back Tuesday's short rib that sold out by 7 PM.

With SCD2, rollback works the same way. Say version 3 of your prompt is producing bad classifications. You want to go back to version 2 — the one that was working fine last week. Every previous version is still in the table:

```sql
BEGIN;
  -- Expire the current version
  UPDATE prompt_templates
     SET end_date = now(), is_current = FALSE
   WHERE prompt_key = 'order_classifier' AND is_current = TRUE;

  -- Bring back version 2 as a new entry
  INSERT INTO prompt_templates
    (prompt_key, template_body, version, created_by, approved_by,
     approved_at, start_date, is_current, change_reason)
  SELECT
    prompt_key, template_body, 4, 'gordon', 'marco',
    now(), now(), TRUE,
    'Rollback to v2: v3 increased false positives on international orders'
  FROM prompt_templates
  WHERE prompt_key = 'order_classifier' AND version = 2;
COMMIT;
```

Version 3 isn't deleted — it's preserved with timestamps showing exactly when it was active and when it was rolled back. Version 4 is a copy of version 2's content with a new `change_reason` explaining *why*. If an auditor asks what happened, you have the full story: v3 went live at 14:00, caused issues, rolled back at 15:22, and here's what v3 was trying to do.

No deployment queue. No waiting for CI. No merge conflicts because someone else pushed to main in the meantime. The application picks up the rolled-back config on its next read — the way a restaurant picks up the new specials board without rebuilding the dining room.

---

## Pattern 2: Maker-checker — the sous chef and the head chef

Also called the four-eyes principle, maker-checker splits every sensitive operation into two steps: one person proposes a change, a different person approves it. The system physically prevents single-actor completion regardless of permission level.

Every kitchen runs on a version of this. The sous chef writes the special on a ticket. The head chef tastes the dish, approves it, and *then* it goes on the board. Two sets of hands, not because the sous chef can't cook — because the kitchen is designed so nothing reaches the dining room without a second check.

![Maker-checker workflow: Gordon writes the special, Marco Pierre White tastes and approves or rejects — a different person must review](/maker-checker-workflow.svg)

You don't need a separate approvals table. The maker-checker columns live on the same row as the data — the same `prompt_templates` table from above. A row with `approved_by IS NULL` is a pending proposal. A row with `approved_by` filled in and `start_date` set is live. The database enforces the constraint:

```sql
CONSTRAINT different_actors
    CHECK (created_by != approved_by OR approved_by IS NULL)
```

That's the whole point. The database itself enforces that the maker cannot be the checker. This isn't a policy in a wiki that people follow when they remember — it's a constraint that the system cannot violate.

The workflow maps to the columns directly:

1. **Propose**: `created_by` and `created_at` fill in. `approved_by` stays NULL. The row exists but isn't active.
2. **Review**: a different user approves — `approved_by` and `approved_at` fill in.
3. **Activate**: `start_date` is set, `is_current` flips to TRUE, and the previous version gets an `end_date`.

This is how most banks process wire transfers. How most hospitals manage medication orders. The pattern is so well-established that regulators don't just recommend it — they mandate it.

---

## What the regulators actually require

If the instinct is "but compliance won't allow database changes in prod," it's worth checking what the compliance frameworks actually say — because these patterns are exactly what they describe.

Health codes don't require a renovation to change the menu — they require that the kitchen is built to code, and the daily decisions flow through it safely.

Regulatory frameworks work the same way:

| Standard | What it requires | Retention | What SCD2 + maker-checker gives you |
|----------|-----------------|-----------|-------------------------------------|
| **SOX §302/§404** | Internal controls, audit trails for financial systems | 7 years | Immutable history + segregation of duties |
| **HIPAA (21 CFR Part 11)** | Audit trails: who modified data, when, what changed | 6 years | `created_by`, `approved_by`, `start_date`, `change_reason` |
| **PCI-DSS v4.0** | Logging of all changes to system components | 12 months | Approval workflow + full version history |
| **NIST 800-53 AU** | Event logging: who, what, when, where, outcome | Policy-defined | Append-only records, no physical deletes |
| **EU DORA** | Change control with full audit trails for ICT systems | Per-contract | Maker-checker workflow + SCD2 trail |
| **GDPR Article 30** | Records of processing activities: what and why | Duration of processing | `change_reason` field + complete history |

The pattern across all of them: *who* changed *what*, *when*, and *why* — with immutable records and independent verification. That's SCD2 + maker-checker by construction.

---

## Putting it together

The chef's notebook after a week of specials:

| v | special | created | approved | start | end   | cur | reason |
|---|---------|---------|----------|-------|-------|-----|--------|
| 1 | Pan-seared halibut, lemon beurre blanc | Gordon | Marco | Mon | Wed | no | Fresh halibut from market |
| 2 | Wagyu beef tartare, truffle vinaigrette | Gordon | Marco | Wed | Fri | no | Wagyu delivery came in |
| 3 | Lobster risotto, saffron cream | Marco | Gordon | Fri | Sat | no | Weekend prix fixe |
| 4 | Wagyu beef tartare, truffle vinaigrette | Gordon | Marco | Sat | — | yes | Rollback: risotto undersold |

Four rows. Every special that ran, who wrote it, who approved it, when it was live, and why it changed. Saturday's special is Wednesday's wagyu brought back — the risotto didn't sell, so they flipped the notebook back two pages. Nothing erased. The health inspector can read it top to bottom and see the whole week.

The specials board changes. The kitchen stays.

---

## What's next: making the SQL disappear

The raw SQL in this post is worth understanding — you should know what's happening at the database level. But in a real application, nobody should be writing expire-and-insert transactions by hand.

In a follow-up, I'll show how to wrap these patterns in a domain layer using SQLModel, the Unit of Work pattern, and ports and adapters. The idea: a base model carries all the audit and temporal columns — `created_at`, `created_by`, `approved_by`, `start_date`, `end_date` — and your domain models inherit from it. `PromptTemplate` just adds `prompt_key` and `template_body`. The SCD2 versioning, maker-checker enforcement, and approval workflow happen automatically in the infrastructure layer. Your application code never writes a temporal query directly — the same way a well-run kitchen handles food safety without the chef thinking about health codes on every plate.

---

## Key takeaways

- **SCD Type 2** gives you a complete, immutable history of every configuration change — who, what, when, why — queryable by timestamp.
- **Maker-checker** enforces dual authorization at the database level, not as a policy people can skip.
- Together, these patterns map directly to the audit trail requirements of SOX, HIPAA, PCI-DSS, NIST 800-53, DORA, and GDPR — giving you the building blocks by construction, not by procedure.
- The litmus test: if it changes on a different cadence than your code deployments, it's data, not code. Treat it accordingly.
- Rollback is one transaction, not a revert-rebuild-redeploy cycle.
- The fear of production isn't solved by avoiding production. It's solved by building the kitchen to code so the daily specials can change safely.

---

## Further reading

- [Société Générale: the €4.9B rogue trader](https://en.wikipedia.org/wiki/2008_Soci%C3%A9t%C3%A9_G%C3%A9n%C3%A9rale_trading_loss) — one person approved his own trades; dual authorization would have stopped it
- [The Knight Capital disaster](https://www.henricodolfing.ch/en/case-study-4-the-440-million-software-error-at-knight-capital/) — $440M lost in 45 minutes from an unreviewed config deployment
- [The $47M UPDATE without a WHERE clause](https://thecodeforge.io/database/sql-insert-update-delete/) — destructive UPDATE zeroed out production data; SCD2's append-only model prevents this by design
- [SCD Type 2 explained](https://www.analyticsengineering.com/resources/slowly-changing-dimensions-type-2-explained) — comprehensive walkthrough of the pattern
- [Building audit logs with CDC and SCD Type 2](https://www.artie.com/blogs/how-to-build-audit-logs-using-cdc-and-scd-type-2) — combining change data capture with SCD2
- [Maker-checker implementation guide for fintech](https://www.opcito.com/blogs/maker-checker-implementation-guide-for-secure-fintech-systems) — real-world banking implementation
- [NIST 800-53 AU controls](https://csf.tools/reference/nist-sp-800-53/r5/au/) — the audit and accountability family
- [DORA and database teams](https://www.liquibase.com/blog/what-is-the-digital-operational-resilience-act-dora-what-financial-database-developer-teams-need-to-know) — what DORA means for database change management
- [Feature flags vs. config files vs. deployment](https://launchdarkly.com/blog/feature-flags-vs-deployment-automation-vs-config-files/) — when each approach is appropriate
- [Martin Fowler on feature toggles](https://martinfowler.com/articles/feature-toggles.html) — the canonical reference on runtime configuration
