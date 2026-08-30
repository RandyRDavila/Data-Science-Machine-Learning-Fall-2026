import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: ".",
  use: {
    baseURL: process.env.E2E_BASE_URL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "desktop-chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "android-chromium", use: { ...devices["Pixel 7"] } },
    { name: "ios-webkit", use: { ...devices["iPhone 15"] } },
  ],
});
