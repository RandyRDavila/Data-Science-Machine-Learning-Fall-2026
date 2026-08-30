import { expect, test } from "@playwright/test";

test("latest-measurement journey is usable", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Scientific Measurement Monitor" })).toBeVisible();
  await expect(page.getByRole("status")).not.toHaveText("Loading…");
  await expect(page.getByRole("button", { name: "Refresh measurements" })).toBeEnabled();
});
