#!/usr/bin/env node
/**
 * odoo-coding-skills installer
 *
 * Interactive (or flag-driven) CLI to install a coding-rules skill into the
 * user's project for their AI tool of choice.
 *
 * Usage:
 *   npx odoo-coding-skills                       # interactive
 *   npx odoo-coding-skills --list
 *   npx odoo-coding-skills -s <skill> -p <provider> [-t <target>] [-y]
 */

'use strict';

const fs = require('node:fs');
const path = require('node:path');

let prompts;
try {
  prompts = require('prompts');
} catch (err) {
  console.error("Missing dependency 'prompts'. If running from a clone, run:");
  console.error('  npm install');
  process.exit(1);
}

const PACKAGE_ROOT = path.resolve(__dirname, '..');
const DIST_DIR = path.join(PACKAGE_ROOT, 'dist');
const SKILLS_SRC_DIR = path.join(PACKAGE_ROOT, 'skills');

const PROVIDERS = [
  { value: 'claude',    label: 'Claude (Anthropic)' },
  { value: 'cursor',    label: 'Cursor' },
  { value: 'copilot',   label: 'GitHub Copilot' },
  { value: 'cline',     label: 'Cline' },
  { value: 'windsurf',  label: 'Windsurf / Codeium' },
  { value: 'aider',     label: 'Aider' },
  { value: 'continue',  label: 'Continue.dev' },
  { value: 'generic',   label: 'Generic (any LLM — paste as system prompt)' },
];

// ---------- Argument parsing ----------

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    switch (a) {
      case '-l': case '--list':     args.list = true; break;
      case '-h': case '--help':     args.help = true; break;
      case '-y': case '--yes':      args.yes = true; break;
      case '-s': case '--skill':    args.skill = argv[++i]; break;
      case '-p': case '--provider': args.provider = argv[++i]; break;
      case '-t': case '--target':   args.target = argv[++i]; break;
      default:
        if (a.startsWith('--')) {
          const eq = a.indexOf('=');
          if (eq > 0) args[a.slice(2, eq)] = a.slice(eq + 1);
          else args[a.slice(2)] = true;
        }
    }
  }
  return args;
}

// ---------- Skill discovery ----------

function discoverSkills() {
  if (!fs.existsSync(DIST_DIR)) return [];
  return fs.readdirSync(DIST_DIR, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name)
    .sort();
}

function readSkillDescription(skillName) {
  // Try several locations:
  //   1. skills/<n>/SKILL.md       — present when running from a repo clone
  //   2. dist/<n>/claude/<n>/SKILL.md — present in the published npm package
  const candidates = [
    path.join(SKILLS_SRC_DIR, skillName, 'SKILL.md'),
    path.join(DIST_DIR, skillName, 'claude', skillName, 'SKILL.md'),
  ];

  for (const p of candidates) {
    if (!fs.existsSync(p)) continue;
    const content = fs.readFileSync(p, 'utf8');
    const fmMatch = content.match(/^---\n([\s\S]*?)\n---/);
    if (!fmMatch) continue;
    const dm = fmMatch[1].match(/^description:\s*([\s\S]+?)(?=\n[a-z_]+:|$)/m);
    if (!dm) continue;
    return dm[1].trim().replace(/\s+/g, ' ').replace(/^"|"$/g, '');
  }
  return null;
}

function shorten(text, n = 70) {
  if (!text) return '';
  return text.length > n ? text.slice(0, n).trimEnd() + '...' : text;
}

// ---------- Help / list ----------

function showHelp() {
  console.log(`
odoo-coding-skills — install AI coding rules into your project

Usage:
  npx odoo-coding-skills                     interactive install
  npx odoo-coding-skills [options]           non-interactive

Options:
  -s, --skill <name>      Skill to install (e.g. odoo19-syntax)
  -p, --provider <id>     AI tool: claude, cursor, copilot, cline,
                          windsurf, aider, continue, generic
  -t, --target <path>     Project root (default: current directory)
  -y, --yes               Overwrite existing files without asking
  -l, --list              List available skills
  -h, --help              Show this help

Examples:
  npx odoo-coding-skills
  npx odoo-coding-skills --list
  npx odoo-coding-skills -s odoo19-syntax -p cursor
  npx odoo-coding-skills -s odoo19-syntax -p copilot -t ~/my-project -y
`);
}

function listSkills() {
  const skills = discoverSkills();
  if (skills.length === 0) {
    console.log('No skills available. (dist/ is empty or missing)');
    return;
  }
  console.log('Available skills:');
  for (const s of skills) {
    const d = readSkillDescription(s);
    if (d) console.log(`  - ${s}\n      ${shorten(d, 80)}`);
    else   console.log(`  - ${s}`);
  }
}

// ---------- File copy with conflict detection ----------

function walkSource(srcDir, opts = {}) {
  const { skipRootNames = [] } = opts;
  const items = [];

  function recurse(dir, isRoot) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      if (isRoot && skipRootNames.includes(entry.name)) continue;
      const full = path.join(dir, entry.name);
      const rel = path.relative(srcDir, full);
      if (entry.isDirectory()) {
        items.push({ rel, isDir: true });
        recurse(full, false);
      } else if (entry.isFile()) {
        items.push({ rel, isDir: false });
      }
    }
  }

  recurse(srcDir, true);
  return items;
}

function detectConflicts(srcDir, destDir, opts) {
  const items = walkSource(srcDir, opts);
  const conflicts = [];
  for (const it of items) {
    if (it.isDir) continue;
    const destFile = path.join(destDir, it.rel);
    if (fs.existsSync(destFile)) conflicts.push(destFile);
  }
  return conflicts;
}

function copyTree(srcDir, destDir, opts) {
  const items = walkSource(srcDir, opts);
  let copied = 0;
  for (const it of items) {
    const srcPath = path.join(srcDir, it.rel);
    const destPath = path.join(destDir, it.rel);
    if (it.isDir) {
      fs.mkdirSync(destPath, { recursive: true });
    } else {
      fs.mkdirSync(path.dirname(destPath), { recursive: true });
      fs.copyFileSync(srcPath, destPath);
      copied++;
    }
  }
  return copied;
}

// ---------- Provider-specific post-install hints ----------

const POST_INSTALL_HINTS = {
  copilot: [
    'To enable in VS Code, add to .vscode/settings.json:',
    '  { "github.copilot.chat.codeGeneration.useInstructionFiles": true }',
  ],
  aider: [
    'Run aider with: aider --read CONVENTIONS.md',
    'Or copy .aider.conf.yml.example to .aider.conf.yml to load automatically.',
  ],
  cursor: [
    'Cursor will auto-load .cursor/rules/ in your next chat session.',
  ],
  cline: [
    'Cline will auto-load .clinerules in your next session. To use the multi-file',
    'variant instead, rename .clinerules-split/ to .clinerules/.',
  ],
  generic: [
    'Open the .md file and paste its contents into your AI tool\'s system prompt',
    'or "custom instructions" field.',
  ],
};

// ---------- Main ----------

async function main() {
  const args = parseArgs(process.argv);

  if (args.help) { showHelp(); return; }
  if (args.list) { listSkills(); return; }

  const skills = discoverSkills();
  if (skills.length === 0) {
    console.error('No skills available in dist/. Run `python scripts/build.py` first');
    console.error('(or reinstall the npm package).');
    process.exit(1);
  }

  // 1. Pick skill
  let skill = args.skill;
  if (!skill) {
    const r = await prompts({
      type: 'select',
      name: 'skill',
      message: 'Which skill do you want to install?',
      choices: skills.map(s => ({
        title: s,
        description: shorten(readSkillDescription(s), 70),
        value: s,
      })),
    }, { onCancel: () => process.exit(0) });
    skill = r.skill;
  }
  if (!skills.includes(skill)) {
    console.error(`Unknown skill: ${skill}`);
    console.error(`Available: ${skills.join(', ')}`);
    process.exit(1);
  }

  const skillDir = path.join(DIST_DIR, skill);

  // 2. Pick provider
  const availableProviders = PROVIDERS.filter(p =>
    fs.existsSync(path.join(skillDir, p.value))
  );
  let provider = args.provider;
  if (!provider) {
    const r = await prompts({
      type: 'select',
      name: 'provider',
      message: 'Which AI tool are you using?',
      choices: availableProviders.map(p => ({ title: p.label, value: p.value })),
    }, { onCancel: () => process.exit(0) });
    provider = r.provider;
  }
  const providerInfo = availableProviders.find(p => p.value === provider);
  if (!providerInfo) {
    console.error(`Provider '${provider}' is not available for skill '${skill}'`);
    console.error(`Available: ${availableProviders.map(p => p.value).join(', ')}`);
    process.exit(1);
  }

  // 3. Target directory
  let targetDir = args.target;
  if (!targetDir) {
    const r = await prompts({
      type: 'text',
      name: 'target',
      message: 'Project root path:',
      initial: process.cwd(),
    }, { onCancel: () => process.exit(0) });
    targetDir = r.target;
  }
  const targetAbs = path.resolve(targetDir);
  if (!fs.existsSync(targetAbs) || !fs.statSync(targetAbs).isDirectory()) {
    console.error(`Target is not a directory: ${targetAbs}`);
    process.exit(1);
  }

  // 4. Special-case Claude (single .skill file)
  if (provider === 'claude') {
    const skillFile = path.join(skillDir, `${skill}.skill`);
    if (!fs.existsSync(skillFile)) {
      console.error(`.skill file not found: ${skillFile}`);
      process.exit(1);
    }
    const dest = path.join(targetAbs, `${skill}.skill`);
    if (fs.existsSync(dest) && !args.yes) {
      const r = await prompts({
        type: 'confirm',
        name: 'overwrite',
        message: `${skill}.skill exists in target. Overwrite?`,
        initial: false,
      }, { onCancel: () => process.exit(0) });
      if (!r.overwrite) { console.log('Aborted.'); return; }
    }
    fs.copyFileSync(skillFile, dest);
    console.log(`\n✅ Copied ${skill}.skill to ${dest}\n`);
    console.log('Next steps:');
    console.log('  Claude.ai web/desktop:');
    console.log('    Settings → Capabilities → Skills → Upload skill → choose this file');
    console.log('  Claude Code CLI:');
    console.log(`    Place the unpacked skill folder under .claude/skills/${skill}/`);
    return;
  }

  // 5. Other providers: copy directory contents (excluding the per-provider README)
  const sourceDir = path.join(skillDir, provider);
  const copyOpts = { skipRootNames: ['README.md'] };

  const conflicts = detectConflicts(sourceDir, targetAbs, copyOpts);
  if (conflicts.length > 0 && !args.yes) {
    console.log(`\n⚠️  ${conflicts.length} file(s) will be overwritten:`);
    for (const c of conflicts.slice(0, 10)) {
      console.log(`   ${path.relative(targetAbs, c)}`);
    }
    if (conflicts.length > 10) {
      console.log(`   ... and ${conflicts.length - 10} more`);
    }
    const r = await prompts({
      type: 'confirm',
      name: 'overwrite',
      message: 'Overwrite these files?',
      initial: false,
    }, { onCancel: () => process.exit(0) });
    if (!r.overwrite) { console.log('Aborted.'); return; }
  }

  const copiedCount = copyTree(sourceDir, targetAbs, copyOpts);

  console.log(`\n✅ Installed ${skill} for ${providerInfo.label}`);
  console.log(`   ${copiedCount} files copied to ${targetAbs}`);

  const hints = POST_INSTALL_HINTS[provider];
  if (hints) {
    console.log('\n💡 ' + hints[0]);
    for (const line of hints.slice(1)) console.log('   ' + line);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  if (process.env.DEBUG) console.error(err);
  process.exit(1);
});
