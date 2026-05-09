# GitHub Branch Protection Baseline (main)

## Required Settings
1. Require a pull request before merging
2. Require approvals: minimum 1
3. Dismiss stale pull request approvals when new commits are pushed
4. Require status checks to pass before merging
5. Required checks:
   - `build-and-check`
6. Require branches to be up to date before merging
7. Restrict direct pushes to `main`
8. Include administrators in restrictions
9. Disable force pushes
10. Disable branch deletion

## Optional Hardening
1. Require conversation resolution before merge
2. Enable secret scanning alerts and push protection
3. Enable Dependabot security updates
4. Enable vulnerability alerts

## Recommended Merge Policy
1. Allow squash merge
2. Disable merge commits
3. Optionally disable rebase merge
