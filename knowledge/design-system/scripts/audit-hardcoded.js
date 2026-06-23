#!/usr/bin/env node

/**
 * Scan source files for hardcoded design values.
 *
 * Usage:
 *   node audit-hardcoded.js src
 */

const fs = require("fs");
const path = require("path");

const TARGET_EXTENSIONS = new Set([
  ".js",
  ".jsx",
  ".ts",
  ".tsx",
  ".css",
  ".scss",
  ".sass",
]);

const colorPattern = /#(?:[0-9a-fA-F]{3,8})\b|rgba?\([^)]+\)|hsla?\([^)]+\)/g;
const pxPattern = /\b\d+px\b/g;
const remPattern = /\b\d*\.?\d+rem\b/g;

function walk(dir, files = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === "node_modules" || entry.name.startsWith(".")) {
      continue;
    }

    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(fullPath, files);
      continue;
    }

    if (TARGET_EXTENSIONS.has(path.extname(entry.name))) {
      files.push(fullPath);
    }
  }

  return files;
}

function collectMatches(content, pattern, category, filePath) {
  const results = [];
  const lines = content.split(/\r?\n/);

  lines.forEach((line, index) => {
    const matches = line.match(pattern);
    if (!matches) {
      return;
    }

    for (const value of matches) {
      if (line.includes("var(--")) {
        continue;
      }

      results.push({
        category,
        value,
        line: index + 1,
        filePath,
      });
    }
  });

  return results;
}

function main() {
  const target = process.argv[2];

  if (!target) {
    console.error("Usage: node audit-hardcoded.js <directory>");
    process.exit(1);
  }

  const absoluteTarget = path.resolve(process.cwd(), target);
  const files = walk(absoluteTarget);
  const findings = [];

  for (const filePath of files) {
    const content = fs.readFileSync(filePath, "utf8");
    findings.push(...collectMatches(content, colorPattern, "color", filePath));
    findings.push(...collectMatches(content, pxPattern, "px", filePath));
    findings.push(...collectMatches(content, remPattern, "rem", filePath));
  }

  if (findings.length === 0) {
    console.log("No hardcoded design values found.");
    return;
  }

  for (const finding of findings) {
    console.log(
      `${finding.category}\t${finding.value}\t${finding.filePath}:${finding.line}`
    );
  }
}

main();
