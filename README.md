# ☁️ Cloud Resume Challenge — Complete Project

> Researched from real GitHub repos of candidates hired at AWS, TCS, Infosys & Accenture.
> All 14 files · all 16 challenge steps · every file a recruiter will check.

## Architecture

```
Browser → Route 53 → CloudFront → S3 (HTML/CSS/JS)
                                   ↓
                          counter.js → API Gateway → Lambda → DynamoDB
```

## All 14 Files → 16 Challenge Steps

| File | Challenge Step |
|------|---------------|
| `frontend/index.html` | Step 2 — HTML |
| `frontend/style.css` | Step 3 — CSS |
| `frontend/counter.js` | Step 7 — JavaScript |
| `backend/lambda/lambda_function.py` | Step 10 — Python (boto3) |
| `backend/tests/test_lambda.py` | Step 11 — **5 unit tests** (pytest + moto) |
| `backend/requirements.txt` | Step 11 — dependencies |
| `infrastructure/modules/static-site/main.tf` | Steps 4,5,6 — S3 + CloudFront + Route 53 + ACM |
| `infrastructure/modules/api-backend/main.tf` | Steps 8,9,12 — DynamoDB + Lambda + API Gateway |
| `infrastructure/modules/oidc/main.tf` | Step 14 — OIDC (no long-lived keys) |
| `infrastructure/environments/dev/main.tf` | Step 12 — IaC root (Terraform modules) |
| `.github/workflows/frontend.yml` | Steps 13,14 — CI/CD frontend pipeline |
| `.github/workflows/backend.yml` | Steps 13,14 — CI/CD backend pipeline |
| `scripts/bootstrap-tfstate.sh` | Step 13 — remote state bootstrap |
| `README.md` | Step 16 — blog/documentation |

## Top Differentiators (what got candidates hired)

- ✅ **OIDC authentication** — no long-lived AWS keys stored in GitHub
- ✅ **Terraform remote state** in S3 with DynamoDB locking
- ✅ **5 unit tests** using pytest + moto (mock AWS — no real calls)
- ✅ **Two separate CI/CD pipelines** — one for frontend, one for backend
- ✅ **Terraform modules** — reusable, not a single flat file

## Quick Start

### 1. Bootstrap remote state (run once)
```bash
chmod +x scripts/bootstrap-tfstate.sh
./scripts/bootstrap-tfstate.sh
```

### 2. Update variables
Edit `infrastructure/environments/dev/main.tf`:
- Replace `ACCOUNT_ID` in the backend bucket name
- Set `domain_name` and `root_domain` variables

### 3. Set GitHub secrets
| Secret | Value |
|--------|-------|
| `AWS_OIDC_ROLE_ARN` | Output of `terraform output github_actions_role_arn` |
| `S3_BUCKET_NAME` | Output of `terraform output s3_bucket` |
| `CLOUDFRONT_DIST_ID` | Output of `terraform output cloudfront_id` |
| `DOMAIN_NAME` | Your resume domain |
| `ROOT_DOMAIN` | Your root domain |

### 4. Update counter.js
Replace `API_URL` in `frontend/counter.js` with the output of `terraform output api_endpoint`.

### 5. Run tests locally
```bash
pip install -r backend/requirements.txt
pytest backend/tests/test_lambda.py -v
```

### 6. Deploy
Push to `main` — GitHub Actions handles the rest.

---
*Cloud Resume Challenge — [cloudresumechallenge.dev](https://cloudresumechallenge.dev)*
