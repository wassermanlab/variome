import { expect, test } from "@playwright/test";

test("loads the application shell", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("button").first()).toBeVisible({ timeout: 10000 });
  await expect(page.locator("body")).not.toBeEmpty();
});