# 🚀 EduCore Deployment Checklist

Follow these steps to complete **Step 17 (Staging)** and move to **Step 18 (Production)**.

## 1. 🏗️ Backend Setup (Railway)
Create a new project on [Railway.app](https://railway.app) and connect your GitHub repo.

### 🔌 Add Services
1. **PostgreSQL**: Add a PostgreSQL database.
2. **Redis**: Add a Redis instance.
3. **API Service**: Connect the repo, set root directory to `backend`, use `Dockerfile`.
4. **Worker Service**: Connect the repo, set root directory to `backend`, override Dockerfile to `Dockerfile.worker`.
5. **Beat Service**: Connect the repo, set root directory to `backend`, override Dockerfile to `Dockerfile.beat`.

### 🔑 Required Environment Variables (API + Workers)
Add these in the Railway "Variables" tab:

| Variable | Recommended Value |
| :--- | :--- |
| `APP_NAME` | `EduCore Platform` |
| `APP_ENV` | `staging` |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` |
| `SECRET_KEY` | `(Generate a long 32+ char random string)`|
| `JWT_ALGORITHM` | `HS256` |
| `PII_ENCRYPTION_KEY` | `(Generate a 32-byte base64 key)` |
| `ALLOWED_ORIGINS` | `https://your-vercel-domain.com,http://localhost:5173` |

## 2. 🎨 Frontend Setup (Vercel)
Connect your GitHub repo to [Vercel](https://vercel.com).

### 🔑 Environment Variables
| Variable | Value |
| :--- | :--- |
| `VITE_API_BASE_URL` | `https://your-railway-api-url.up.railway.app` |

---

## 3. 🛡️ Verification Steps
Once both are deployed:
1. [ ] Check health endpoint: `https://.../api/v1/system/health`
2. [ ] Run DB migrations: `railway run alembic upgrade head` (from your local machine)
3. [ ] Verify SSL is active on both URLs.
4. [ ] Try to login via the frontend.

---

## 🛠️ Automation Status
- ✅ `railway.toml` created.
- ✅ Production Dockerfiles created.
- ✅ CI Pipeline (`ci.yml`) is active.

**Next Step**: Push these changes to GitHub to trigger the first build.
```bash
git checkout -b deployment-setup
git add .
git commit -m "chore: add deployment configuration for Railway"
git push origin deployment-setup
```
