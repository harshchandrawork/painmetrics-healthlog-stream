<div align="center">

# PainMetrics — Symptoms & Health Log

### A structured, longitudinal health-tracking application built with Streamlit and PostgreSQL

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**PainMetrics** is a multi-page application for collecting organized, date-based records of symptoms, pain, daily routines, and activity. It is designed to turn repeated self-reported observations into a consistent relational dataset that can be explored with data-analysis tools.

[Overview](#project-overview) · [Features](#features) · [Data model](#data-model) · [Setup](#getting-started) · [Data science relevance](#data-science-and-analysis) · [Limitations](#privacy-safety-and-limitations)

</div>

---

## Project overview

Pain and symptom experiences are difficult to summarize from memory alone. PainMetrics provides a repeatable way to record observations over time, including pain intensity at different times of day, associated activities, sleep, stiffness, and other daily factors.

The project focuses on **authenticated data capture, persistence, and personal descriptive analysis**. It stores records in PostgreSQL using a stable identity from an OpenID Connect sign-in and a relational schema. The Analysis page helps each signed-in user explore their own log coverage and descriptive trends; it does not provide diagnoses, predictions, treatment recommendations, or causal conclusions.

### Project goals

- Make daily symptom and activity logging straightforward.
- Capture repeated observations in a consistent, structured format.
- Relate daily summaries, pain characteristics, and activities to a profile and date.
- Provide a practical foundation for exploratory analysis of longitudinal data.
- Demonstrate an end-to-end workflow across a Python UI, a relational database, and data-oriented problem framing.

## Features

### Daily summary

Record sleep duration and quality; morning, afternoon, evening, and nighttime pain ratings; stiffness timing, duration, and intensity; pain regions; walking, sitting, and standing time; lumbar support; exercise and workout duration; medication information; fatigue; hydration; and a free-text daily note.

### Activity log

Record one or more activities for a selected date, including time of day, activity type, duration and/or repetitions, and pain before, during, 30 minutes after, and two hours after the activity.

### Pain characteristics

Record primary and secondary pain locations and intensities, pain type, whether pain radiates, and whether it is pinpoint/diffuse or deep/surface.

### Additional capabilities

- Public, unauthenticated showcase pages for getting started, project details,
  and a synthetic sample-patient analysis; signed-in health-log pages remain
  account-scoped.
- A per-account Analysis page for descriptive trends in pain, sleep, stiffness,
  daily routine, and activity-related pain ratings.
- An authenticated sidebar showing the latest entry date for daily summaries,
  activities, and pain logs.
- Per-account data keys derived server-side from the verified identity-provider issuer and subject.
- Current-date or past-date entry selection.
- PostgreSQL persistence with parameterized database queries.
- Database constraints, foreign keys, and reference tables for pain scores and pain types.
- Repeat submissions update daily summary and pain-characteristic records for the same account and date. Submitting the activity form replaces entries previously submitted through the app for that account and date.
- A fresh-install script creates the database, schema, tables, and reference data.

## Data science and analysis

This project is relevant to data analysis and data science because it addresses an upstream challenge common in real analysis projects: collecting repeatable observations and modeling them so records can be joined, validated, and analyzed later.

### Personal analysis supported by the app

The authenticated Analysis page summarizes the current user's records and can help answer descriptive questions such as:

- How do self-reported pain levels vary by time of day or across dates?
- Are sleep quality, stiffness, fatigue, or activity duration associated with reported pain?
- How do pain ratings change before and after different activities?
- How consistently have daily summaries and other log types been recorded, and which daily-summary fields are missing?
- Which pain locations and characteristics have been recorded most often?

The page provides descriptive views and date filtering for the signed-in user's own data. It does not calculate statistical significance, estimate causal effects, train machine-learning models, or make diagnostic conclusions. Interpretations should account for repeated measures, missingness, self-report bias, and confounding; comparisons are not evidence that one factor caused another. Cross-user or population analysis is not part of the app.

### Public synthetic sample analysis

Visitors can review the same analysis views using synthetic records for the
reserved `sample_patient` account without signing in. The page adds calculated
descriptive highlights for pain over time, daily pain by time of day, sleep
duration groups, activity-related ratings, and recorded locations. Its
synthetic-data notice makes clear that authenticated patients can see only
analysis of their own data; public pages do not query real patient accounts.

To create the deterministic sample dataset after initializing the
schema, run `python seed_sample_data.py` with the configured database connection.
It inserts 100 daily summaries, 100 activity records, and 100 pain-characteristic
records for `sample_patient` (plus related lookup/link rows). The script is
idempotent and refuses to overwrite conflicting records; it does not delete data.

### Data workflow

```mermaid
flowchart LR
    A[User enters dated observations] --> B[Streamlit pages]
    B --> C[Python persistence layer]
    C --> D[(PostgreSQL relational schema)]
    D --> E[Account-scoped descriptive analysis]
    D -. future, separate analysis .-> F[De-identified population analysis]
```

## Technology stack

| Area | Technology | Role |
|---|---|---|
| Language | Python | Application logic and database setup |
| User interface | Streamlit | Authenticated multi-page data entry and personal analysis |
| UI component | `streamlit-extras` | Selectable cards on the home page |
| Database | PostgreSQL | Relational storage, constraints, keys, and reference data |
| Database driver | Psycopg 3 | PostgreSQL connections and parameterized SQL |
| Configuration | `python-dotenv` | Loads local database connection settings from `.env` |
| Dependency management | `requirements.txt` | Python package installation |

The requirements file also pins NumPy, pandas, Altair, Vega datasets, and yfinance. The Analysis page uses pandas for per-account descriptive summaries and Streamlit's native charts; other pinned analytical packages may support future extensions.

### Portfolio and engineering concepts

The implemented workflow provides examples of:

- Designing a relational schema for repeated, date-indexed observations.
- Using primary keys, foreign keys, uniqueness rules, and range checks to represent data relationships and enforce basic integrity.
- Separating UI, persistence, and database initialization responsibilities across modules.
- Using parameterized SQL and PostgreSQL upserts for safe, repeatable writes.
- Loading local connection configuration from an environment file rather than embedding credentials in application code.

## Data model

The database is initialized by [`db_init.py`](db_init.py). Its core tables are:

| Table | Purpose |
|---|---|
| `patients` | Profile identifier and optional care-team label |
| `daily_summary_logs` | One daily summary per profile and date |
| `daily_summary_pain_regions` | Pain regions associated with a daily summary |
| `daily_summary_exercises` | Exercise types associated with a daily summary |
| `activity_logs` | Activities and pain ratings around each activity |
| `pain_characteristics` | Daily pain locations, intensity, radiation, and descriptors |
| `pain_characteristic_types` | Links pain records to pain-type reference values |
| `pain_intensity_scale` | Reference scores from 0 to 10 |
| `pain_types` | Reference codes for pain types |

Primary and foreign keys link related records, while unique constraints support the application's account/date update behavior. The app uses an opaque, stable account key in the existing `patient_id` columns. The persistence functions are in [`database.py`](database.py); database initialization and data entry are separate responsibilities.

## Getting started

### Requirements

- Python 3.11 or later
- PostgreSQL running locally or reachable from your machine
- A PostgreSQL role with permission to create a database (needed for local initialization)

### 1. Get the project

```bash
git clone https://github.com/harshchandrawork/painmetrics-healthlog-stream.git
cd painmetrics-healthlog-stream
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Create a `.env` file in the project root. Set `CONN_INFO` to a PostgreSQL connection string for a role that can connect to the maintenance database and create `symptoms_tracker_db`:

```dotenv
CONN_INFO="host=localhost port=5432 user=YOUR_POSTGRES_USER password=YOUR_POSTGRES_PASSWORD"
```

Replace the placeholders with your local PostgreSQL role and password. Keep `.env` private; it is excluded by `.gitignore`. If your database provider requires TLS or additional connection options, include the appropriate libpq connection parameters in `CONN_INFO`.

### 5. Initialize the database

From the project root, run:

```bash
python db_init.py
```

The setup script connects to PostgreSQL, creates the `symptoms_tracker_db` database if needed, creates the application tables, enables Row Level Security without public policies, and seeds the pain-score and pain-type lookup tables. It does not import historical records.

### 6. Run the application

Configure a local OIDC provider first. For Google, register `http://localhost:8501/oauth2callback` as an authorized redirect URI and place the credentials in `.streamlit/secrets.toml`:

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "REPLACE_WITH_A_RANDOM_SECRET"
client_id = "YOUR_OIDC_CLIENT_ID"
client_secret = "YOUR_OIDC_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

Generate a random cookie secret locally, for example with `openssl rand -hex 32`. This secrets file is git-ignored; never commit it.

Then run:

```bash
streamlit run streamlit_app.py
```

Sign in, choose a logging page, select a date, and submit an entry. For another OIDC provider, use its client credentials and discovery URL instead of Google's.

## Deploy to Streamlit Community Cloud and Supabase

The application connects to PostgreSQL with Psycopg, so Supabase's hosted Postgres database can be used directly. The Cloud app connects server-side; browser users never receive the database connection string.

1. Commit and push the application changes to GitHub. Keep `.env`, `.streamlit/secrets.toml`, database dumps, and `sample_data/` out of the repository. The importer script is tracked, but the CSV data remains local unless you deliberately provide a sanitized test dataset.
2. In Streamlit Community Cloud, create an app from the repository with `streamlit_app.py` as the entry point. It can be deployed before secrets are configured to obtain its public app URL, but do not share it as ready for use yet.
3. Create a Supabase project. In its **Connect** dialog, copy the PostgreSQL **Session pooler** connection string. The pooler is a practical choice for IPv4-only hosting. Use the `postgres` database and keep SSL enabled. Do not use the Supabase `anon` key as a PostgreSQL password.
4. From the local project checkout, place the copied connection string in the local `.env` file and select Supabase's existing database:

   ```dotenv
   CONN_INFO="postgresql://postgres.PROJECT_REF:YOUR_PASSWORD@POOLER_HOST:5432/postgres?sslmode=require"
   DATABASE_NAME=postgres
   ```

   Replace the placeholders with the exact values from Supabase. Percent-encode reserved characters in the password if needed. Run the schema initializer from the project root:

   ```bash
   python db_init.py --schema-only
   ```

   This creates the tables, keys, constraints, reference rows, and owner-scoped Row Level Security policies. Run initialization with the Supabase admin connection only; the Streamlit app should use a separate restricted role.
   To populate the public demo with synthetic records, configure the intended
   database in `.env` and run `python seed_sample_data.py`. The script writes only
   to `sample_patient`, uses the row-level-security identity setting, and preserves
   existing data.
5. In the Supabase SQL Editor, create a role for the app. Replace the password with a unique random value, keep it private, and do not reuse your `postgres` password:

   ```sql
   CREATE ROLE painmetrics_app
       WITH LOGIN PASSWORD 'REPLACE_WITH_A_UNIQUE_RANDOM_PASSWORD'
       NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS;
   GRANT CONNECT ON DATABASE postgres TO painmetrics_app;
   GRANT USAGE ON SCHEMA public TO painmetrics_app;
   GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE
       patients, daily_summary_logs, daily_summary_pain_regions,
       daily_summary_exercises, activity_logs, pain_characteristics,
       pain_characteristic_types
       TO painmetrics_app;
   GRANT USAGE, SELECT ON SEQUENCE
       daily_summary_logs_id_seq, activity_logs_id_seq,
       pain_characteristics_id_seq
       TO painmetrics_app;
   ```

   This role does not own the tables and cannot bypass their RLS policies. Keep the admin credential only for schema initialization and imports; use the restricted role in the deployed app.
6. Create an OIDC client in Google Cloud (or another OIDC provider), using the deployed app URL followed by `/oauth2callback` as an authorized redirect URI. Configure the provider so the intended audience can self-register/sign in; remove provider-side allowlists if any account should be able to use the app.
7. In the Cloud app's **Settings → Secrets**, add TOML in this shape, replacing all placeholders. For `CONN_INFO`, use the Supabase session-pooler host/port and database from the admin connection, but the `painmetrics_app.PROJECT_REF` username and the restricted role's password. Generate a fresh random cookie secret; never reuse or publish it.

    ```toml
    CONN_INFO = "postgresql://painmetrics_app.PROJECT_REF:APP_ROLE_PASSWORD@POOLER_HOST:5432/postgres?sslmode=require"
    DATABASE_NAME = "postgres"

    [auth]
    redirect_uri = "https://YOUR-APP.streamlit.app/oauth2callback"
    cookie_secret = "A_LONG_RANDOM_SECRET"
    client_id = "YOUR_OIDC_CLIENT_ID"
    client_secret = "YOUR_OIDC_CLIENT_SECRET"
    server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
    ```

    Save the secrets and reboot the app. Test sign-in with two separate accounts and confirm both can submit logs. The RLS policies should prevent either account from writing under the other's owner key. The deployed app URL is the public entry point.
8. If the local `sample_data/data/` CSV files are present and you want to load them, run the importer locally using the admin connection in `.env`:

   ```bash
   IMPORT_PATIENT_ID=sample_patient python import_existing_data.py
   ```

   This importer supports the repository's CSV format; it does not import a PostgreSQL dump. To associate an import with one user's account, sign into the app, copy that account's data key from the collapsed section on Home, and use it as `IMPORT_PATIENT_ID`. For actual existing records, first make a private backup, check that source and target schemas match, and plan an explicit account-to-record mapping. Never upload sensitive data to GitHub.

The app provides descriptive analysis but does not include a transaction-level
history browser, export, or delete workflow. Add and test those workflows before
describing it as a complete personal health-record service.

## Repository structure

```text
.
├── streamlit_app.py          # Streamlit entry point and home/navigation
├── pages/
│   ├── analysis.py          # Personal analysis and public synthetic demo
│   ├── daily_summary.py      # Daily symptom and routine entry
│   ├── activities_log.py     # Activity and before/after pain entry
│   └── pain_intensity.py     # Pain location and characteristic entry
├── database.py               # PostgreSQL persistence functions
├── db_init.py                # Fresh database/schema/reference-data setup
├── seed_sample_data.py        # Idempotent synthetic sample-patient seeder
├── import_existing_data.py   # Optional local CSV importer
├── user_identity.py          # OIDC-derived account key
├── requirements.txt          # Python dependencies
├── .streamlit/config.toml    # Streamlit theme and UI settings
└── LICENSE                   # MIT License
```

## Configuration and data handling

- Database connection settings are read from `CONN_INFO`; `DATABASE_NAME` defaults to `symptoms_tracker_db` and can be set to `postgres` for Supabase.
- `.streamlit/secrets.toml` configures local OIDC sign-in and must never be committed.
- Account data keys are SHA-256 hashes of the identity-provider issuer and subject; email addresses are not used as database keys.
- The app stores self-reported health-related information, including pain, medication, and symptom notes. Use synthetic data while evaluating the project.
- The CSV importer is tracked, but local sample data remains excluded from the public repository. Fresh installation creates an empty application database with required reference rows.
- The public showcase reads only the synthetic `sample_patient` account; signed-in analysis remains scoped to each account's server-derived identity.

## Privacy, safety, and limitations

> **Prototype notice:** PainMetrics is an educational portfolio project, not a medical device or clinical decision-support system. It does not diagnose, treat, or replace advice from a qualified healthcare professional.

- Do not enter real patient or other sensitive personal health information into this educational deployment. OIDC sign-in does not make the application a production privacy/compliance program.
- The app derives account ownership server-side and the restricted database role is governed by RLS policies, but it has not undergone a security review or compliance assessment. Protect both the database role secret and the Supabase admin credentials.
- Anyone deploying a modified copy is responsible for securing the application, PostgreSQL instance, credentials, backups, network access, and any data they collect, as well as assessing applicable laws and institutional policies.
- Health observations are self-reported and may be incomplete, inaccurate, or affected by selection bias. They should not be treated as clinical evidence without appropriate review.
- Database persistence, entry forms, and account-scoped descriptive analytics are implemented; export/report workflows and predictive modeling are not currently part of the app.

## Development notes

Run the setup script from the repository root so the root `.env` file is discovered. Local initialization requires PostgreSQL to be available and the configured role to have database-creation privileges. For Supabase, set `DATABASE_NAME=postgres` and run `python db_init.py --schema-only`.

There is currently no committed automated test suite or CI workflow. Before relying on changes, validate Python syntax and test database initialization and each entry flow against a disposable PostgreSQL database with synthetic data.

## Roadmap

Possible next steps for the project include:

- Expand personal trend views with clearly documented aggregation and filtering choices.
- Add data-quality checks and a documented export path for analysis.
- Add automated tests for form-to-database behavior and schema initialization.
- Complete a security, privacy, consent, and data-retention review before any real-world data collection.

## Contributing

Suggestions, issues, and pull requests are welcome. Please do not include credentials, database dumps, real patient data, or identifying information in issues, commits, screenshots, or example datasets. Use synthetic data for bug reports and tests.

## License

This project is available under the [MIT License](LICENSE).
