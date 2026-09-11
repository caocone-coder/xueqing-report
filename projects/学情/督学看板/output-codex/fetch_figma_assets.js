#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

const WORKDIR = "/Users/a1-6";
const OUTPUT_ROOT = "/Users/a1-6/CC_project/projects/学情/督学看板/output-codex";
const ASSETS_DIR = path.join(OUTPUT_ROOT, "assets");
const METADATA_DIR = path.join(OUTPUT_ROOT, "metadata");
const FILE_KEY = "woetItQ1KMfNGFziYpzxTA";

const NODES = [
  { id: "23:2220", slug: "customer-detail" },
  { id: "23:2221", slug: "customer-detail-body" },
  { id: "23:2469", slug: "customer-detail-topbar" },
  { id: "23:571", slug: "supervisor-dashboard" },
  { id: "23:572", slug: "supervisor-dashboard-body" },
  { id: "23:805", slug: "supervisor-dashboard-top" },
  { id: "23:824", slug: "footprint-detail" },
  { id: "23:2032", slug: "report-detail" },
  { id: "23:2033", slug: "report-detail-phone" },
];

fs.mkdirSync(ASSETS_DIR, { recursive: true });
fs.mkdirSync(METADATA_DIR, { recursive: true });

function runCodexForNode(node) {
  const prompt =
    `Use the figma MCP server. For Figma file ${FILE_KEY} and node ${node.id}, ` +
    `call get_metadata and get_screenshot. After the tool calls, reply with exactly the word done.`;

  return new Promise((resolve, reject) => {
    const child = spawn(
      "codex",
      [
        "exec",
        "--ephemeral",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--json",
        "-C",
        WORKDIR,
        prompt,
      ],
      {
        cwd: WORKDIR,
        stdio: ["ignore", "pipe", "pipe"],
      }
    );

    let stdoutBuffer = "";
    let stderrBuffer = "";
    let screenshot = null;
    let metadata = null;

    function maybeHandleLine(line) {
      const trimmed = line.trim();
      if (!trimmed.startsWith("{")) {
        return;
      }

      let event;
      try {
        event = JSON.parse(trimmed);
      } catch {
        return;
      }

      if (event.type !== "item.completed" || event.item?.type !== "mcp_tool_call") {
        return;
      }

      if (event.item.tool === "get_screenshot") {
        const imageContent = (event.item.result?.content || []).find(
          (entry) => entry.type === "image" && entry.data
        );
        if (imageContent) {
          screenshot = imageContent;
        }
      }

      if (event.item.tool === "get_metadata") {
        metadata = event.item.result || null;
      }
    }

    function flushLines(finalFlush = false) {
      const parts = stdoutBuffer.split("\n");
      stdoutBuffer = finalFlush ? "" : parts.pop() || "";
      for (const part of parts) {
        maybeHandleLine(part);
      }
      if (finalFlush && stdoutBuffer) {
        maybeHandleLine(stdoutBuffer);
      }
    }

    child.stdout.on("data", (chunk) => {
      stdoutBuffer += chunk.toString("utf8");
      flushLines(false);
    });

    child.stderr.on("data", (chunk) => {
      stderrBuffer += chunk.toString("utf8");
    });

    child.on("error", reject);

    child.on("close", (code) => {
      flushLines(true);

      if (code !== 0) {
        reject(
          new Error(
            `codex exec failed for ${node.id} (${node.slug}) with exit code ${code}\n${stderrBuffer}`
          )
        );
        return;
      }

      if (!screenshot || !metadata) {
        reject(
          new Error(
            `missing screenshot or metadata for ${node.id} (${node.slug})`
          )
        );
        return;
      }

      const extension = screenshot.mimeType === "image/png" ? "png" : "bin";
      const assetPath = path.join(ASSETS_DIR, `${node.slug}.${extension}`);
      const metadataPath = path.join(METADATA_DIR, `${node.slug}.json`);

      fs.writeFileSync(assetPath, Buffer.from(screenshot.data, "base64"));
      fs.writeFileSync(
        metadataPath,
        JSON.stringify(
          {
            fileKey: FILE_KEY,
            nodeId: node.id,
            slug: node.slug,
            result: metadata,
          },
          null,
          2
        )
      );

      resolve({ assetPath, metadataPath });
    });
  });
}

async function main() {
  for (const node of NODES) {
    const assetPath = path.join(ASSETS_DIR, `${node.slug}.png`);
    const metadataPath = path.join(METADATA_DIR, `${node.slug}.json`);
    if (fs.existsSync(assetPath) && fs.existsSync(metadataPath)) {
      process.stdout.write(`Skipping ${node.slug} (${node.id})...\n`);
      continue;
    }

    process.stdout.write(`Fetching ${node.slug} (${node.id})...\n`);
    const result = await runCodexForNode(node);
    process.stdout.write(`Saved ${result.assetPath}\n`);
    process.stdout.write(`Saved ${result.metadataPath}\n`);
  }
}

main().catch((error) => {
  console.error(error.message || error);
  process.exit(1);
});
