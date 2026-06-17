## Tagging

Tags in Git are references that point to specific points in a repository's history. They are typically used to mark release points (v1.0, v2.0, etc.). Unlike branches, tags do not move as new commits are added.

### 1. Lightweight vs Annotated Tags

Git supports two types of tags: lightweight and annotated.

**Lightweight tags** are simply a name pointing to a commit. They are like a branch that never moves. They contain no additional metadata.

```
$ git tag v1.0
```

This creates a tag named v1.0 at the current commit. The tag is stored as a reference under `.git/refs/tags/v1.0` and contains only the commit hash.

**Annotated tags** are stored as full objects in Git's object database. They include:
- The tagger name and email
- The date the tag was created
- A tagging message
- Optionally, a GPG signature

```
$ git tag -a v1.0 -m "Release version 1.0"
```

An annotated tag creates a tag object that points to the commit, rather than pointing directly to the commit. Use `git show` to see the tag details:

```
$ git show v1.0
tag v1.0
Tagger: Alice <alice@example.com>
Date:   Mon Jan 15 10:00:00 2026 -0500

Release version 1.0
-----BEGIN PGP SIGNATURE-----

[...signature...]
-----END PGP SIGNATURE-----

commit a1b2c3d4e5f6...
Author: Bob <bob@example.com>
Date:   Mon Jan 15 09:30:00 2026 -0500

    Add login feature
```

When to use lightweight tags:
- Private or temporary tags
- Local bookmarking of commits
- Quick references that don't need metadata

When to use annotated tags:
- Public releases that need release notes
- Tags that need to be signed for verification
- Any tag that will be pushed and shared with a team

### 2. git tag (List, Create, Delete)

**Listing tags:**

```
$ git tag
v1.0
v1.1
v2.0
```

Search for tags matching a pattern:

```
$ git tag -l "v1.*"
v1.0
v1.1
```

List tags with annotations and commits:

```
$ git tag -n
v1.0            Release version 1.0
v1.1            Release version 1.1
v2.0            Major refactor with new API
```

**Creating tags:**

Lightweight tag at current commit:

```
$ git tag v1.0
```

Annotated tag at current commit:

```
$ git tag -a v1.0 -m "Release version 1.0"
```

Tag a specific commit (not the current HEAD):

```
$ git tag -a v0.9 a1b2c3d -m "Beta release"
```

**Deleting tags:**

```
$ git tag -d v1.0
Deleted tag 'v1.0' (was a1b2c3d)
```

### 3. git tag -a (Annotated with Message)

The `-a` flag creates an annotated tag with a message. The `-m` flag provides the message directly; without it, Git opens an editor.

```
$ git tag -a v2.0 -m "Release version 2.0

New features:
- User authentication
- API versioning
- Performance improvements"
```

View the annotated tag details:

```
$ git tag -v v2.0
```

This verifies the tag if it is signed, or shows the tag details if unsigned.

You can also tag after the fact using a commit reference:

```
$ git log --oneline
a1b2c3d Add user authentication
e4f5g6h Fix login page bug
i7j8k9l Initial commit

$ git tag -a v1.0 i7j8k9l -m "Initial release"
```

### 4. Signing Tags (-s)

Tags can be GPG-signed to verify authenticity. This ensures that the tag was created by a trusted identity.

Create a signed tag:

```
$ git tag -s v1.0 -m "Release version 1.0"
```

You need a GPG key configured. Git uses the `user.signingkey` configuration:

```
$ git config --global user.signingkey A1B2C3D4
```

Verify a signed tag:

```
$ git tag -v v1.0
object a1b2c3d4e5f6...
type commit
tag v1.0
tagger Alice <alice@example.com> 1705320000 -0500

Release version 1.0
gpg: Signature made Mon Jan 15 10:00:00 2026 EST
gpg: Good signature from "Alice <alice@example.com>"
```

If the signature is invalid or the key is not trusted:

```
$ git tag -v v1.0
gpg: Can't check signature: No public key
```

You can also force signing all tags with a config option:

```
$ git config --global tag.gpgsign true
```

### 5. Pushing Tags (git push --tags)

Tags are not automatically pushed to remote repositories. You must explicitly push them.

**Push a specific tag:**

```
$ git push origin v1.0
```

**Push all tags:**

```
$ git push --tags
```

This pushes all tags that are not already on the remote.

**Push tags with force (if you need to update a remote tag):**

```
$ git push origin --tags --force
```

Note: Force-pushing tags is dangerous. If others have already fetched the tag, they will have conflicting references.

**Delete a tag on the remote:**

```
$ git push origin --delete v1.0
```

Or:

```
$ git push origin :refs/tags/v1.0
```

**Fetching tags from remote:**

```
$ git fetch --tags
```

This fetches all tags from the remote. Tags are fetched automatically with `git fetch` if they point to commits being fetched, but `--tags` ensures all tags are fetched.

**Checking out a tag:**

```
$ git checkout v1.0
```

This puts you in a detached HEAD state. If you make changes, they are not on any branch. To work from a tag, create a new branch:

```
$ git checkout -b release-v1.0-fixes v1.0
```

### Quiz: Tagging

**Question 1:** What is the primary difference between a lightweight tag and an annotated tag?

a) Lightweight tags can only be local while annotated tags can be pushed
b) Annotated tags are stored as full objects in Git's database with metadata, while lightweight tags are just pointers to commits
c) Lightweight tags support GPG signing while annotated tags do not
d) Annotated tags cannot be deleted

**Question 2:** After creating a tag v2.0 locally, how do you make it available on the remote repository?

a) `git push origin --all`
b) `git push origin v2.0` or `git push --tags`
c) Tags are automatically pushed with `git push`
d) `git push --branch v2.0`

**Question 3:** You run `git checkout v1.0` to examine a previous release. What happens when you make changes?

a) The changes are automatically committed on v1.0
b) The changes are applied to the current branch
c) HEAD becomes detached, and changes are not on any branch
d) Git refuses to make changes on a tag

---

**Answers:** 1-b, 2-b, 3-c
