#!/usr/bin/env node
/**
 * odoo-review — npm wrapper for odoo-best-practices Python CLI.
 *
 * Usage:
 *   npx @foxpink-dev/odoo-best-practices --init [ide]
 *   npx @foxpink-dev/odoo-best-practices /path/to/addon [--format json] [--check]
 *
 * Requires Python 3.6+ with odoo-best-practices installed (pip install odoo-best-practices)
 * or running from the local checkout.
 */

const { spawnSync } = require("child_process");
const path = require("path");
const fs = require("fs");

// Find the odoo-review Python entry point
const projectRoot = path.resolve(__dirname, "..");
const localCli = path.join(projectRoot, "analyzer", "cli.py");
const pipCli = "odoo-review";

function findPython() {
  const candidates = ["python3", "python"];
  for (const cmd of candidates) {
    try {
      const r = spawnSync(cmd, ["--version"], { stdio: "pipe" });
      if (r.status === 0) return cmd;
    } catch (_) {}
  }
  return null;
}

function main() {
  const args = process.argv.slice(2);

  // If --init, try local module first (for dev), then pip-installed CLI
  if (args.includes("--init")) {
    const python = findPython();
    if (!python) {
      console.error("Error: Python 3 is required but not found in PATH.");
      process.exit(1);
    }
    const result = spawnSync(python, ["-m", "analyzer.cli", ...args], {
      cwd: projectRoot,
      stdio: "inherit",
      env: { ...process.env, PYTHONPATH: projectRoot },
    });
    process.exit(result.status ?? 1);
  }

  // For non-init commands, try pip-installed CLI first
  const result = spawnSync(pipCli, args, {
    stdio: "inherit",
    shell: true,
  });

  if (result.error) {
    // Fall back to local
    const python = findPython();
    if (!python) {
      console.error("Error: Python 3 is required but not found in PATH.");
      process.exit(1);
    }
    const fallback = spawnSync(python, ["-m", "analyzer.cli", ...args], {
      cwd: projectRoot,
      stdio: "inherit",
      env: { ...process.env, PYTHONPATH: projectRoot },
    });
    process.exit(fallback.status ?? 1);
  }

  process.exit(result.status ?? 1);
}

main();
