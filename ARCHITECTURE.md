# EMA Pingbot Architecture

This document describes the current architecture of the EMA Pingbot application as implemented in this repository.

EMA Pingbot is a web application for running ecological momentary assessment studies. Researchers use the web UI to create studies, configure ping templates, and monitor participants. Participants enroll through a public web flow, link their Telegram account through the Telegram bot, and receive scheduled Telegram messages that forward them to an external survey platform.

## System Overview

The application is split into four main runtime services:

| Service | Location | Purpose |
| --- | --- | --- |
| React frontend | `react_frontend/` | Researcher UI, participant enrollment page, participant dashboard |
| Flask backend | `flask_app/` | REST API, authentication, database access, ping forwarding, support requests |
| Celery worker/beat | `flask_app/` | Background scheduler that checks for due pings and reminders |
| Telegram bot | `bot/` | Telegram command interface for participant enrollment, dashboard login, and contact messages |
| Nginx | `nginx/` | Serves the built frontend, proxies API traffic, terminates TLS, forwards Telegram webhooks |

Redis is used for Celery broker/result storage and JWT blocklisting. The backend expects a PostgreSQL database through `SQLALCHEMY_DATABASE_URI`.

## Deployment Topology

`docker-compose.yml` defines the production-like topology:

- `nginx` listens on ports `80` and `443`.
- `/` serves the built React app from `/usr/share/nginx/html`.
- `/api/` proxies to `flask-backend:8000`.
- `/webhook` proxies to the Telegram bot service on port `8443`.
- `flask-backend` runs Gunicorn with `run:app`.
- `celery-worker` runs `celery -A celery_app.celery worker`.
- `celery-beat` runs `celery -A celery_app.celery beat`.
- `redis` runs with a password from `REDIS_PASSWORD`.
- `certbot` uses the nginx webroot to issue/renew certificates.

The nginx image is built from `nginx/Dockerfile`. It first builds `react_frontend` with Node, then copies `dist/` into an nginx image. The Flask and bot images are Python 3.11 slim containers.

## Frontend

The frontend is a Vite React app using React Router, Material UI, axios, and localStorage-backed JWT authentication.

Important files:

- `react_frontend/src/App.jsx` defines public and protected routes.
- `react_frontend/src/api/axios.jsx` creates an axios instance with `baseURL: "/api"`, attaches access tokens, and refreshes access tokens on `401`.
- `react_frontend/src/components/PrivateRoute.jsx` gates protected routes by checking for `access_token` in localStorage.
- `react_frontend/src/context/StudyContext.jsx` loads the active study for nested study routes.

Public routes:

- `/login`
- `/register`
- `/enroll/:signup_code`
- `/participant_dash`
- `/help`

Protected researcher routes:

- `/studies`
- `/studies/:studyId`
- `/studies/:studyId/ping_templates`
- `/studies/:studyId/pings`
- `/studies/:studyId/participants`
- `/studies/:studyId/users`

The frontend mostly talks to the backend through `/api/*`. Because nginx proxies `/api/` to Flask, the same axios base URL works in production without hardcoding the backend host.

## Flask Application

The backend is created by `flask_app/app.py:create_app`.

At startup it:

1. Loads environment variables.
2. Creates the Flask app and applies `CurrentConfig`.
3. Applies `ProxyFix` so Flask sees the correct upstream scheme/host behind nginx.
4. Initializes extensions from `extensions.py`.
5. Creates a Celery app with `make_celery`.
6. Imports models.
7. Registers API blueprints.
8. Adds `/health` and error handlers.

Registered blueprints:

| Blueprint | Prefix | File | Responsibility |
| --- | --- | --- | --- |
| `auth_bp` | `/api` | `blueprints/auth.py` | Register, login, refresh, logout |
| `studies_bp` | `/api` | `blueprints/studies.py` | Study CRUD and study user role management |
| `ping_templates_bp` | `/api` | `blueprints/ping_templates.py` | Ping template CRUD |
| `enrollments_bp` | `/api` | `blueprints/enrollments.py` | Researcher enrollment views and updates |
| `pings_bp` | `/api` | `blueprints/pings.py` | Researcher ping views and updates |
| `participant_facing_bp` | `/api` | `blueprints/participant_facing.py` | Public signup, ping forwarding, participant dashboard |
| `bot_bp` | `/api/bot` | `blueprints/bot.py` | Internal endpoints called by the Telegram bot |
| `support_bp` | `/api` | `blueprints/support.py` | Feedback/support form |

`blueprints/users.py` exists but is not registered in `app.py` and currently contains only an incomplete feedback route.

## Configuration

Backend configuration is in `flask_app/config.py`.

`CurrentConfig` is chosen from `FLASK_ENV`:

- `development`: localhost frontend/backend and Redis without password.
- `production`: `https://emapingbot.com`, secure cookies, Redis at `redis` with password.

The backend expects environment variables for:

- mail and Mailtrap settings
- JWT secret
- Telegram bot token and bot shared secret
- Redis password and database URL
- PostgreSQL SQLAlchemy URI
- reCAPTCHA secret

The bot has its own config in `bot/config.py`, selected by `ENV_TYPE`.

## Data Model

SQLAlchemy models live in `flask_app/models.py`.

Core entities:

- `User`: researcher account with email, password hash, profile fields, and support requests.
- `Study`: a research study with public/internal names, unique signup code, and contact message.
- `UserStudy`: join table between users and studies, with role-based access.
- `PingTemplate`: reusable message/survey template for a study. Stores message text, survey URL, display text, reminder/expiry latencies, and a JSON schedule.
- `Enrollment`: participant enrollment in a study. Stores participant timezone, researcher-assigned participant ID, Telegram linking state, dashboard OTP state, and completion percentage.
- `Ping`: concrete scheduled message for a specific enrollment/template.
- `Support`: support/feedback submissions.

Most tables include `deleted_at` for soft deletes. `extensions.py` defines `SoftDeleteQuery`, and many newer queries explicitly filter `deleted_at is None`.

Primary relationships:

- `User` has many `UserStudy`.
- `Study` has many `PingTemplate`, `Ping`, `Enrollment`, and `UserStudy`.
- `Enrollment` has many `Ping`.
- `PingTemplate` has many `Ping`.
- `Ping` belongs to one `Study`, `PingTemplate`, and `Enrollment`.

## Roles And Permissions

Study authorization is implemented in `flask_app/permissions.py`.

Roles are ordered as:

1. `developer`
2. `owner`
3. `editor`
4. `viewer`

Lower numeric rank means more privilege. `user_has_study_permission(user_id, study_id, minimum_role)` returns the study when the user has a sufficient role through `UserStudy`; otherwise it returns `None`.

Typical access rules:

- View study data: `viewer`
- Create/update/delete studies, ping templates, pings, enrollments: `editor`
- Manage study users and roles: `owner`

JWT authentication is handled by Flask-JWT-Extended. Access tokens are issued at login and refreshed through `/api/refresh`. Logout blocklists JWT IDs in Redis.

## Researcher Workflow

1. A researcher registers and logs in through `/api/register` and `/api/login`.
2. The frontend stores `access_token` and `refresh_token` in localStorage.
3. The researcher creates a study through `POST /api/studies`.
4. The backend generates a unique non-confusable study code.
5. The creating user is linked to the study as `owner` in `UserStudy`.
6. The researcher creates ping templates under `/api/studies/:studyId/ping_templates`.
7. The researcher shares the study signup code or enrollment link with participants.

Study user management is handled through:

- `GET /api/studies/:studyId/users`
- `POST /api/studies/:studyId/add_user`
- `PUT /api/studies/:studyId/users/:userId`
- `DELETE /api/studies/:studyId/users/:userId`

## Participant Enrollment Workflow

Participant-facing signup starts in the React route `/enroll/:signup_code`, which posts to:

- `POST /api/signup`

The signup endpoint:

1. Validates the study signup code against `Study.code`.
2. Collects `study_pid` and participant timezone.
3. Creates an `Enrollment` with `enrolled=False`.
4. Generates a six-character Telegram link code.
5. Stores the link code and expiry timestamp.
6. Returns the link code to the participant.

The participant then opens Telegram and runs `/enroll` with the bot. The bot asks for the link code and calls:

- `PUT /api/bot/link_telegram_id`

This bot-only endpoint:

1. Requires `X-Bot-Secret-Key`.
2. Finds the enrollment by `telegram_link_code`.
3. Rejects expired or already-used codes.
4. Prevents linking the same Telegram account to the same study twice.
5. Saves `telegram_id`, marks the code used, and sets `enrolled=True`.
6. Calls `make_pings()` to instantiate scheduled `Ping` rows for all templates in the study.

## Ping Scheduling

Ping templates store a `schedule` JSON array. Each item is expected to include:

- `begin_day_num`
- `begin_time`
- `end_day_num`
- `end_time`

When an enrollment is linked to Telegram, `make_pings()` in `blueprints/enrollments.py` loops over every ping template and every schedule interval.

For each schedule interval:

1. `utils.random_time()` computes a random participant-local datetime inside the interval.
2. The interval is based on the participant's signup date in their timezone.
3. `expire_ts` is calculated from `PingTemplate.expire_latency`.
4. `reminder_ts` is calculated from `PingTemplate.reminder_latency`.
5. A concrete `Ping` row is inserted.

The actual sending is asynchronous and driven by Celery.

## Celery And Message Sending

Celery is configured by:

- `flask_app/celery_app.py`
- `flask_app/celery_factory.py`
- `flask_app/tasks.py`

`BaseConfig.CELERY_BEAT_SCHEDULE` runs `tasks.check_and_send_pings` every minute.

`check_and_send_pings()`:

1. Opens the Flask app context.
2. Queries due pings with `crud.get_pings_to_send(session, now)`.
3. Marks them as sent before sending to reduce duplicate sends.
4. Constructs Telegram messages with `MessageConstructor`.
5. Sends through `TelegramMessenger`.
6. Resets `sent_ts` if Telegram delivery fails.
7. Updates participant `pr_completed`.
8. Calls `check_and_send_reminders()`.

`get_pings_to_send()` only returns pings that:

- have not been sent
- are scheduled at or before `now`
- are no more than 15 minutes late
- are not expired
- are not soft-deleted
- belong to active enrollments, templates, and studies
- belong to enrolled participants

The query uses `with_for_update(skip_locked=True)` to reduce duplicate processing if multiple workers are running.

Reminders are selected by `crud.get_pings_for_reminder()`. A reminder is sent when:

- the original ping was sent
- no reminder has been sent
- `reminder_ts <= now`
- the ping has not expired
- the participant has not clicked the ping link

Telegram delivery uses `flask_app/telegram_messenger.py`, which calls the Telegram Bot HTTP API synchronously via `requests.post`.

## Message Construction And Link Forwarding

`flask_app/message_constructor.py` builds participant messages and survey URLs.

Ping template messages and URLs can include placeholders such as:

- `<PING_ID>`
- `<SCHEDULED_TIME>`
- `<EXPIRE_TIME>`
- `<DAY_NUM>`
- `<PING_TEMPLATE_NAME>`
- `<STUDY_PUBLIC_NAME>`
- `<PID>`
- `<ENROLLMENT_ID>`
- `<PR_COMPLETED>`
- `<URL>`

When sending a ping, `MessageConstructor.construct_message()` creates a frontend-visible Telegram message. If the template has a survey URL, the sent message includes an HTML link to:

`{BASE_URL}/api/ping/{ping.id}?code={ping.forwarding_code}`

That endpoint is implemented by `participant_facing.py:ping_forwarder`.

When the participant clicks:

1. Flask loads the `Ping`.
2. The `code` query parameter is checked against `Ping.forwarding_code`.
3. `first_clicked_ts` and `last_clicked_ts` are updated.
4. Enrollment `pr_completed` is recalculated.
5. `MessageConstructor.construct_survey_url()` substitutes URL placeholders into the real external survey URL.
6. Flask redirects the participant with HTTP `307`.

This forwarding layer lets the app track completion behavior while still using external survey platforms like Qualtrics or REDCap.

## Telegram Bot

The bot lives in `bot/telegram_bot.py` and uses `python-telegram-bot`.

It runs as a webhook service:

- listens on `0.0.0.0:8443`
- URL path: `/webhook`
- public webhook URL: `https://emapingbot.com/webhook`

Commands:

- `/start`: show available commands
- `/enroll`: prompt for a link code and call `/api/bot/link_telegram_id`
- `/contact`: call `/api/bot/get_contact_msgs` and return study contact messages
- `/dashboard`: call `/api/bot/participant_login` to generate and send a one-time dashboard link

The bot authenticates to Flask with the shared `X-Bot-Secret-Key` header. The bot service does not access the database directly.

## Participant Dashboard

Participants can request a dashboard link through Telegram `/dashboard`.

Flow:

1. The bot calls `POST /api/bot/participant_login` with the participant Telegram ID.
2. Flask finds all enrollments for that Telegram ID.
3. Flask generates one OTP and stores it on each enrollment.
4. Flask sends a Telegram message containing:

   `https://emapingbot.com/participant_dash?otp={otp}&t={telegram_id}`

5. The React participant dashboard calls `GET /api/participant_dashboard`.
6. Flask validates the OTP and expiry and returns enrollment/study details.

OTP expiry is controlled by `ENROLLMENT_DASHBOARD_OTP_EXPIRY_MINS`.

## Support Flow

The feedback widget posts to:

- `POST /api/support`

The endpoint:

1. Optionally accepts a JWT.
2. Verifies Google reCAPTCHA.
3. Sends an email through Mailtrap.
4. Saves a `Support` row.

If a logged-in user omits email, the endpoint uses the email from the JWT identity.

## Persistence And Soft Deletes

The application uses PostgreSQL through Flask-SQLAlchemy. There is no migration directory present in the repository scan, though `flask_migrate.Migrate` is initialized.

Soft delete behavior is common:

- `Study.deleted_at` cascades manually to enrollments, pings, templates, and user-study links in `crud.soft_delete_study`.
- `Enrollment.deleted_at` cascades manually to its pings.
- `PingTemplate.deleted_at` cascades manually to its pings.
- `UserStudy.deleted_at` removes access without deleting the user.

Because many routes use SQLAlchemy `select()` directly, deleted-row filtering is usually explicit rather than relying only on `SoftDeleteQuery`.

## Logs

Each service writes logs into mounted directories:

- `./logs/flask:/app/logs`
- `./logs/celery:/app/logs`
- `./logs/bot:/app/logs`
- `./logs/nginx:/var/log/nginx`

Logger setup is defined separately in `flask_app/logger_setup.py` and `bot/logger_setup.py`.

## Notable Implementation Details

- The frontend `AuthContext.jsx` is marked "NOT CURRENTLY USED"; auth is handled directly through localStorage and axios interceptors.
- `flask_app/blueprints/users.py` is not registered and appears incomplete.
- `flask_app/app.py` contains a `/smash_matchups` route unrelated to EMA Pingbot.
- `flask_app/extensions.py` initializes CORS twice. The second `CORS(app, resources={r"*": {"origins": []}})` may be worth reviewing.
- `MessageConstructor` builds tracked links against `/api/ping/:id`, so ping tracking depends on nginx continuing to proxy `/api/` to Flask.
- `participant_facing.py` checks `hasattr(ping, 'expiry_ts')`, but the model field is `expire_ts`; as written, the expiry check in the click forwarder likely never runs.
- `crud.update_ping()` accepts `ping_sent_ts`, but the model field is `sent_ts`; updates to sent status through that helper may not affect the intended column.
- The React enrollment dashboard calls `POST /api/studies/:studyId/enrollments`, but no matching protected route is present in `blueprints/enrollments.py` in this scan.

## End-To-End Happy Path

1. Researcher registers/logs in.
2. Researcher creates a study.
3. Researcher creates one or more ping templates with schedules.
4. Participant signs up with the study code and receives a Telegram link code.
5. Participant sends the link code to the Telegram bot via `/enroll`.
6. Flask links the Telegram ID and creates concrete scheduled pings.
7. Celery beat runs every minute and dispatches due pings through the worker.
8. The worker sends Telegram messages containing tracked forwarding links.
9. Participant clicks the link.
10. Flask records click timestamps and redirects to the external survey URL.
11. Researcher views pings, enrollments, and completion progress in the React UI.

