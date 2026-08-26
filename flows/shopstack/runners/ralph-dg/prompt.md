# Discount Genie — Workspace Context

You are working inside a sub-repo nested within the `discount-genie-core/`
orchestration repo. The sub-repo has its own git history — your commits land
here, not in the parent.

## Workspace topology

```
discount-genie-core/          ← orchestration (issues tracked here)
├── discount-genie-backend/   ← FastAPI backend (Python, Docker, PostgreSQL)
└── discount-genie/           ← Remix frontend (TypeScript, Shopify embedded)
```

## Issue tracker

All issues are on `shopstackio/discount-genie-core`. For every `gh issue`
command, use `--repo shopstackio/discount-genie-core`:

```bash
gh issue close <N> --repo shopstackio/discount-genie-core --comment "Done: ..."
gh issue comment <N> --repo shopstackio/discount-genie-core --body "..."
gh issue edit <N> --repo shopstackio/discount-genie-core --add-label ready-for-agent
```

Do not use `--repo shopstackio/discount-genie-backend` or
`--repo shopstackio/discount-genie` — those repos do not have the issue queue.

`gh` commands work as-is — account routing is handled by the runner. Do not add
`GH_CONFIG_DIR` or `GH_HOST` prefixes.

## Branch discipline

You MUST be on a `feature/*` branch. Never commit to `main`, `develop`, or
`staging` — they trigger automated deploys.

If you discover you are on a protected branch, STOP and output:
```
<promise>WRONG BRANCH — cannot commit to [branch name]</promise>
```

## Test commands

**Frontend (discount-genie):** Always use `--run` to disable watch mode.
Without `--run`, vitest enters watch mode which hangs when piped.
```bash
npm test -- --run --reporter=verbose <pattern>
```
Never run multiple `npm test` commands in parallel — vitest instances
deadlock on shared resources. Run tests sequentially.

**Backend (discount-genie-backend):** Tests run inside Docker:
```bash
docker compose -f docker-compose.test-main.yaml run --rm test-runner sh -c "pytest app/tests/ -v --tb=short"
```

## Cross-repo architecture

The two sub-repos are tightly coupled. Understanding their contract prevents
breaking changes.

**Authentication chain:**
Frontend signs a custom JWT (jose, HS256, `SHOPIFY_API_SECRET`) → Backend
verifies the same JWT → extracts `dest` claim → resolves tenant via Session →
Configuration. `SHOPIFY_API_SECRET` must be identical in both `.env` files.

**API client contract:**
The frontend calls the backend via an auto-generated typed client built from the
backend's OpenAPI spec (`npm run generate-client` in the frontend repo, backend
must be running). Output: `app/server/clients/discountGenie/`. When a backend PR
adds or changes an endpoint, the frontend must regenerate the client.

**Tenant key:** `configuration_id` (not `shop_id` — that doesn't exist).

## AFK commit reminder

You are running autonomously — no human will respond. When your work is done
(tests pass, lint clean), commit and close the issue immediately. Never output
"want me to commit?", "ready when you are", or any other confirmation prompt.
Stage the files, `git commit`, then `gh issue close`.

## Klaviyo OAuth

Feature-gated by `KLAVIYO_OAUTH_ENABLED` (defaults to `false` — all endpoints
return 503 when disabled).

**Flow:** Frontend Settings page → `POST /oauth/start` → Redis state + Klaviyo
auth URL → user authorizes → `GET /oauth/callback` (public, no JWT) → token
exchange → Fernet-encrypted storage in `KlaviyoIntegration` table → redirect to
Settings. Disconnect: `DELETE /connection` → revoke + clear.

**OAuth callback resolves tenant via Redis state store**, not JWT. Uses
`get_multi_by_shop()` and handles 0/1/>1 session rows per the session uniqueness
invariant.

**Backend env vars required:** `KLAVIYO_OAUTH_ENABLED`, `KLAVIYO_CLIENT_ID`,
`KLAVIYO_CLIENT_SECRET`, `KLAVIYO_ENCRYPTION_KEY` (Fernet), `KLAVIYO_REDIRECT_URI`,
`APP_HANDLE`, `FRONTEND_URL`. See core CLAUDE.md for full setup instructions.
