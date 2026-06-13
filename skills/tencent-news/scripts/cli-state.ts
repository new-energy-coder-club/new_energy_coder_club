import {
  type PlatformInfo,
  detectPlatform, getPlatformJson, getApiKeyState,
  getCliVersionState,
  fail,
} from "./_common";

if (process.argv[2] === "help") {
  console.log(
    "Usage: bun scripts/cli-state.ts\n\n" +
    "Print install state, version/update status, and API key status.",
  );
  process.exit(0);
}

const args = process.argv.slice(2);
if (args.length > 0) {
  fail(`unknown argument: ${args[0]}`);
}

const p = detectPlatform();
const cliExists = await Bun.file(p.cliPath).exists();
const cliSource: PlatformInfo["cliSource"] = cliExists ? p.cliSource : "none";
const platform: PlatformInfo = { ...p, cliSource };

const update = {
  needUpdate: null as boolean | null,
  error: null as string | null,
};

if (cliExists) {
  try {
    const versionState = await getCliVersionState(platform.cliPath);
    if (versionState.error) {
      update.error = versionState.error;
    } else {
      const parsed = versionState.versionInfo;
      if (parsed && typeof parsed.need_update === "boolean") {
        update.needUpdate = parsed.need_update;
      } else {
        update.error = `${platform.cliPath} version did not return a valid need_update value: ${versionState.rawOutput || "(empty output)"}`;
      }
    }
  } catch (error) {
    update.error = error instanceof Error ? error.message : String(error);
  }
}

console.log(JSON.stringify({
  platform: getPlatformJson(platform),
  cliExists,
  update,
  apiKey: await getApiKeyState(platform),
}, null, 2));
