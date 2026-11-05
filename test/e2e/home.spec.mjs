import { expect, test } from "@playwright/test";

test("loads the application shell", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("button").first()).toBeVisible({ timeout: 10000 });
});

const mtVariant = {
  variant: { id: 42, variant_id: "M-3243-A-G", var_type: "M", filter: "PASS" },
  mt: { pos: 3243, ref: "A", alt: "G" },
  bvlFrequencies: {
    an: 100, ac_hom: 0, ac_het: 2, af_hom: 0, af_het: 0.02,
    max_hl: 0.8, hl_hist: "0,2,0,0,0,0,0,0,0,0",
  },
  annotations: [],
};

async function mockMtApi(page, variant = mtVariant) {
  await page.route("https://gnomad.broadinstitute.org/api", route => route.fulfill({
    json: { data: { mitochondrial_variant: {
      an: 1000, ac_hom: 0, ac_het: 3, max_heteroplasmy: 0.5,
    } } },
  }));
  await page.route("**/api/**", async route => {
    const path = new URL(route.request().url()).pathname.replace(/\/$/, "");
    let response = {};
    if (path.endsWith("/settings")) {
      response = { settings: { example_mt: { id: 42, var_id: "M-3243-A-G" } } };
    } else if (path.endsWith("/user")) {
      response = { user: { email: "e2e@example.org" } };
    } else if (path.endsWith("/variant/42")) {
      response = variant;
    } else if (path.endsWith("/search")) {
      response = { results: { position: [{
        ...mtVariant.variant, snv__chr: "M", snv__pos: 3243, snv__ref: "A", snv__alt: "G",
      }] } };
    }
    await route.fulfill({ json: response });
  });
}

test("MT loads live gnomAD frequencies alongside the local histogram", async ({ page }) => {
  await mockMtApi(page);
  await page.goto("/variant/42");
  await expect(page.getByRole("row", { name: "Allele Count 0 2 0 3", exact: true })).toBeVisible();
  await expect(page.getByRole("row", { name: "Allele Frequency 0 0.02 0 0.003", exact: true })).toBeVisible();
  await expect(page.getByRole("img", { name: /Heteroplasmy histogram/ })).toBeVisible();
});

test("MT reports gnomAD failure without hiding local data", async ({ page }) => {
  await mockMtApi(page);
  await page.route("https://gnomad.broadinstitute.org/api", route => route.abort());
  await page.goto("/variant/42");
  await expect(page.getByRole("alert")).toHaveText("gnomAD connection error");
  await expect(page.getByRole("row", { name: "Allele Count 0 2 - -", exact: true })).toBeVisible();
});

test("SNV continues using nuclear frequencies and external gnomAD", async ({ page }) => {
  await mockMtApi(page, {
    variant: { id: 42, variant_id: "1-123-A-G", var_type: "SNV", filter: "PASS" },
    snv: { chr: "1", pos: 123, ref: "A", alt: "G" },
    bvlFrequencies: {
      an_tot: 100, an_xx: 50, an_xy: 50,
      ac_tot: 2, ac_xx: 1, ac_xy: 1,
      af_tot: 0.02, af_xx: 0.02, af_xy: 0.02,
      hom_tot: 0, hom_xx: 0, hom_xy: 0,
    },
    annotations: [],
  });
  await page.route("https://gnomad.broadinstitute.org/api", route => route.fulfill({
    json: { data: { variant: { joint: { ac: 1, an: 1000, homozygote_count: 0 } } } },
  }));
  await page.goto("/variant/42");
  await expect(page.getByRole("row", { name: "Allele Count 2 1 1 1", exact: true })).toBeVisible();
});

test("search normalizes mitochondrial coordinates and highlights an exact match", async ({ page }) => {
  await mockMtApi(page);
  await page.route("https://rest.ensembl.org/**", route => route.fulfill({ json: { seq: "A" } }));
  const searchRequest = page.waitForRequest(request => new URL(request.url()).pathname === "/api/search");
  await page.goto(`/?q=${encodeURIComponent("chrMT:3,243:A:G")}`);
  const parameters = new URL((await searchRequest).url()).searchParams;
  expect(parameters.get("chr")).toBe("M");
  expect(parameters.get("pos")).toBe("3243");
  await expect(page.getByText("(Exact match)", { exact: true })).toBeVisible();
});
