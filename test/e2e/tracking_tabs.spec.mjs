import { readFile } from "node:fs/promises";
import { expect, test } from "@playwright/test";
import { transformWithOxc } from "../../frontend/node_modules/vite/dist/node/index.js";

const dashboardSource = await readFile(
  new URL("../../variome_backend/library_access/static/tracking_dashboard.js", import.meta.url),
  "utf8"
);
const dashboardScript = await transformWithOxc(dashboardSource, "tracking_dashboard.jsx", {
  jsx: { runtime: "classic" }
});

test.beforeEach(async ({ page }) => {
  await page.route("http://127.0.0.1/tracking/**", route => route.fulfill({
    contentType: "text/html",
    body: `
      <button role="tab" id="variant-tab" aria-selected="true">Variant views</button>
      <button role="tab" id="search-tab" aria-selected="false">Search queries</button>
      <section id="variant-tracking">
        <form method="get">
          <input type="hidden" name="tab" id="tracking-tab" value="variant">
          <input name="start" value="2026-10-01">
          <input name="end" value="2026-10-31">
          <button type="submit">Apply Filters</button>
        </form>
      </section>
      <section id="search-tracking" hidden>
        <div id="search-query-root" data-url="/tracking/searches/">Search analytics</div>
      </section>
      <script>
        window.searchMounts = 0;
        window.React = { useState() {}, createElement() {} };
        window.ReactDOM = { createRoot() {
          window.searchMounts++;
          return { render() {} };
        }};
        ${dashboardScript.code}
      </script>
    `
  }));
});

test("restores search deep links, preserves other parameters, and supports history", async ({ page }) => {
  await page.goto("http://127.0.0.1/tracking/?tab=search&start=2026-10-01&user=1&user=2#details");
  const search = page.getByRole("tab", { name: "Search queries" });
  const variant = page.getByRole("tab", { name: "Variant views" });
  await expect(search).toHaveAttribute("aria-selected", "true");
  await expect(page.locator("#search-tracking")).toBeVisible();
  await expect(page.locator("#variant-tracking")).toBeHidden();
  await expect(page.locator("#tracking-tab")).toHaveValue("search");
  await expect.poll(() => page.evaluate(() => window.searchMounts)).toBe(1);

  await variant.click();
  await expect(page).toHaveURL(/tab=variant/);
  const url = new URL(page.url());
  expect(url.searchParams.get("start")).toBe("2026-10-01");
  expect(url.searchParams.getAll("user")).toEqual(["1", "2"]);
  expect(url.hash).toBe("#details");
  await page.goBack();
  await expect(search).toHaveAttribute("aria-selected", "true");
  await page.goForward();
  await expect(variant).toHaveAttribute("aria-selected", "true");
  await search.click();
  await expect.poll(() => page.evaluate(() => window.searchMounts)).toBe(1);
  await page.reload();
  await expect(search).toHaveAttribute("aria-selected", "true");
});

test("defaults to variant for missing or unknown tab values", async ({ page }) => {
  for (const query of ["", "?tab=unknown", "?tab=variant"]) {
    await page.goto(`http://127.0.0.1/tracking/${query}`);
    await expect(page.getByRole("tab", { name: "Variant views" })).toHaveAttribute("aria-selected", "true");
    await expect(page.locator("#variant-tracking")).toBeVisible();
    await expect(page.locator("#search-tracking")).toBeHidden();
    expect(await page.evaluate(() => window.searchMounts)).toBe(0);
  }
});

test("keyboard tab selection updates the URL without duplicate history entries", async ({ page }) => {
  await page.goto("http://127.0.0.1/tracking/?tab=variant");
  const variant = page.getByRole("tab", { name: "Variant views" });
  const search = page.getByRole("tab", { name: "Search queries" });
  await variant.focus();
  await page.keyboard.press("End");
  await expect(page).toHaveURL(/tab=search/);
  await expect(search).toBeFocused();
  await expect(search).toHaveAttribute("tabindex", "0");
  const historyLength = await page.evaluate(() => history.length);
  await search.click();
  expect(await page.evaluate(() => history.length)).toBe(historyLength);
  await page.keyboard.press("Home");
  await expect(page).toHaveURL(/tab=variant/);
});

test("variant filter submissions preserve the active tab", async ({ page }) => {
  await page.goto("http://127.0.0.1/tracking/?tab=search");
  await page.getByRole("tab", { name: "Variant views" }).click();
  await page.getByRole("button", { name: "Apply Filters" }).click();
  await expect(page).toHaveURL(/tab=variant/);
  expect(new URL(page.url()).searchParams.get("start")).toBe("2026-10-01");
  await expect(page.getByRole("tab", { name: "Variant views" })).toHaveAttribute("aria-selected", "true");
});
