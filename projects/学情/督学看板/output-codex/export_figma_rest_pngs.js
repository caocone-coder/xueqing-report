#!/usr/bin/env node

const fs = require("fs");
const path = require("path");

const FILE_KEY = "woetItQ1KMfNGFziYpzxTA";
const SCALE = 2;
const OUTPUT_DIR = "/Users/a1-6/CC_project/projects/学情/督学看板/output-codex/assets";

const EXPORTS = [
  { id: "23:2221", slug: "customer-detail-body" },
  { id: "23:2469", slug: "customer-detail-topbar" },
  { id: "23:572", slug: "supervisor-dashboard-body" },
  { id: "23:805", slug: "supervisor-dashboard-top" },
  { id: "23:824", slug: "footprint-detail" },
  { id: "23:2033", slug: "report-detail-phone" },
];

function getToken() {
  const raw = fs.readFileSync("/Users/a1-6/.claude.json", "utf8");
  const parsed = JSON.parse(raw);
  return parsed.projects["/Users/a1-6"].mcpServers.figma.env.FIGMA_API_KEY;
}

async function getExportUrl(token, nodeId) {
  const endpoint =
    `https://api.figma.com/v1/images/${FILE_KEY}?ids=${encodeURIComponent(nodeId)}&format=png&scale=${SCALE}`;
  const response = await fetch(endpoint, {
    headers: {
      "X-Figma-Token": token,
    },
  });

  if (!response.ok) {
    throw new Error(`failed to get image url for ${nodeId}: ${response.status} ${response.statusText}`);
  }

  const payload = await response.json();
  const url = payload.images?.[nodeId];
  if (!url) {
    throw new Error(`missing export url for ${nodeId}`);
  }
  return url;
}

async function downloadPng(url, targetPath) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`failed to download image ${url}: ${response.status} ${response.statusText}`);
  }

  const buffer = Buffer.from(await response.arrayBuffer());
  fs.writeFileSync(targetPath, buffer);
}

async function main() {
  const token = getToken();
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  for (const item of EXPORTS) {
    const targetPath = path.join(OUTPUT_DIR, `${item.slug}.png`);
    process.stdout.write(`Exporting ${item.slug} (${item.id})...\n`);
    const url = await getExportUrl(token, item.id);
    await downloadPng(url, targetPath);
    process.stdout.write(`Saved ${targetPath}\n`);
  }
}

main().catch((error) => {
  console.error(error.message || error);
  process.exit(1);
});
