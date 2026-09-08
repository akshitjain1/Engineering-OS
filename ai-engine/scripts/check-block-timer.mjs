/* -------------------------------------------------------------------------
 * Behaviour checks for the block stopwatch.
 *
 * There is no test runner in this package, and the stopwatch rules are the
 * kind that look obviously right and are obviously wrong in use: the previous
 * version discarded any open window older than 15 seconds, on the theory that
 * the tab must have died. It had not died. Opening the recall queue from the
 * Recall block silently threw the time away, which is the one thing a
 * stopwatch must never do.
 *
 * Run:
 *     npm run check:timer
 * ---------------------------------------------------------------------- */

import { execFileSync } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const out = mkdtempSync(join(tmpdir(), "eos-timer-"));
let failures = 0;

function check(name, condition, detail = "") {
  if (condition) {
    console.log(`  ok   ${name}`);
  } else {
    failures += 1;
    console.log(`  FAIL ${name}${detail ? ` — ${detail}` : ""}`);
  }
}

try {
  // Invoke the compiler through node rather than the `npx` shim: on Windows
  // that shim is a .cmd file, which execFileSync cannot spawn without a shell.
  execFileSync(
    process.execPath,
    [
      join("node_modules", "typescript", "bin", "tsc"),
      "src/lib/block-timer.ts",
      "--outDir",
      out,
      "--module",
      "es2020",
      "--target",
      "es2020",
      "--moduleResolution",
      "bundler",
    ],
    { stdio: "inherit" },
  );

  const {
    LONG_RUN_WARN_S,
    elapsedOf,
    isRunning,
    looksLeftRunning,
    parseRecord,
    pause,
    resume,
  } = await import(pathToFileURL(join(out, "block-timer.js")).href);

  const now = 1_000_000_000_000;
  const stored = (accumulated, sinceMsAgo) =>
    JSON.stringify({ accumulated, runningSince: now - sinceMsAgo });

  console.log("\na running stopwatch survives leaving the page");
  const afterNav = parseRecord(stored(30, 10 * 60 * 1000), now);
  check("still running after ten minutes away", isRunning(afterNav));
  check(
    "the ten minutes away are counted",
    Math.round(elapsedOf(afterNav, now)) === 630,
    `got ${Math.round(elapsedOf(afterNav, now))}s, wanted 630s`,
  );

  const afterHours = parseRecord(stored(0, 3 * 60 * 60 * 1000), now);
  check("still running after three hours", isRunning(afterHours));
  check("three hours are counted", Math.round(elapsedOf(afterHours, now)) === 10_800);
  check("three hours is not flagged as forgotten", !looksLeftRunning(afterHours, now));

  console.log("\na stopwatch left on overnight is counted, and said out loud");
  const overnight = parseRecord(stored(0, 9 * 60 * 60 * 1000), now);
  check("nine hours are not discarded", Math.round(elapsedOf(overnight, now)) === 32_400);
  check("nine hours is flagged", looksLeftRunning(overnight, now));
  check("the threshold is four hours", LONG_RUN_WARN_S === 4 * 60 * 60);

  console.log("\nonly a deliberate pause stops it");
  const paused = pause(afterNav, now);
  check("pause stops it", !isRunning(paused));
  check("pause banks what had accrued", Math.round(elapsedOf(paused, now + 60_000)) === 630);
  check(
    "a paused stopwatch stays paused across a reload an hour later",
    !isRunning(parseRecord(JSON.stringify(paused), now + 3_600_000)),
  );
  check(
    "resume reopens without losing the bank",
    Math.round(elapsedOf(resume(paused, now), now)) === 630,
  );

  console.log("\nthe one record still rejected");
  const skewed = parseRecord(JSON.stringify({ accumulated: 5, runningSince: now + 60_000 }), now);
  check(
    "a start time in the future is dropped, keeping the banked total",
    !isRunning(skewed) && elapsedOf(skewed, now) === 5,
  );
} finally {
  rmSync(out, { recursive: true, force: true });
}

console.log(failures === 0 ? "\nall stopwatch checks passed" : `\n${failures} check(s) failed`);
process.exit(failures === 0 ? 0 : 1);
