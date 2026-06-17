## Ignoring Files

Not every file in a project should be tracked by Git. Compiled binaries, dependencies, editor configuration, and environment files clutter the repository and cause conflicts. Git provides `.gitignore` to automatically exclude files.

### 1. The .gitignore File

`.gitignore` is a plain text file placed in the root of your repository (or in subdirectories). It tells Git which files and directories to ignore.

**Basic rules:**

```
# Comments start with #
# Ignore compiled files
*.o
*.class
*.pyc

# Ignore entire directory
node_modules/
vendor/

# Ignore a specific file
config.local.json

# Ignore files in any directory
.DS_Store
Thumbs.db

# Ignore everything in a specific directory except one file
logs/
!logs/.gitkeep
```

Create and commit the `.gitignore`:

```
$ echo "node_modules/" >> .gitignore
$ git add .gitignore
$ git commit -m "Add .gitignore to exclude node_modules"
```

### 2. .gitignore Pattern Reference

| Pattern | Matches |
|---------|---------|
| `*.log` | All files ending in `.log` anywhere in the repo |
| `/build` | Only `build` in the root directory (not `src/build`) |
| `build/` | All directories named `build` |
| `doc/**/*.pdf` | All PDF files in any subdirectory under `doc/` |
| `!important.pdf` | Negation: do not ignore `important.pdf` (even if `*.pdf` is ignored) |
| `[Tt]emp/` | `Temp/` or `temp/` |
| `*.log.[0-9]` | `.log.0`, `.log.1`, etc. |
| `**/__pycache__/` | `__pycache__/` at any depth |

**Important rules:**

- Trailing `/` means the pattern matches only directories.
- Leading `/` anchors the pattern to the root of the repository.
- An asterisk `*` matches anything except a slash.
- Double asterisk `**` matches any number of directories (including zero).
- Negation (`!`) re-includes a file that was excluded by a previous pattern. Order matters: negation must follow the pattern it is overriding.

### 3. Global .gitignore

Sometimes you want to ignore files across all repositories on your machine (e.g., editor swap files, OS files).

```
$ git config --global core.excludesFile ~/.gitignore_global
$ echo ".DS_Store" >> ~/.gitignore_global
$ echo "*.swp" >> ~/.gitignore_global
```

Now `.DS_Store` and Vim swap files are ignored in every repository without adding them to each project's `.gitignore`.

### 4. Checking Why a File is Ignored

Use `git check-ignore` to determine if a file is being ignored and which rule applies:

```
$ git check-ignore -v node_modules/express/package.json
.gitignore:2:node_modules/  node_modules/express/package.json
```

The output shows the source file, line number, pattern, and matched path.

Check multiple files:

```
$ git check-ignore -v *.log config.env
```

If a file is not ignored, `git check-ignore` exits with status 1 and produces no output.

### 5. Ignoring Files That Are Already Tracked

If you add a file to `.gitignore` after it is already being tracked, Git still tracks it. `.gitignore` only applies to untracked files.

To stop tracking a tracked file (without deleting it from disk):

```
$ git rm --cached secrets.env
$ echo "secrets.env" >> .gitignore
$ git add .gitignore
$ git commit -m "Stop tracking secrets.env"
```

For files that you want Git to pretend are unchanged (useful for config files that differ per environment):

```
$ git update-index --assume-unchanged config.json
$ git update-index --skip-worktree config.json
```

- `--assume-unchanged`: Tells Git that this file should not be checked for changes. Use when the file is expensive to check or you never want to commit changes to it.
- `--skip-worktree`: Similar but safer for files that should remain modified locally. Use for config files that are customized per environment.

Undo these flags:

```
$ git update-index --no-assume-unchanged config.json
$ git update-index --no-skip-worktree config.json
```

List files with the flag set:

```
$ git ls-files -v | grep '^[a-z]'      # assume-unchanged files
$ git ls-files -v | grep '^S'           # skip-worktree files
```

### 6. .gitignore Templates

GitHub maintains a collection of `.gitignore` templates for different languages and frameworks:

https://github.com/github/gitignore

You can use them as starting points. For example, for a Node.js project:

```
# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
```

To initialize a project with a template:

```
$ curl -O https://raw.githubusercontent.com/github/gitignore/main/Node.gitignore
$ mv Node.gitignore .gitignore
```

### 7. Repo-Level Excludes: .git/info/exclude

The `.git/info/exclude` file works like `.gitignore` but is NOT committed. It is specific to your local clone.

```
$ cat .git/info/exclude
# git ls-files --others --exclude-from=.git/info/exclude
# Lines that start with '#' are comments.
# For a project-local ignore, use .gitignore.
.DS_Store
*.swp
```

Use this for personal ignore rules that should not affect collaborators.

### Quiz: 3 MCQs

**Q1.** You have a file `config.env` that is already tracked by Git. You add `config.env` to `.gitignore`. Why is the file still tracked?

a) .gitignore only applies to files in subdirectories
b) .gitignore does not affect files that are already tracked by Git
c) You need to run `git config core.ignore true` first
d) .gitignore only works for files with extensions

**Q2.** What does the pattern `build/` in .gitignore match?

a) Only a file named `build` in the root directory
b) Only a directory named `build` in the root directory
c) Any directory named `build` anywhere in the repository
d) Any file or directory named `build` anywhere

**Q3.** You run `git check-ignore -v dist/bundle.js` and get no output. What does this mean?

a) `dist/bundle.js` is ignored by a rule in .gitignore
b) The file does not exist
c) `dist/bundle.js` is NOT ignored by any rule
d) The check-ignore command failed
