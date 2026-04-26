# GitHub Copilot distribution

## Repo-wide single file (simpler)

Copy `.github/copilot-instructions.md` to your project's `.github/`.

Enable in VS Code:

```json
{ "github.copilot.chat.codeGeneration.useInstructionFiles": true }
```

## Scoped instructions (more accurate)

Copy `.github/instructions/*.instructions.md` to your project. Each file declares `applyTo` globs so Copilot only loads the relevant rule for matching files.
