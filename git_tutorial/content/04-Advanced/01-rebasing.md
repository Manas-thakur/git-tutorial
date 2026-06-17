## Rebasing

Rebasing is a Git operation that moves or replays a sequence of commits on top of a new base commit. Instead of merging divergent branches together, rebasing rewrites history so that the changes appear to have been made sequentially on top of the target branch.

### 1. What is Rebasing?

At its core, rebasing takes a set of commits from one branch and reapplies them onto another commit. The command `git rebase` does this by finding the common ancestor of the two branches, then creating new commits for each change that exists on the branch being rebased.

```
Before rebase:
      E---F---G feature
     /
A---B---C---D main

After `git rebase main` on feature:
              E'--F'--G' feature
             /
A---B---C---D main
```

The commits E', F', and G' are *new* commits -- they have different SHA-1 hashes than E, F, and G, even though the content changes are identical. This is because they now have a different parent commit (D instead of B).

### 2. git rebase vs git merge

Both `git rebase` and `git merge` integrate changes from one branch into another, but they do so in very different ways.

**Merge** creates a new "merge commit" that ties together the histories of both branches. The original branch commits remain unchanged, and the branch history shows a fork-and-join pattern. Merges are "truthful" in that they preserve exactly what happened and when.

**Rebase** rewrites history by placing commits in a linear sequence. It produces a cleaner, linear project history but at the cost of losing the historical context of when commits were originally made relative to each other.

```
git merge:
A---B---C---D---E (main)
         \     /
          F---G (feature)

git rebase:
A---B---C---D---F'---G' (main, after rebase and fast-forward)
```

When to use merge:
- Integrating a shared branch that others also use
- When you want to preserve the exact historical record
- When working on a public branch that others have based work on

When to use rebase:
- Cleaning up local commits before pushing
- Maintaining a linear project history
- Incorporating upstream changes into a feature branch

### 3. Rebase Workflow

A typical rebase workflow involves pulling the latest changes from the target branch and then rebasing your feature branch on top of it.

```
$ git checkout feature
$ git rebase main
```

If there are conflicts, Git will pause the rebase and ask you to resolve them. After resolving each conflicted file, stage it and continue:

```
$ git add <resolved-file>
$ git rebase --continue
```

To skip a problematic commit:

```
$ git rebase --skip
```

To abort the entire rebase and return to the original state:

```
$ git rebase --abort
```

A common workflow pattern is to rebase your feature branch before opening a pull request:

```
$ git checkout main
$ git pull --rebase
$ git checkout feature
$ git rebase main
$ git push --force-with-lease origin feature
```

The `--force-with-lease` option is safer than `--force` because it checks that your remote tracking branch is up to date before force pushing.

### 4. When NOT to Rebase (Shared Branches)

The Golden Rule of Rebasing: **Never rebase commits that have been pushed to a shared branch.**

If you rebase a branch that others have based work on, you create divergent histories that are difficult to reconcile. When someone else pulls your rebased branch, their local history will no longer match the remote, leading to duplicate commits and confusion.

```
What happens if you rebase a shared branch:

Original shared history:
A---B---C (public)
         \
          D---E (someone else's work)

After you rebase public branch:
A---B---C' (rebased public)

Someone else's view after pulling:
A---B---C---D---E (their local)
         \
          C' (your rebased remote)

Result: a merge mess with duplicate commits.
```

Safe to rebase:
- Local commits that have never been pushed
- Your own feature branch that no one else is working on
- When you are certain no one has based work on your branch

Unsafe to rebase:
- Commits on a shared or public branch (main, develop, release)
- Any branch that other team members have pulled and are working with
- Commits that have been reviewed in a pull request that others may have pulled

### Quiz: Rebasing

**Question 1:** What is the primary difference between `git merge` and `git rebase`?

a) Merge creates a linear history while rebase preserves branching
b) Rebase rewrites commit history to create a linear sequence, while merge creates a merge commit preserving branch divergence
c) Rebase can only be used on local branches, while merge works on remote branches
d) There is no difference; they are aliases for the same operation

**Question 2:** You rebase a feature branch onto main and encounter conflicts. What is the correct sequence to resolve them?

a) Edit the files, then run `git rebase --abort`
b) Edit the files, stage them with `git add`, then run `git rebase --continue`
c) Run `git merge --continue` to handle the conflicts
d) Delete the conflicted files and run `git rebase --skip`

**Question 3:** Which of the following scenarios is safe for rebasing?

a) A feature branch that three teammates have pulled and are committing to
b) The main branch that is shared across the entire team
c) A local feature branch that only you are working on and has not been pushed
d) A release branch that is used for deployment by the CI/CD pipeline

---

**Answers:** 1-b, 2-b, 3-c
