# Publishing to npm

The repo ships with everything needed to publish the npx installer to npm so that anyone can run `npx <your-package-name>` to install skills into their project.

## Choose a package name

`odoo-coding-skills` is the default placeholder. Before first publish, edit `package.json` and pick a name:

- **Unscoped**: `npx my-coding-skills` — must be globally unique on npm. Check at https://www.npmjs.com/package/my-coding-skills
- **Scoped**: `npx @your-org/coding-skills` — namespaced under your username/org. Always available if your org name is.

Update these fields in `package.json`:
```json
{
  "name": "your-package-name",
  "repository": { "url": "git+https://github.com/<owner>/<repo>.git" },
  "bugs":       { "url": "https://github.com/<owner>/<repo>/issues" },
  "homepage":   "https://github.com/<owner>/<repo>#readme"
}
```

Then update README.md, replacing all instances of `odoo-coding-skills` with your chosen name.

## First-time publish (manual)

```bash
# 1. Make sure dist/ is up to date
python scripts/build.py

# 2. Sanity-check
node installer/index.js --list

# 3. Login to npm (one-time)
npm login

# 4. Publish
npm publish --access public
```

If the package name is scoped (`@org/name`), `--access public` is required for free npm accounts; otherwise it defaults to private.

## Automated publish (GitHub Actions)

The `.github/workflows/npm-publish.yml` workflow publishes automatically when you create a GitHub release.

### Setup

1. Generate an npm automation token: https://www.npmjs.com/settings/<user>/tokens → New Granular Token → Type: "Automation" → scope to your package.
2. Add it as a repo secret named `NPM_TOKEN`: GitHub repo → Settings → Secrets and variables → Actions → New secret.

### Trigger a publish

```bash
# 1. Bump version
npm version patch    # 0.2.0 → 0.2.1   (or `minor`, or `major`)
git push --follow-tags

# 2. Create a GitHub release for the new tag (via UI or:)
gh release create v0.2.1 --generate-notes

# Action runs automatically and publishes to npm.
```

The workflow:
1. Checks out the tagged commit
2. Rebuilds `dist/` from `skills/`
3. Runs the installer help/list to verify it works
4. `npm publish --provenance` (uses the secret token)

`--provenance` adds a cryptographic statement linking the published package to the GitHub commit it was built from, visible on npmjs.com — a nice security signal for users.

## Version policy

Two changelogs:

- **Top-level `CHANGELOG.md`** tracks the npm package version — the build script, installer, and structural changes.
- **`skills/<n>/CHANGELOG.md`** tracks each skill's coverage version independently.

A new skill release usually means a new package release too, so both changelogs get updated together.

Use semver for the npm package:
- **Patch** (0.2.0 → 0.2.1): bug fixes, doc updates, content updates to existing rules
- **Minor** (0.2.0 → 0.3.0): new skill added, new provider supported, non-breaking API changes
- **Major** (0.x.x → 1.0.0): breaking changes to the installer CLI, removed providers, structural changes that require user action

## Testing before publish

To dry-run the install end-to-end:

```bash
# Pack the package as it would be published
npm pack
# Produces: <name>-<version>.tgz

# Install into a throwaway project
mkdir /tmp/test && cd /tmp/test
npm init -y
npm install /path/to/<name>-<version>.tgz

# Run as it would be from npx
npx --no-install <name> --list
npx --no-install <name> -s odoo19-syntax -p cursor -t /tmp/fake-project -y

# Cleanup
cd / && rm -rf /tmp/test /path/to/<name>-<version>.tgz
```

This simulates exactly what an end user gets via `npx <name>`.

## Unpublishing

npm policy: you can `npm unpublish` within 72 hours of publishing if no one has installed it. After that, deprecate instead:

```bash
npm deprecate <name>@"< 0.2.0" "Please upgrade to 0.2.0 or later"
```

Avoid unpublishing once the package has users — broken installs are worse than an outdated version.
