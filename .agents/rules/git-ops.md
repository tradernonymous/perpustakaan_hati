---
trigger: always_on
---

# Git Ops & GitHub MCP Rules (`tradernonymous/perpustakaan_hati`)

- **Repository Owner:** `tradernonymous` (`https://github.com/tradernonymous/perpustakaan_hati`).
- **GitHub MCP Server:** Always use **`github-work`** (authenticated as `tradernonymous`). Never use `github` or `github-mcp-server` (which are authenticated as `printezy247` and do not have write access to `tradernonymous/perpustakaan_hati`).
- **Full Automatic "git ops" Flow:** Whenever Jack says **"git ops"** (or after any successful build), execute the entire flow end-to-end without handing git commands back to him:
  1. Create and commit on a feature branch (`git switch --no-track -c <branch>`), never leaving new work only on local `main`. Do not commit stray dotfiles.
  2. Push the branch to `origin` (`git push -u origin <branch>`).
  3. Open a Pull Request to `main` via `github-work` MCP (or `gh pr create` authenticated with the `github-work` token).
  4. Verify CI checks (or local build/lint/test gates if no CI workflow exists).
  5. Squash-merge the PR into `main` immediately once green via `github-work` MCP (`merge_pull_request`) or `gh pr merge --squash --delete-branch`.
  6. Sync local `main` (`git switch main && git pull origin main && git fetch --prune`) and delete any leftover local feature branch.
  7. Report the final state concisely.
