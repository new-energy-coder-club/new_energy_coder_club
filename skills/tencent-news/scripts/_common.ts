import { existsSync } from "node:fs";
import { chmod, readFile } from "node:fs/promises";

export const BASE_DOWNLOAD_URL = "https://mat1.gtimg.com/qqcdn/qqnews/cli/hub";
const INSTALL_ENV_NAME = "TENCENT_NEWS_INSTALL";
const CALLER_MIN_VERSION = "1.0.12";

const SCRIPT_DIR = import.meta.dir.replaceAll("\\", "/");
export const SKILL_DIR = SCRIPT_DIR.replace(/\/[^/]+$/, "");

export function fail(msg: string): never {
  console.error(`Error: ${msg}`);
  process.exit(1);
}

export function normalizeApiKey(raw: string): string {
  let key = raw.trim();
  if ((key.startsWith('"') && key.endsWith('"')) || (key.startsWith("'") && key.endsWith("'"))) {
    key = key.slice(1, -1);
  }
  key = key.replace(/^api[\s_-]*key\s*[:=]\s*/i, "");
  return key.trim();
}

function formatError(error: unknown): string {
  return error instanceof Error ? error.message : String(error);
}

function trimOptionalQuotes(value: string): string {
  if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
    return value.slice(1, -1).trim();
  }
  return value.trim();
}

interface CommandResult {
  stdout: string;
  stderr: string;
  exitCode: number;
  output: string;
}

interface CliVersionInfo {
  current_version?: unknown;
  need_update?: unknown;
}

export interface CliVersionState {
  rawOutput: string;
  error: string | null;
  versionInfo: CliVersionInfo | null;
}

async function runCommand(args: string[], description: string): Promise<CommandResult> {
  let proc: ReturnType<typeof Bun.spawn>;
  try {
    proc = Bun.spawn(args, { stdout: "pipe", stderr: "pipe" });
  } catch (error) {
    fail(`${description} failed to start: ${formatError(error)}`);
  }

  const stdoutPromise = new Response(proc.stdout).text();
  const stderrPromise = new Response(proc.stderr).text();
  const [stdout, stderr, exitCode] = await Promise.all([stdoutPromise, stderrPromise, proc.exited]);
  const output = (stdout + stderr).trim();
  return { stdout, stderr, exitCode, output };
}

export interface PlatformInfo {
  os: string;
  arch: string;
  isWindows: boolean;
  cliFilename: string;
  cliPath: string;
  cliSource: "global" | "local" | "none";
  cliDownloadUrl: string;
}

export interface DetectPlatformOptions {
  preferGlobal?: boolean;
}

function resolveInstallRoot(): string {
  const configuredRoot = process.env[INSTALL_ENV_NAME]?.trim();
  if (configuredRoot) return configuredRoot.replaceAll("\\", "/");

  const homeDir = process.env.HOME?.trim()
    || process.env.USERPROFILE?.trim()
    || `${process.env.HOMEDRIVE ?? ""}${process.env.HOMEPATH ?? ""}`.trim();

  if (!homeDir) fail(`unable to resolve home directory for ${INSTALL_ENV_NAME} fallback`);
  return `${homeDir}/.tencent-news-cli`.replaceAll("\\", "/");
}

function resolveCommandCliPath(cliCommandName: string, isWindows: boolean): string | null {
  const lookupCommand = isWindows ? "where" : "which";
  const lookupArgs = [lookupCommand, cliCommandName];

  try {
    const proc = Bun.spawnSync(lookupArgs, { stdout: "pipe", stderr: "pipe" });
    if (proc.exitCode !== 0) return null;

    const resolvedPath = proc.stdout.toString().trim().split(/\r?\n/)[0]?.trim();
    if (!resolvedPath) return null;

    const helpProc = Bun.spawnSync([resolvedPath, "help"], { stdout: "pipe", stderr: "pipe" });
    if (helpProc.exitCode !== 0) return null;

    return resolvedPath.replaceAll("\\", "/");
  } catch {
    return null;
  }
}

export function detectPlatform(options: DetectPlatformOptions = {}): PlatformInfo {
  const preferGlobal = options.preferGlobal ?? true;

  let os: string;
  switch (process.platform) {
    case "win32":  os = "windows"; break;
    case "darwin": os = "darwin";  break;
    case "linux":  os = "linux";   break;
    default: fail(`unsupported os: ${process.platform}`);
  }

  let arch: string;
  switch (process.arch) {
    case "arm64": arch = "arm64"; break;
    case "x64":   arch = "amd64"; break;
    default: fail(`unsupported architecture: ${process.arch}`);
  }

  const isWindows = os === "windows";
  const cliCommandName = "tencent-news-cli";
  const cliFilename = isWindows ? "tencent-news-cli.exe" : "tencent-news-cli";
  const localCliPath = `${SKILL_DIR}/${cliFilename}`;
  const globalCliPath = `${resolveInstallRoot()}/bin/${cliFilename}`;
  const cliDownloadUrl = `${BASE_DOWNLOAD_URL}/${os}-${arch}/${cliFilename}`;

  let cliPath = globalCliPath;
  let cliSource: "global" | "local" | "none" = "none";

  const commandCliPath = preferGlobal ? resolveCommandCliPath(cliCommandName, isWindows) : null;
  if (commandCliPath) {
    cliPath = commandCliPath;
    cliSource = "global";
  } else if (preferGlobal && existsSync(globalCliPath)) {
    cliSource = "global";
  } else if (existsSync(localCliPath)) {
    cliPath = localCliPath;
    cliSource = "local";
  }

  return {
    os, arch, isWindows, cliFilename, cliPath, cliSource, cliDownloadUrl,
  };
}

export function getPlatformJson(p: PlatformInfo) {
  return {
    os: p.os,
    arch: p.arch,
    cliPath: p.cliPath,
    cliSource: p.cliSource,
  };
}

export async function resolveSkillName(skillDir: string = SKILL_DIR): Promise<string> {
  const skillMdPath = `${skillDir}/SKILL.md`;

  let skillMdContent: string;
  try {
    skillMdContent = await readFile(skillMdPath, "utf8");
  } catch (error) {
    fail(`failed to read ${skillMdPath}: ${formatError(error)}`);
  }

  const frontmatterMatch = skillMdContent.match(/^---\s*\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
  if (!frontmatterMatch) {
    fail(`SKILL.md missing YAML frontmatter: ${skillMdPath}`);
  }

  const nameMatch = frontmatterMatch[1].match(/^name:\s*(.+)$/m);
  if (!nameMatch) {
    fail(`name field not found in ${skillMdPath}`);
  }

  const skillName = trimOptionalQuotes(nameMatch[1] || "");
  if (!skillName) {
    fail(`name field is empty in ${skillMdPath}`);
  }

  return skillName;
}

export function injectCallerArg(args: string[], caller: string): string[] {
  if (!caller.trim()) {
    fail("caller cannot be empty");
  }

  if (args.some((arg) => arg === "--caller" || arg.startsWith("--caller="))) {
    fail("do not pass --caller manually; scripts/run-cli injects it from SKILL.md");
  }

  const callerArgs = ["--caller", caller];
  const argsTerminatorIndex = args.indexOf("--");

  if (argsTerminatorIndex === -1) {
    return [...args, ...callerArgs];
  }

  return [
    ...args.slice(0, argsTerminatorIndex),
    ...callerArgs,
    ...args.slice(argsTerminatorIndex),
  ];
}

export async function getCliVersionState(cliPath: string): Promise<CliVersionState> {
  const versionResult = await runCommand([cliPath, "version"], `${cliPath} version`);
  const rawOutput = versionResult.output;

  if (versionResult.exitCode !== 0) {
    return {
      rawOutput,
      error: rawOutput || `${cliPath} version failed with exit code ${versionResult.exitCode}`,
      versionInfo: null,
    };
  }

  let versionInfo: unknown;
  try {
    versionInfo = JSON.parse(rawOutput);
  } catch {
    return {
      rawOutput,
      error: `${cliPath} version did not return valid JSON: ${rawOutput || "(empty output)"}`,
      versionInfo: null,
    };
  }

  if (!versionInfo || typeof versionInfo !== "object" || Array.isArray(versionInfo)) {
    return {
      rawOutput,
      error: `${cliPath} version did not return a JSON object: ${rawOutput || "(empty output)"}`,
      versionInfo: null,
    };
  }

  return {
    rawOutput,
    error: null,
    versionInfo: versionInfo as CliVersionInfo,
  };
}

function parseVersionParts(rawVersion: string): number[] | null {
  const normalized = trimOptionalQuotes(rawVersion).replace(/^v/i, "").split("-")[0];
  if (!normalized) return null;

  const parts = normalized.split(".");
  if (parts.some((part) => part === "" || !/^\d+$/.test(part))) {
    return null;
  }

  return parts.map((part) => Number(part));
}

function compareVersions(a: string, b: string): number | null {
  const left = parseVersionParts(a);
  const right = parseVersionParts(b);
  if (!left || !right) return null;

  const length = Math.max(left.length, right.length);
  for (let index = 0; index < length; index += 1) {
    const leftPart = left[index] ?? 0;
    const rightPart = right[index] ?? 0;
    if (leftPart > rightPart) return 1;
    if (leftPart < rightPart) return -1;
  }

  return 0;
}

export async function supportsCallerArg(cliPath: string): Promise<boolean> {
  const versionState = await getCliVersionState(cliPath);
  if (versionState.error || !versionState.versionInfo) {
    return false;
  }

  const currentVersion = typeof versionState.versionInfo.current_version === "string"
    ? versionState.versionInfo.current_version.trim()
    : "";
  if (!currentVersion) {
    return false;
  }

  const compared = compareVersions(currentVersion, CALLER_MIN_VERSION);
  return compared !== null && compared >= 0;
}

function extractApiKey(output: string): string | null {
  const match = output.match(/API Key\s*:\s*(.+)$/m);
  if (!match) return null;
  const value = normalizeApiKey(match[1] || "");
  return value || null;
}

function includesMissingApiKeyMessage(output: string): boolean {
  return /未设置 API Key/i.test(output) || /not set/i.test(output);
}

export async function ensureCliExecutable(cliPath: string): Promise<void> {
  if (!(await Bun.file(cliPath).exists())) fail(`cli not found at ${cliPath}`);
  if (process.platform !== "win32") {
    await chmod(cliPath, 0o755).catch(() => {});
  }
}

async function runCliCommand(p: PlatformInfo, args: string[]): Promise<CommandResult> {
  await ensureCliExecutable(p.cliPath);
  return runCommand([p.cliPath, ...args], `${p.cliPath} ${args.join(" ")}`);
}

export interface ApiKeyState {
  status: "configured" | "missing" | "error";
  present: boolean;
  error: string | null;
}

export async function getApiKeyState(p: PlatformInfo): Promise<ApiKeyState> {
  if (!(await Bun.file(p.cliPath).exists())) {
    return {
      status: "error",
      present: false,
      error: "CLI not found, cannot check API key.",
    };
  }

  const result = await runCliCommand(p, ["apikey-get"]);
  const rawOutput = result.output;

  if (result.exitCode === 0) {
    const key = extractApiKey(rawOutput);
    return {
      status: key ? "configured" : "error",
      present: !!key,
      error: key ? null : "CLI apikey-get succeeded, but API key could not be parsed from output.",
    };
  }

  if (includesMissingApiKeyMessage(rawOutput) || result.exitCode === 2) {
    return {
      status: "missing",
      present: false,
      error: null,
    };
  }

  return {
    status: "error",
    present: false,
    error: rawOutput || `apikey-get failed with exit code ${result.exitCode}.`,
  };
}
