## Git Workflows

Git workflows define how teams organize their branches, coordinate changes, and release software. Different workflows suit different team sizes, release cadences, and project requirements.

### 1. GitFlow (main, develop, feature, release, hotfix branches)

GitFlow is a comprehensive branching model designed by Vincent Driessen. It defines strict branch roles and lifecycle rules.

**Branch structure:**

```
main                     v1.0 ---- v1.1 ---- v2.0
                         /         /         /
develop                 *----*----*----*----*
                       /    /    /    /    /
feature/new-feature   *----*   /    /    /
                             /    /    /
release/v1.0               *----*  /
                                 /
hotfix/critical-fix            *----*
```

**Branch types:**

| Branch        | Purpose                                            | Lifecycle                     |
|---------------|----------------------------------------------------|-------------------------------|
| main          | Production-ready code. Always deployable.          | Permanent                     |
| develop       | Integration branch for features.                   | Permanent                     |
| feature/*     | New features. Branched from develop.               | Temporary, merged to develop  |
| release/*     | Preparing a new release. Branched from develop.    | Temporary, merged to main+develop |
| hotfix/*      | Urgent production fixes. Branched from main.       | Temporary, merged to main+develop |

**Workflow steps:**

1. Feature development:
   ```
   $ git checkout develop
   $ git checkout -b feature/user-auth
   # Work on the feature
   $ git commit -m "Add OAuth login"
   $ git checkout develop
   $ git merge --no-ff feature/user-auth
   $ git branch -d feature/user-auth
   ```

2. Creating a release:
   ```
   $ git checkout develop
   $ git checkout -b release/v1.0
   # Bug fixes and release prep
   $ git commit -m "Bump version to 1.0"
   $ git checkout main
   $ git merge --no-ff release/v1.0
   $ git tag -a v1.0 -m "Release v1.0"
   $ git checkout develop
   $ git merge --no-ff release/v1.0
   $ git branch -d release/v1.0
   ```

3. Hotfix for production:
   ```
   $ git checkout main
   $ git checkout -b hotfix/security-fix
   # Fix the critical bug
   $ git commit -m "Fix security vulnerability"
   $ git checkout main
   $ git merge --no-ff hotfix/security-fix
   $ git tag -a v1.0.1 -m "Hotfix v1.0.1"
   $ git checkout develop
   $ git merge --no-ff hotfix/security-fix
   $ git branch -d hotfix/security-fix
   ```

**When to use GitFlow:**
- Projects with a formal release cycle
- Multiple supported versions (e.g., LTS releases)
- Large teams where strict process is beneficial
- Projects that need both hotfix and feature isolation

### 2. GitHub Flow (Main + Feature Branches, PRs)

GitHub Flow is a simpler, more lightweight workflow that GitHub popularized. It has fewer rules and is well-suited for continuous deployment.

**Rules of GitHub Flow:**

1. Everything in `main` is always deployable
2. Create descriptive branches off main for new work
3. Push to your branch regularly
4. Open a pull request early for feedback
5. Merge only after review and passing CI
6. Deploy immediately after merge

**Workflow example:**

```
$ git checkout main
$ git checkout -b add-user-auth
# Work on the feature
$ git commit -m "Add user auth middleware"
$ git push origin add-user-auth
# Create a PR on GitHub
# Get reviews and address feedback
$ git commit -m "Address review feedback"
$ git push origin add-user-auth
# PR is approved, merge to main
$ git checkout main
$ git pull origin main
```

**Branch structure:**

```
main:  A---B---C---D---E---F---G
           \         /
feature:    *---*---*
```

**Key characteristics:**
- No `develop` branch. `main` is always the latest.
- Feature branches are short-lived (days, not weeks).
- Deployments happen from main after every merge.
- No release branches. Use feature toggles for incomplete work.

**When to use GitHub Flow:**
- Continuous deployment environments
- Small to medium teams
- Projects that deploy frequently (daily or more)
- SaaS products with a single supported version

### 3. Trunk-Based Development

Trunk-based development (TBD) is an even simpler model where developers work directly on `main` (the trunk) or on very short-lived branches.

**Key principles:**
- All developers work on `main` (or branch off for less than a day)
- Branches are merged within hours, not days
- Feature flags hide incomplete work
- No long-lived feature branches
- Frequent small commits to main

**Workflow with short-lived branches:**

```
$ git checkout main
$ git pull origin main
$ git checkout -b fix-typo
# Fix a typo (5 minutes of work)
$ git commit -m "Fix typo in error message"
$ git push origin fix-typo
# Open PR, get quick review, merge
# Continue working
```

**Using feature flags instead of branches:**

Instead of hiding incomplete features behind branches, hide them behind feature flags in the code:

```go
if feature.IsEnabled("new-login") {
    // New login code
} else {
    // Old login code
}
```

**Branch structure:**

```
main:  A---B---C---D---E---F---G---H---I
           \ /         \ /     \
           fix-a      fix-b   fix-c
```

**When to use trunk-based development:**
- Highly mature DevOps practices
- Strong automated testing culture
- Feature flags platform available
- Continuous delivery with fast deployment
- Small, experienced teams

### 4. Comparison and Decision Guide

| Aspect               | GitFlow            | GitHub Flow        | Trunk-Based        |
|----------------------|--------------------|--------------------|--------------------|
| Number of long-lived branches | 2 (main + develop) | 1 (main) | 1 (main) |
| Branch lifetime      | Days to weeks      | Hours to days      | Minutes to hours   |
| Release process      | Release branches   | Deploy from main   | Feature flags      |
| Hotfix handling      | Hotfix branches    | PR to main         | PR to main         |
| Complexity           | High               | Low                | Very low           |
| CI/CD requirements   | Medium             | High               | Very high          |
| Best for             | Versioned releases | SaaS/continuous    | Elite DevOps teams |

**How to choose:**

- **Your project has formal versioned releases** (v1.0, v2.0, etc.): GitFlow or a simplified version of it
- **You deploy continuously with automated CI/CD**: GitHub Flow
- **You are a small team with rapid iteration**: GitHub Flow
- **You have mature DevOps, feature flags, and automated testing**: Trunk-based development
- **You maintain multiple versions in production**: GitFlow (for LTS branches)

### 5. Simplified GitFlow for Modern Teams

Many teams use a simplified GitFlow that drops the `develop` branch:

```
main:  A---B---C---D---E---F---G
           \         /
feature:    *---*---*
```

In this model:
- Feature branches branch off and merge directly to main
- Releases are tagged on main
- Hotfixes branch off main and merge back to main
- No develop branch needed

This retains GitFlow's structured release approach while reducing complexity.

### Quiz: Git Workflows

**Question 1:** In GitFlow, which branch does a hotfix branch off from?

a) develop
b) feature
c) main
d) release

**Question 2:** What is the defining characteristic of trunk-based development?

a) Two permanent branches (main and develop)
b) Very short-lived branches merged into main within hours or less, using feature flags to hide incomplete work
c) Long-lived feature branches with frequent merging
d) Using release branches for version management

**Question 3:** Which workflow is most appropriate for a project that deploys multiple times per day and has a strong automated testing pipeline?

a) GitFlow
b) GitHub Flow
c) Waterfall
d) Both GitFlow and GitHub Flow are identical for this scenario

---

**Answers:** 1-c, 2-b, 3-b
