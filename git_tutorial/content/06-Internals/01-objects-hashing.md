## Objects and Hashing

Git is fundamentally a content-addressable filesystem. Everything in Git is stored as an object, identified by a SHA-1 hash of its content. Understanding Git objects is key to understanding how Git works internally.

### 1. Git Object Types: Blob, Tree, Commit, Tag

Git has four fundamental object types:

**Blob (Binary Large Object):**
A blob stores the content of a file. It is identified by the SHA-1 hash of the file's content. Blobs do not store filenames or metadata -- they are purely content.

```
Content: "Hello, world!\n"
SHA-1:   8baef1b4abc478178b004d62031cf7fe6db69f93
```

**Tree:**
A tree stores directory listings. It maps filenames to blob hashes (for files) or other tree hashes (for subdirectories). A tree also stores file permissions.

```
100644 blob 8baef1b4... README.md
100755 blob a1b2c3d4... script.sh
040000 tree e4f5g6h7... src/
```

**Commit:**
A commit stores a snapshot of the repository. It contains:
- A pointer to a tree object (the root directory)
- Pointer(s) to parent commit(s)
- Author and committer name, email, timestamp
- Commit message

```
tree 4a5b6c7d8e9f0a...
parent 1a2b3c4d5e6f...
author Alice <alice@example.com> 1705320000 -0500
committer Alice <alice@example.com> 1705320000 -0500

Initial commit with README
```

**Tag (annotated):**
An annotated tag object stores a pointer to a commit, along with metadata. Lightweight tags are not objects -- they are just references in `.git/refs/tags/`.

```
object 4a5b6c7d8e9f0a...
type commit
tag v1.0
tagger Alice <alice@example.com> 1705320000 -0500

Release version 1.0
```

### 2. SHA-1 Hashing

Git uses SHA-1 (Secure Hash Algorithm 1) to generate 40-character hexadecimal hashes for all objects. The hash is computed from the object's type, size, and content.

```
Format: <type> <size>\0<content>

Example for a blob:
"blob 13\0Hello, world!\n"
```

The SHA-1 hash of this content is: `8baef1b4abc478178b004d62031cf7fe6db69f93`

Properties of Git's SHA-1 hashing:
- **Deterministic**: Same content always produces the same hash
- **Collision-resistant**: Extremely unlikely that two different objects produce the same hash
- **Content-addressed**: The hash is the object's identity and address

Git is transitioning to SHA-256 for improved security. As of Git 2.42+, Git supports SHA-256 repositories with `git init --object-format=sha256`.

### 3. .git/objects Directory (Loose Objects)

Git stores objects in the `.git/objects/` directory. The first two characters of the hash form the directory name, and the remaining 38 characters form the filename.

```
.git/objects/
  08/
    baef1b4abc478178b004d62031cf7fe6db69f93
  1a/
    2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b
  4a/
    5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b
  pack/
    pack-a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8.idx
    pack-a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8.pack
  info/
    packs
```

**Storage format:** Each loose object is zlib-compressed and stored in a file named by its hash.

To examine a loose object directly:

```
$ hexdump .git/objects/08/baef1b4abc478178b004d62031cf7fe6db69f93
0000000  78 9c 4b 49 0c 52 30 34 62 60 00 00 00 00 00 00
...
```

### 4. git hash-object, git cat-file

These are plumbing commands that directly interact with the object store.

**git hash-object:**
Computes the SHA-1 hash of a file and optionally stores it as a blob.

```
$ echo "Hello, world!" | git hash-object --stdin
8baef1b4abc478178b004d62031cf7fe6db69f93

$ git hash-object README.md
a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0

$ git hash-object -w README.md
a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0
# The -w flag writes the object to .git/objects/
```

**git cat-file:**
Displays the content or metadata of a Git object.

```
$ git cat-file -p 8baef1b4
Hello, world!

$ git cat-file -p HEAD
tree 4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b
parent 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a
author Alice <alice@example.com> 1705320000 -0500
committer Alice <alice@example.com> 1705320000 -0500

Add README

$ git cat-file -t 8baef1b4
blob

$ git cat-file -s 8baef1b4
13
```

The `-t` flag shows the object type, `-s` shows the size, and `-p` pretty-prints the content.

**Examining a tree object:**

```
$ git cat-file -p HEAD^{tree}
100644 blob a1b2c3d4... README.md
100755 blob e4f5g6h7... script.sh
040000 tree i7j8k9l0... src/
```

**Examining a commit's full tree:**

```
$ git ls-tree -r HEAD
100644 blob a1b2c3d4... README.md
100755 blob e4f5g6h7... script.sh
100644 blob m1n2o3p4... src/main.go
100644 blob q1r2s3t4... src/utils.go
```

### 5. Packfiles

Over time, loose objects accumulate and take up space. Git packs them into packfiles (`.pack`) with an index (`.idx`) for efficiency.

**Packfile structure:**

```
.git/objects/pack/
  pack-a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8.idx   # Index file
  pack-a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8.pack   # Packed objects
```

**How packing works:**
1. Git garbage-collects loose objects: `git gc`
2. Objects are sorted by type and compressed together
3. Delta compression stores differences between similar objects
4. The index file maps object hashes to positions in the packfile

**Manual packing:**

```
$ git gc --aggressive
Counting objects: 1000, done.
Delta compression using up to 8 threads.
Compressing objects: 100% (800/800), done.
Writing objects: 100% (1000/1000), done.
Total 1000 (delta 300), reused 500 (delta 200)
```

**Inspecting packfiles:**

```
$ git verify-pack .git/objects/pack/pack-*.idx
a1b2c3d4... commit 250 200 1000
e4f5g6h7... tree   50 40   800
i7j8k9l0... blob   300 150 500
...

$ git count-objects -v
count: 10
size: 4
in-pack: 1000
packs: 1
size-pack: 500
prune-packable: 0
garbage: 0
size-garbage: 0
```

### 6. Object Storage Summary

The journey of a file through Git's object store:

```
1. File content -> git hash-object -w -> Blob object in .git/objects/
2. git write-tree -> Tree object referencing the blob
3. git commit-tree -> Commit object referencing the tree
4. Over time -> git gc -> Objects packed into packfiles

.git/objects/
  +-- aa/ (first 2 hex chars of hash)
  |   +-- bbbbb... (remaining 38 hex chars) [loose object]
  +-- pack/
  |   +-- pack-XXXXXX.pack  [packed objects]
  |   +-- pack-XXXXXX.idx   [pack index]
  +-- info/
      +-- packs  [list of packfiles]
```

### Quiz: Objects and Hashing

**Question 1:** What is the SHA-1 hash in Git computed from?

a) Only the file content
b) The file name and content together
c) The object type, size, and content concatenated with a null byte
d) A random value assigned by Git at creation time

**Question 2:** Which command would you use to view the content of a tree object in human-readable form?

a) `git show`
b) `git cat-file -p <hash>`
c) `git hash-object -p <hash>`
d) `git read-object <hash>`

**Question 3:** When you run `git gc`, what happens to loose objects in `.git/objects/`?

a) They are deleted permanently
b) They are compressed and combined into packfiles with delta compression
c) They are converted to annotated tags
d) They are uploaded to the remote repository

---

**Answers:** 1-c, 2-b, 3-b
