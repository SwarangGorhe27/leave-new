# Attendance automation test documentation

## Quick run

### Backend only (API E2E + security + coverage)
```powershell
cd HRMS-api\backend
pytest apps/attendance/tests/test_employee_attendance_e2e.py -v --cov=apps.attendance --cov-report=xml:coverage.xml
bandit -r apps/attendance -ll
```

### Full suite (backend + frontend)
```powershell
.\scripts\run-attendance-tests.ps1 -Frontend
```

### Frontend only
```powershell
cd HRMS-web
npm install
npm run test:unit
npx playwright install chromium
npm run test:e2e
```

## SonarQube

1. Generate backend coverage:
   ```powershell
   cd HRMS-api\backend
   pytest apps/attendance/tests/test_employee_attendance_e2e.py --cov=apps.attendance --cov-report=xml:coverage.xml
   ```

2. Generate frontend coverage (optional):
   ```powershell
   cd HRMS-web
   npm run test:unit
   ```

3. Run SonarScanner from repo root:
   ```powershell
   sonar-scanner -Dproject.settings=sonar-project.properties
   ```

Required CI secrets: `SONAR_TOKEN`, `SONAR_HOST_URL`

## Test coverage

| Layer | File | What it validates |
|-------|------|-------------------|
| Backend E2E | `test_employee_attendance_e2e.py` (21 tests) | Full API journey: summary, list, calendar, punch-details, clock-in/out, regularization, analytics |
| Backend Security | same file (`@pytest.mark.security`) | 401 unauthenticated, data isolation, SQL injection, over-posting |
| Backend helpers | `conftest.py` | Tenant subscription + authenticated API client |
| Frontend Unit | `mappers.test.ts` (3 tests) | API → UI mapping, time formatting, KPI deltas |
| Frontend E2E | `e2e/employee-attendance.spec.ts` (7 tests) | Login gate, dashboard KPIs, list, punch modal, regularization, Bearer token |
| CI | `.github/workflows/attendance-ci.yml` | pytest + bandit + vitest + playwright + SonarQube |

## Markers

```powershell
pytest -m e2e          # end-to-end API flows only
pytest -m security     # security regressions only
```

## Bugs fixed while building tests

- `clock_in` / `clock_out`: removed `select_for_update()` + `select_related()` (PostgreSQL outer join error)
- `search_date`: invalid dates return HTTP 400 instead of 500
