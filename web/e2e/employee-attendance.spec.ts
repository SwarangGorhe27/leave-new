import { test, expect } from '@playwright/test';
import {
  employeeAuthStorage,
  MOCK_LIST,
  MOCK_PUNCH_DETAILS,
  MOCK_SUMMARY,
} from './fixtures/attendance-api.mock';

async function seedAuthAndMocks(page: import('@playwright/test').Page) {
  const storage = employeeAuthStorage();
  await page.addInitScript((entries) => {
    for (const [key, value] of Object.entries(entries)) {
      localStorage.setItem(key, value as string);
    }
  }, storage);

  await page.route(/\/api\/employee\/attendance/, (route) => {
    const url = route.request().url();
    if (url.includes('/summary')) {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_SUMMARY),
      });
    }
    if (url.includes('/list')) {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_LIST),
      });
    }
    if (url.includes('/punch-details')) {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_PUNCH_DETAILS),
      });
    }
    if (route.request().method() === 'GET') {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, data: {}, errors: null }),
      });
    }
    return route.continue();
  });
}

async function openAttendancePage(page: import('@playwright/test').Page) {
  await page.goto('/employee/attendance');
  await expect(page.getByRole('heading', { name: 'My Attendance' })).toBeVisible({ timeout: 15_000 });
  await expect(page.getByText('Loading attendance…')).toHaveCount(0, { timeout: 15_000 });
}

test.describe('Employee Attendance E2E', () => {
  test.beforeEach(async ({ page }) => {
    await seedAuthAndMocks(page);
  });

  test('loads My Attendance dashboard with summary KPIs', async ({ page }) => {
    await openAttendancePage(page);
    await expect(page.getByText('Avg Work Hours')).toBeVisible();
    await expect(page.getByText('7.9h')).toBeVisible();
    await expect(page.getByText('Present Days')).toBeVisible();
  });

  test('calendar view shows attendance records', async ({ page }) => {
    await openAttendancePage(page);
    await expect(page.getByRole('button', { name: /calendar/i })).toBeVisible();
    await expect(page.getByText('Performance Analytics')).toBeVisible();
  });

  test('list view displays timing columns', async ({ page }) => {
    await openAttendancePage(page);
    await page.getByRole('button', { name: /^list$/i }).click();
    await expect(page.getByText('09:05 AM')).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText('Present').first()).toBeVisible();
  });

  test('punch details modal opens from list row', async ({ page }) => {
    await openAttendancePage(page);
    await page.getByRole('button', { name: /^list$/i }).click();
    await page.getByText('07 May, 2026').click();
    await expect(page.getByText('Daily Attendance Punch Details')).toBeVisible();
    await expect(page.getByText('Main Entrance')).toBeVisible();
    await expect(page.getByText('Main Gate Exit')).toBeVisible();
  });

  test('regularization tab renders date selection prompt', async ({ page }) => {
    await openAttendancePage(page);
    await page.getByRole('button', { name: /regularization/i }).click();
    await expect(page.getByText('Select dates')).toBeVisible();
    await expect(page.getByText(/click dates that need regularization/i)).toBeVisible();
  });

  test('redirects unauthenticated users to login', async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.clear();
    });
    await page.goto('/employee/attendance');
    await expect(page).toHaveURL(/\/login/);
  });
});

test.describe('Employee Attendance Security E2E', () => {
  test('API calls include Authorization header when token present', async ({ page }) => {
    await seedAuthAndMocks(page);

    const seenAuth: string[] = [];
    await page.route(/\/api\/employee\/attendance/, (route) => {
      seenAuth.push(route.request().headers()['authorization'] ?? '');
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(MOCK_SUMMARY),
      });
    });

    await openAttendancePage(page);
    expect(seenAuth.some((h) => h.startsWith('Bearer '))).toBeTruthy();
  });
});
