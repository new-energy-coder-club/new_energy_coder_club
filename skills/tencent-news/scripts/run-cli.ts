import {
  detectPlatform,
  ensureCliExecutable,
  fail,
  injectCallerArg,
  resolveSkillName,
  supportsCallerArg,
} from "./_common";

function formatError(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

const args = process.argv.slice(2);

if (args.length === 0) {
  fail("missing CLI command");
}

const platform = detectPlatform();

await ensureCliExecutable(platform.cliPath);

const caller = await resolveSkillName();
const finalArgs = (await supportsCallerArg(platform.cliPath))
  ? injectCallerArg(args, caller)
  : args;

let proc: ReturnType<typeof Bun.spawn>;
try {
  proc = Bun.spawn([platform.cliPath, ...finalArgs], {
    stdout: "inherit",
    stderr: "inherit",
  });
} catch (error) {
  fail(`${platform.cliPath} ${finalArgs.join(" ")} failed to start: ${formatError(error)}`);
}

const exitCode = await proc.exited;
process.exit(exitCode);
