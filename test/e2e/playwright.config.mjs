import { defineConfig } from "@playwright/test";

const frontendHost = process.env.E2E_FRONTEND_HOST || "127.0.0.1";
const frontendPort = process.env.E2E_FRONTEND_PORT || "19080";
const backendHost = process.env.E2E_BACKEND_HOST || "127.0.0.1";
const backendPort = process.env.E2E_BACKEND_PORT || "19001";
const timeout = Number.parseInt(process.env.E2E_TIMEOUT_MS || "20000", 10);
const serverOutput = process.env.E2E_WEB_LOGS === "1" ? "pipe" : "ignore";

const frontendUrl = `http://${frontendHost}:${frontendPort}`;
const backendUrl = `http://${backendHost}:${backendPort}`;

export default defineConfig({
  testDir: ".",
  testMatch: ["**/*.spec.mjs", "**/*.test.mjs"],
  timeout,
  preserveOutput: "never",
  use: {
    baseURL: frontendUrl,
  },
  webServer: [
    {
      command: `cd ../.. && uv run manage.py runserver ${backendHost}:${backendPort} --noreload`,
      url: backendUrl,
      timeout: 30000,
      reuseExistingServer: false,
      stdout: serverOutput,
      stderr: serverOutput,
    },
    {
      command: `cd ../.. && BACKEND_ROOT=${backendUrl}/ FRONTEND_PORT=${frontendPort} npm run dev --prefix frontend -- --host ${frontendHost}`,
      url: frontendUrl,
      timeout: 30000,
      reuseExistingServer: false,
      stdout: serverOutput,
      stderr: serverOutput,
    },
  ],
});