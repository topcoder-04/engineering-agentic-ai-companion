import { execFileSync } from "node:child_process";
import { mkdirSync, readdirSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const playwrightModule =
  process.env.PLAYWRIGHT_MODULE || "playwright";
const { chromium } = require(playwrightModule);

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "..");
const html = join(root, "docs", "miras-journey-film.html");
const output = resolve(
  process.argv[2] || join(root, "artifacts", "miras-journey-video.mp4"),
);
const rawDir = resolve(process.env.RUNNER_TEMP || "/tmp", "mira-journey-raw");
const width = 1920;
const height = 1080;
const fps = 30;
const durationMs = 558_833;

mkdirSync(dirname(output), { recursive: true });
mkdirSync(rawDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width, height },
  deviceScaleFactor: 1,
  recordVideo: {
    dir: rawDir,
    size: { width, height },
  },
});

const pageCreatedAt = Date.now();
const page = await context.newPage();
const source = `${pathToFileURL(html).href}?autoplay=0`;
await page.goto(source, { waitUntil: "load" });
await page.waitForFunction(() => {
  return window.MIRA_FILM?.durationMs === 558833 &&
    document.querySelector(".scene.opening")?.classList.contains("active");
});

const preRollSeconds = Math.max(0, (Date.now() - pageCreatedAt) / 1000);
await page.evaluate(() => window.MIRA_FILM.start());
await page.waitForTimeout(durationMs + 750);

await context.close();
await browser.close();

const rawVideo = readdirSync(rawDir)
  .filter(name => name.endsWith(".webm"))
  .map(name => join(rawDir, name))[0];

if (!rawVideo) {
  throw new Error("Playwright did not produce a WebM recording.");
}

execFileSync(
  "ffmpeg",
  [
    "-y",
    "-hide_banner",
    "-loglevel",
    "error",
    "-ss",
    preRollSeconds.toFixed(3),
    "-i",
    rawVideo,
    "-t",
    (durationMs / 1000).toFixed(3),
    "-vf",
    `fps=${fps},scale=${width}:${height}:flags=lanczos`,
    "-an",
    "-c:v",
    "libx264",
    "-preset",
    "medium",
    "-crf",
    "18",
    "-pix_fmt",
    "yuv420p",
    "-movflags",
    "+faststart",
    output,
  ],
  { stdio: "inherit" },
);

const probe = execFileSync(
  "ffprobe",
  [
    "-v",
    "error",
    "-show_entries",
    "format=duration:stream=codec_name,width,height,r_frame_rate",
    "-of",
    "json",
    output,
  ],
  { encoding: "utf8" },
);

console.log(probe);
console.log(`Rendered ${output}`);
