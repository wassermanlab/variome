import { expect, test } from "@playwright/test";

test("loads the application shell", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("button").first()).toBeVisible({ timeout: 10000 });
  await expect(page.locator("body")).not.toBeEmpty();
});

const mtVariant = {
  variant: { id: 42, variant_id: "M-3243-A-G", var_type: "M", filter: "PASS" },
  mt: {
    pos: 3243, ref: "A", alt: "G",
    ucsc_url: "https://genome.ucsc.edu/cgi-bin/hgTracks?position=chrM:3243",
    mitomap_url: "https://www.mitomap.org/foswiki/bin/view/MITOMAP/MutationsRNA",
    gnomad_url: "https://gnomad.broadinstitute.org/variant/M-3243-A-G?dataset=gnomad_r3",
    dbsnp_id: null, dbsnp_url: null, clinvar_url: null, clinvar_vcv: null,
  },
  bvlFrequencies: {
    an: 100, ac_hom: 0, ac_het: 2, af_hom: "0.0000000000", af_het: "0.0200000000",
    max_hl: "0.8000000000", hl_hist: "0,2,0,0,0,0,0,0,0,0",
  },
  gnomadFrequencies: {
    an: 1000, ac_hom: 0, ac_het: 3, af_hom: "0", af_het: "0.0030000000", max_hl: "0.5",
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
    const url = new URL(route.request().url());
    const path = url.pathname.replace(/\/$/, "");
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

test("MT example loads live gnomAD frequencies and keeps the local histogram", async ({ page }) => {
  await mockMtApi(page);
  let gnomadRequests = 0;
  await page.route("https://gnomad.broadinstitute.org/api", route => {
    gnomadRequests++;
    const request = route.request().postDataJSON();
    expect(request.query).toContain("mitochondrial_variant");
    expect(request.query).toContain("dataset: gnomad_r3");
    expect(request.variables.variantId).toBe("M-3243-A-G");
    return route.fulfill({ json: { data: { mitochondrial_variant: {
      an: 2000, ac_hom: 2, ac_het: 4, max_heteroplasmy: 0.9,
    } } } });
  });
  await page.goto("/");
  await page.getByRole("link", { name: "M-3243-A-G", exact: true }).click();
  await expect(page.getByText("Mitochondrial", { exact: true })).toBeVisible();
  const table = page.getByRole("table", { name: "Mitochondrial frequencies", exact: true });
  const headers = table.locator("thead tr").first().locator("th");
  await expect(headers.nth(1)).not.toHaveCSS("background-color", "rgba(0, 0, 0, 0)");
  await expect(headers.nth(2)).toHaveCSS("background-color", "rgba(255, 188, 188, 0.25)");
  await expect(headers.nth(2)).toHaveText("gnomAD mitochondrial");
  await expect(table.getByRole("columnheader", { name: "Homoplasmic", exact: true })).toHaveCount(2);
  const count = table.getByRole("row", { name: "Allele Count 0 2 2 4", exact: true });
  await expect(count).toBeVisible();
  await expect(table.getByRole("row", { name: "Allele Frequency 0 0.02 0.001 0.002", exact: true })).toBeVisible();
  await expect(page.getByRole("img", { name: /Heteroplasmy histogram/ })).toBeVisible();
  await expect(page.getByRole("img", { name: /Heteroplasmy histogram/ })).toHaveAccessibleDescription(/0–10%: 0; 10–20%: 2/);
  await expect(page.getByRole("link", { name: "M-3243-A-G", exact: false })).toHaveAttribute("href", mtVariant.mt.gnomad_url);
  await expect(page.locator(`a[href="${mtVariant.mt.mitomap_url}"]`)).toBeVisible();
  expect(gnomadRequests).toBe(1);
});

for (const histogram of [null, "", "0,,2", "0,-1,2"]) {
  test(`MT missing frequencies and unavailable histogram (${JSON.stringify(histogram)})`, async ({ page }) => {
    await mockMtApi(page, {
      ...mtVariant,
      bvlFrequencies: { hl_hist: histogram },
      gnomadFrequencies: null,
    });
    await page.route("https://gnomad.broadinstitute.org/api", route => route.fulfill({
      json: { data: { mitochondrial_variant: null } },
    }));
    await page.goto("/");
    await page.getByRole("link", { name: "M-3243-A-G", exact: true }).click();
    const table = page.getByRole("table", { name: "Mitochondrial frequencies", exact: true });
    await expect(table.getByRole("row", { name: "Allele Count - - - -", exact: true })).toBeVisible();
    await expect(page.getByText("No heteroplasmy histogram available.")).toBeVisible();
    await expect(page.getByRole("img", { name: /Heteroplasmy histogram/ })).toHaveCount(0);
  });
}

test("MT all-zero histogram remains available", async ({ page }) => {
  await mockMtApi(page, {
    ...mtVariant,
    bvlFrequencies: { ...mtVariant.bvlFrequencies, hl_hist: "0,0,0,0,0,0,0,0,0,0", max_hl: 0 },
  });

  await page.goto("/");
  await page.getByRole("link", { name: "M-3243-A-G", exact: true }).click();
  await expect(page.getByRole("img", { name: /Heteroplasmy histogram/ })).toBeVisible();
  await expect(page.getByRole("row", { name: "Maximum heteroplasmy level 0 0.5", exact: true })).toBeVisible();
});

test("MT shows loading while live gnomAD data is pending", async ({ page }) => {
  await mockMtApi(page);
  let release;
  const pending = new Promise(resolve => { release = resolve; });
  await page.route("https://gnomad.broadinstitute.org/api", async route => {
    await pending;
    await route.fulfill({ json: { data: { mitochondrial_variant: {
      an: 200, ac_hom: 0, ac_het: 1, max_heteroplasmy: 0.8,
    } } } });
  });
  await page.goto("/variant/42");
  await expect(page.getByRole("progressbar", { name: "Loading gnomAD frequencies" })).toBeVisible();
  await expect(page.getByRole("img", { name: /Heteroplasmy histogram/ })).toBeVisible();
  release();
  await expect(page.getByRole("row", { name: "Allele Count 0 2 0 1", exact: true })).toBeVisible();
  await expect(page.getByRole("progressbar")).toHaveCount(0);
});

for (const failure of ["network", "graphql"]) {
  test(`MT reports a gnomAD ${failure} failure instead of using stored data`, async ({ page }) => {
    await mockMtApi(page);
    await page.route("https://gnomad.broadinstitute.org/api", route => {
      if (failure === "network") return route.abort();
      return route.fulfill({ json: { errors: [{ message: "gnomAD unavailable" }] } });
    });
    await page.goto("/variant/42");
    await expect(page.getByRole("alert")).toHaveText("gnomAD connection error");
    await expect(page.getByRole("row", { name: "Allele Count 0 2 - -", exact: true })).toBeVisible();
    await expect(page.getByRole("progressbar")).toHaveCount(0);
  });
}

test("MT missing live counts remain unavailable rather than becoming zero frequencies", async ({ page }) => {
  await mockMtApi(page);
  await page.route("https://gnomad.broadinstitute.org/api", route => route.fulfill({
    json: { data: { mitochondrial_variant: {
      an: 200, ac_hom: null, ac_het: null, max_heteroplasmy: null,
    } } },
  }));
  await page.goto("/variant/42");
  await expect(page.getByRole("row", { name: "Allele Frequency 0 0.02 - -", exact: true })).toBeVisible();
});

for (const varType of ["SNV", "SV", "INDEL", "S"]) {
  test(`${varType} continues using nuclear frequencies and external gnomAD`, async ({ page }) => {
    await mockMtApi(page, {
      variant: { id: 42, variant_id: "1-123-A-G", var_type: varType, filter: "PASS" },
      snv: { chr: "1", pos: 123, ref: "A", alt: "G" },
      bvlFrequencies: {
        an_tot: 100, an_xx: 50, an_xy: 50,
        ac_tot: 2, ac_xx: 1, ac_xy: 1,
        af_tot: 0.02, af_xx: 0.02, af_xy: 0.02,
        hom_tot: 0, hom_xx: 0, hom_xy: 0,
      },
      annotations: [],
    });
    let nuclearRequests = 0;
    await page.route("https://gnomad.broadinstitute.org/api", route => {
      nuclearRequests++;
      return route.fulfill({ json: { data: { variant: { joint: { ac: 1, an: 1000, homozygote_count: 0 } } } } });
    });
    await page.goto("/");
    await page.getByRole("link", { name: "M-3243-A-G", exact: true }).click();
    await expect(page.getByText("1-123-A-G (hg38)", { exact: true })).toBeVisible();
    await expect(page.getByText(varType, { exact: true })).toBeVisible();
    await expect(page.getByText("Ensembl", { exact: true })).toBeVisible();
    await expect(page.getByRole("table", { name: "simple table" })).toBeVisible();
    await expect(page.getByRole("row", { name: "Allele Count 2 1 1 1", exact: true })).toBeVisible();
    await expect(page.getByRole("table", { name: "Mitochondrial frequencies", exact: true })).toHaveCount(0);
    expect(nuclearRequests).toBe(1);
  });
}

for (const query of ["M-3243-A-G", "MT-3243-A-G", "chrMT:3,243:A:G", "chrM:3243:A:G"]) {
  test(`search normalizes mitochondrial alias ${query}`, async ({ page }) => {
    await mockMtApi(page);
    await page.route("https://rest.ensembl.org/**", route => route.fulfill({ json: { seq: "A" } }));
    const searchRequest = page.waitForRequest(request => new URL(request.url()).pathname === "/api/search");
    await page.goto(`/?q=${encodeURIComponent(query)}`);
    const request = await searchRequest;
    const parameters = new URL(request.url()).searchParams;
    expect(parameters.get("chr")).toBe("M");
    expect(parameters.get("pos")).toBe("3243");
    expect(parameters.get("ref")).toBe("A");
    expect(parameters.get("alt")).toBe("G");
    await expect(page.getByText("(Exact match)", { exact: true })).toBeVisible();
  });
}