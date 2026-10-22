# Databricks GitHub Actions Template

## Overview

This repository is a minimal template for a Databricks project on GitHub. It includes:

- A **Databricks Asset Bundle** with one job.
- **Genie Data Review** on every pull request. The [Genie Data Review action](https://github.com/guanjieshen/genie_code_code_review_gh_action) checks the change against your workspace (schemas, lineage, deployed jobs, governance tags, metric definitions) and posts one review comment. It runs alongside any other reviewer, such as GitHub Copilot.
- **Bundle deployment** to `prod` on every merge to `main`.

| File | Purpose |
|---|---|
| `databricks.yml` | Bundle with a `dev` target (your workspace user) and a `prod` target |
| `resources/job.yml` | One serverless job |
| `src/trips_daily.py` | Example notebook (reads `samples.nyctaxi.trips`) |
| `.github/workflows/genie-data-review.yml` | Genie Data Review on every pull request |
| `.github/workflows/deploy-bundle.yml` | Deploys `prod` on every merge to `main` |

## Getting started

### 1. Create your repository

Select **Use this template**, then rename `my_project` in `databricks.yml` and set the `catalog` and `schema` defaults.

### 2. Create two service principals

| Service principal | Used by | Access |
|---|---|---|
| Deployer | `deploy-bundle.yml` | Can create jobs and write to your schema |
| Reviewer | `genie-data-review.yml` | Read-only: `USE CATALOG`, `BROWSE`, `USE SCHEMA`, `CAN_VIEW` on the job, `CAN_USE` on a SQL warehouse |

Generate an OAuth secret for each. See the [reviewer setup guide](https://github.com/guanjieshen/genie_code_code_review_gh_action/blob/main/docs/setup.md).

### 3. Add repository variables and secrets

| Name | Type |
|---|---|
| `DATABRICKS_HOST` | Variable |
| `DATABRICKS_CLIENT_ID` | Variable (deployer) |
| `DATABRICKS_CLIENT_SECRET` | Secret (deployer) |
| `GENIE_REVIEWER_CLIENT_ID` | Variable (reviewer) |
| `GENIE_REVIEWER_CLIENT_SECRET` | Secret (reviewer) |

### 4. Develop

```bash
databricks bundle deploy          # deploys the dev target to your user folder
databricks bundle run trips_daily
```

Open a pull request and Genie Data Review comments on it within a few minutes. Merge to `main` to deploy `prod`.

> 💡 **Tip**
> To require approval before production deploys, add required reviewers to the `production` environment in your repository settings.

> ⚠️ **Warning**
> `prod` deploys to `/Workspace/Shared/.bundle/...` so the reviewer can see the deployed job, and the CLI warns that this folder is writable by all users. To restrict it, add a top-level `permissions` block to `databricks.yml`.
