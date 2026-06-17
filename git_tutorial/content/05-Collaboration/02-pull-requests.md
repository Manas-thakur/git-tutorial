## Pull Requests

Pull requests (PRs) are a core feature of collaboration platforms like GitHub, GitLab, and Bitbucket. A pull request is a request to merge changes from one branch into another, typically accompanied by a description, discussion, and review process.

### 1. Creating Pull Requests

A pull request is created after you push a branch to a remote repository. It signals to other team members that your changes are ready for review.

**Creating a PR on GitHub:**

1. Push your feature branch:
   ```
   $ git push origin feature/new-feature
   ```

2. Navigate to the repository on GitHub
3. GitHub detects the newly pushed branch and shows a "Compare & pull request" button
4. Click the button and fill in:
   - **Base branch**: The branch you want to merge into (e.g., main)
   - **Compare branch**: Your feature branch
   - **Title**: A concise description of the changes
   - **Description**: Detailed explanation, including context, motivation, and any breaking changes

**Creating a PR via GitHub CLI:**

```
$ gh pr create --base main --head feature/new-feature --title "Add user authentication" --body "Implements OAuth2 login flow"
```

**Creating a PR via GitLab Merge Request:**

The equivalent on GitLab is called a Merge Request (MR), created similarly through the UI or API.

**What makes a good PR description:**

- What problem does this solve?
- How does it solve it (high level)?
- What changed (summary of files modified)?
- Any breaking changes or migration steps?
- Screenshots or logs for UI changes
- Related issues or tickets (e.g., "Closes #123")

### 2. Code Review Workflow

The typical code review workflow involves several stages:

**Submission:**
- Author creates the PR
- CI/CD pipelines run automated checks (lint, test, build)
- Author may need to fix failing checks before requesting review

**Review:**
- Reviewers are assigned or volunteer
- Reviewers examine the changes and leave comments
- Reviewers can approve, request changes, or comment
- Discussions happen inline or in the PR comments

**Revisions:**
- Author addresses feedback by pushing new commits
- Reviewers re-review the changes
- The cycle repeats until approval

**Merge:**
- PR is approved and all checks pass
- The PR is merged using the chosen merge strategy
- The branch may be deleted after merge

**Typical review states on GitHub:**

- **Changes requested**: Reviewer has concerns that need addressing
- **Approved**: Reviewer is satisfied with the changes
- **Comment**: General feedback without blocking the merge

### 3. Updating PRs with New Commits

When a reviewer requests changes, you update the PR by pushing new commits to the same branch. The PR automatically reflects the new commits.

```
$ git checkout feature/new-feature
# Make changes based on review feedback
$ git add .
$ git commit -m "Address review feedback: fix edge case in validation"
$ git push origin feature/new-feature
```

The PR updates automatically to include the new commit. GitHub shows the commit history and highlights what changed since the last review.

**Amending a commit (if the PR has only one commit):**

```
$ git add .
$ git commit --amend --no-edit
$ git push --force-with-lease origin feature/new-feature
```

Warning: Force pushing after a PR is opened can confuse reviewers if they have already reviewed the previous commits. Use with caution and communicate with your team.

**Interactive rebase to clean up history before merge:**

Some teams prefer a clean commit history. You can rebase before the final push:

```
$ git rebase -i HEAD~3
# Squash fixup commits into logical commits
$ git push --force-with-lease origin feature/new-feature
```

### 4. Squashing Before Merge

Squashing combines all commits in a PR into a single commit before merging. This keeps the main branch history clean and linear.

**Squash and merge on GitHub:**

GitHub provides a "Squash and merge" button that automatically squashes all commits from the feature branch into one commit before merging.

```
Before squash-and-merge:
main:     A---B---C
feature:   \---D---E---F

After squash-and-merge:
main:     A---B---C---G
Where G combines D, E, F into a single commit
```

**Manual squash via interactive rebase:**

```
$ git rebase -i main
# Mark all but the first commit as squash or fixup
$ git push --force-with-lease origin feature
```

**Pros of squashing:**
- Clean, linear history on main
- Each commit on main represents a coherent, complete feature
- Removes "WIP" and "fix typo" commits from the permanent record

**Cons of squashing:**
- Loses granularity of individual commits
- Makes `git bisect` less precise (harder to find which specific change broke something)
- Merged commits lose their original authorship timestamps

### 5. Merge Strategies (Merge Commit, Squash, Rebase)

Most platforms offer three merge strategies:

**1. Create a merge commit:**

```
$ git checkout main
$ git merge --no-ff feature/new-feature
```

This creates a merge commit even if a fast-forward is possible. Preserves full branch history.

```
main: A---B---C---D---E---F---G
                  \         /
feature:            H---I---J
```

- Pros: Preserves exact branch topology and individual commits
- Cons: Adds merge commits that can clutter history

**2. Squash and merge:**

```
$ git checkout main
$ git merge --squash feature/new-feature
$ git commit -m "Add feature X"
```

All feature branch commits are combined into one single commit.

```
main: A---B---C---D---E---F---G
```

- Pros: Clean, linear history
- Cons: Loses individual commit context

**3. Rebase and merge:**

```
$ git checkout feature/new-feature
$ git rebase main
$ git checkout main
$ git merge feature/new-feature
```

This rebases the feature commits onto main, then fast-forwards main.

```
main: A---B---C---D---E'---F'---G'
```

- Pros: Linear history, preserves individual commits
- Cons: Requires force push if the branch was already pushed

**Which strategy to choose:**

| Strategy       | When to use                                       |
|----------------|---------------------------------------------------|
| Merge commit   | Preserving full history and collaboration context |
| Squash         | Each PR should be one logical commit on main      |
| Rebase         | Each PR commit is meaningful and should be kept   |

### Quiz: Pull Requests

**Question 1:** A reviewer asks you to make changes to your PR. What is the correct workflow?

a) Close the PR and create a new one with the changes
b) Make changes locally, commit, push to the same branch, and the PR updates automatically
c) Make changes directly on the main branch
d) Email the changes to the reviewer for manual application

**Question 2:** What is the main advantage of using squash-and-merge on a pull request?

a) It preserves every individual commit from the feature branch
b) It creates a merge commit that shows the branch topology
c) It combines all feature commits into one clean commit on the target branch
d) It automatically deletes the feature branch

**Question 3:** Which merge strategy produces a linear history while preserving individual commits from the feature branch?

a) Create a merge commit
b) Squash and merge
c) Rebase and merge
d) All of the above produce linear history

---

**Answers:** 1-b, 2-c, 3-c
