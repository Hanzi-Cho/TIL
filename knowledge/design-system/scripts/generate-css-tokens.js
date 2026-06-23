#!/usr/bin/env node

/**
 * Convert a token JSON file into CSS custom properties.
 *
 * Usage:
 *   node generate-css-tokens.js tokens.json > variables.css
 */

const fs = require("fs");
const path = require("path");

function flattenTokens(input, prefix = [], output = []) {
  if (input && typeof input === "object" && !Array.isArray(input)) {
    for (const [key, value] of Object.entries(input)) {
      flattenTokens(value, [...prefix, key], output);
    }
    return output;
  }

  output.push([prefix.join("-"), String(input)]);
  return output;
}

function toCssVarName(name) {
  return `--${name.replace(/[^a-zA-Z0-9-]/g, "-").toLowerCase()}`;
}

function main() {
  const inputPath = process.argv[2];

  if (!inputPath) {
    console.error("Usage: node generate-css-tokens.js <tokens.json>");
    process.exit(1);
  }

  const absolutePath = path.resolve(process.cwd(), inputPath);
  const source = fs.readFileSync(absolutePath, "utf8");
  const json = JSON.parse(source);
  const entries = flattenTokens(json);

  console.log(":root {");
  for (const [name, value] of entries) {
    console.log(`  ${toCssVarName(name)}: ${value};`);
  }
  console.log("}");
}

main();
