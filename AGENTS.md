# Agent guide

Instructions for coding agents (Claude Code, Codex, Copilot, Genie Code) working in a repository created from this template. People can read it too: it is the short version of the README.

> **Code review agents:** this guide is about writing and deploying code. It does not change review rules. If you are Lakehouse Review, follow your own charter.

## What this repository is

A **Databricks Asset Bundle** with GitHub Actions around it:

| Path | What it is | Change it when |
| --- | --- | --- |
| `databricks.yml` | The bundle: name, `catalog` and `schema` variables, `dev` and `prod` targets | Renaming the project, adding variables or targets |
| `resources/*.yml` | Jobs and pipelines, one resource per file | Adding or changing a job |
| `src/` | Code the jobs run: notebooks as `.py` source files, SQL files, Python modules | Changing what a job does |
| `.github/workflows/genie-data-review.yml` | **Lakehouse Review** on every pull request | Turning review options on or off |
| `.github/workflows/deploy-bundle.yml` | Deploys `prod` on every merge to `main` | Rarely |
| `.lakehouse-review/` (optional) | Review settings and team context, read from `main` | Tuning the review |

## Everyday commands

Run from the repository root with a Databricks CLI profile for your own user:

```bash
databricks bundle validate                 # always run this after editing databricks.yml or resources/
databricks bundle deploy                   # deploys the dev target to your user folder
databricks bundle run trips_daily          # runs a job in dev
```

**Never deploy `prod` from a laptop.** `prod` is deployed by `deploy-bundle.yml` after a pull request merges.

## How to make changes

1. Create a branch, change the code, and run `databricks bundle validate`.
2. Deploy and run in `dev` to check the result.
3. Open a pull request. Lakehouse Review comments on it within a few minutes.
4. Fix what it reports, or explain in the pull request why a finding does not apply. Then merge.

### Adding a job

- Add `resources/<job_name>.yml` with one job. Copy `resources/job.yml` as a starting point.
- Put its code in `src/`. Notebooks are `.py` files that start with `# Databricks notebook source`.
- Pass `catalog` and `schema` as task parameters (`${var.catalog}`, `${var.schema}`). **Do not hardcode catalogs or schemas.**
- Use serverless compute unless the job needs a cluster. If it does, use a current LTS runtime the workspace offers.

### Writing code the review can check

Lakehouse Review reads the code to find the tables and columns each task uses, then checks them against Unity Catalog. It can check what it can resolve:

| Do | Avoid |
| --- | --- |
| `spark.table(f"{catalog}.{schema}.orders")` with `catalog` and `schema` from task parameters | Table names read from a config file or built in a loop at runtime |
| Fully qualified names in SQL (`catalog.schema.table`), or `IDENTIFIER(:catalog \|\| '.' \|\| :schema \|\| '.table')` | Unqualified table names that depend on the session's current schema |
| Notebooks as `.py` source files | `.ipynb` notebooks (not reviewed yet) |
| Explicit column lists and casts in joins between different types | `SELECT *` into tables other jobs read |

Names it cannot resolve are listed as **unresolved** in the review's coverage section; they are not errors.

## Lakehouse Review

The review runs on every pull request with a **read-only** service principal. It posts one review comment, updated on each push, and comments on the code line of each issue that is part of the diff.

| Severity and status | What to do |
| --- | --- |
| **Blocker** (confirmed critical contract, lineage, or deployment issue) | Fix before merging. For example, a removed column that a downstream table still reads. |
| **Action required** | Fix, or explain in the pull request why it does not apply. |
| **Review recommended**, **Informational** | Read and decide. |

Each finding cites the Unity Catalog fact it is based on, under **Technical evidence**. If the comment says **Partial review**, the reviewer is missing access; the **Analysis coverage** section lists the exact grant to add.

To configure it:

| You want to… | Where |
| --- | --- |
| Fail the check on blocking issues | `fail-on: blocker` in `genie-data-review.yml` |
| Merge one pull request despite blocking issues | Add the `lakehouse-review-override` label to it. Only do this when a person asks for it. |
| Check joins, grain, and status codes against the workspace's Pages and metric views | `analysis-depth: detailed` in `genie-data-review.yml` |
| Give the reviewer team context (for example "`main` is production") | `.lakehouse-review/instructions.md`, with `instructions_file: .lakehouse-review/instructions.md` in `.lakehouse-review/config.yml` |
| Turn a check off or change its severity | `checks` in `.lakehouse-review/config.yml` |
| Post only the review comment, without comments on code lines | `inline-comments: false` in `genie-data-review.yml` |

**The config file and instructions are read from `main`**, so changes to them take effect after they merge. Unknown settings fail the check. All inputs and settings are documented at <https://github.com/guanjieshen/genie_code_code_review_gh_action/tree/main/docs>.

## Rules

- **No secrets in the repository.** Credentials live in GitHub variables and secrets (`DATABRICKS_HOST`, `DATABRICKS_CLIENT_ID`, `DATABRICKS_CLIENT_SECRET`, `GENIE_REVIEWER_CLIENT_ID`, `GENIE_REVIEWER_CLIENT_SECRET`).
- **Do not give the reviewer service principal write access** or `SELECT` on data. It only needs `USE CATALOG` and `BROWSE`.
- **Do not change the action versions in the workflows** unless asked. Upgrades go in their own pull request.
- **Keep `prod` on a shared `root_path`** (`/Workspace/Shared/.bundle/...`). The review compares the deployed job with the bundle, and it cannot read a personal folder.
- Do not commit `.databricks/` or generated files.
