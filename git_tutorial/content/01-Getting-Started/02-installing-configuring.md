## Installing and Configuring Git

Before you can use Git, you must install it on your machine and configure your identity. This chapter covers installation on all major platforms and walks through every important configuration option.

### 1. Installing Git

**Linux (Debian / Ubuntu / Linux Mint)**

```
$ sudo apt update
$ sudo apt install git
$ git --version
git version 2.34.1
```

For Fedora / RHEL / CentOS:

```
$ sudo dnf install git
```

For Arch Linux:

```
$ sudo pacman -S git
```

**macOS**

The easiest way is via Xcode Command Line Tools:

```
$ xcode-select --install
```

Or use Homebrew:

```
$ brew install git
$ git --version
git version 2.40.1
```

**Windows**

Download the official installer from https://git-scm.com/download/win. During installation:

- Choose "Git Bash" as the terminal emulator
- Select "Checkout as-is, commit as-is" for line endings
- Select "Use Visual Studio Code as default editor" (or your editor of choice)
- After installation, use Git Bash or the Windows Command Prompt

```
$ git --version
git version 2.42.0.windows.2
```

### 2. Configuration Levels

Git reads configuration from three levels. Each level overrides the one above it:

| Level | Scope | File location |
|-------|-------|--------------|
| `--system` | All users on the machine | `/etc/gitconfig` |
| `--global` | Your user account | `~/.gitconfig` or `~/.config/git/config` |
| `--local` | A single repository | `.git/config` (inside the repo) |

Priority order: local > global > system. The most specific level wins.

View all settings:

```
$ git config --list
$ git config --list --global
$ git config --list --local
```

You can also show where each value comes from:

```
$ git config --list --show-origin
```

### 3. Setting Your Identity

The first thing to configure after installing Git is your name and email. Every commit uses this information.

```
$ git config --global user.name "Alice Johnson"
$ git config --global user.email "alice@example.com"
```

Use `--global` so these apply to all repos on your machine. If you need a different identity for a specific project, omit `--global` inside that project:

```
$ cd /path/to/project
$ git config user.name "Alice Work"
$ git config user.email "alice@company.com"
```

### 4. Setting the Default Editor

Git opens an editor when you write commit messages (without `-m`), when resolving conflicts, or when using `git commit --amend`.

Set your preferred editor:

```
$ git config --global core.editor "code --wait"          # VS Code
$ git config --global core.editor "vim"                  # Vim
$ git config --global core.editor "nano"                 # Nano
$ git config --global core.editor "emacs"                # Emacs
```

For VS Code, the `--wait` flag is required because Git needs the editor process to block until you close the file.

### 5. Configuring Line Endings

Different operating systems use different line-ending characters. Git can normalize them automatically.

On Linux/macOS:

```
$ git config --global core.autocrlf input
```

On Windows:

```
$ git config --global core.autocrlf true
```

This ensures files use LF (Linux-style) in Git repositories while Windows users get CRLF in their working directory.

### 6. Useful Configuration Options

**Default branch name** (instead of `master`):

```
$ git config --global init.defaultBranch main
```

**Colorized output**:

```
$ git config --global color.ui auto
```

**Merge tool** (for resolving conflicts):

```
$ git config --global merge.tool vimdiff
$ git config --global merge.tool meld
$ git config --global merge.tool kdiff3
```

**Diff tool**:

```
$ git config --global diff.tool meld
```

**Push behavior** (safer default):

```
$ git config --global push.default simple
```

### 7. Creating Aliases

Aliases save typing by creating shorthand commands.

```
$ git config --global alias.st status
$ git config --global alias.co checkout
$ git config --global alias.br branch
$ git config --global alias.ci commit
$ git config --global alias.lg "log --oneline --graph --all --decorate"
$ git config --global alias.unstage "reset HEAD --"
$ git config --global alias.last "log -1 HEAD"
```

Now you can type `git st` instead of `git status` and `git lg` for a beautified log.

To see all aliases:

```
$ git config --global --get-regexp alias
```

### 8. Checking Configuration

View your complete configuration:

```
$ git config --list --global
user.name=Alice Johnson
user.email=alice@example.com
core.editor=code --wait
init.defaultBranch=main
alias.st=status
alias.lg=log --oneline --graph --all --decorate
```

View a single value:

```
$ git config user.name
Alice Johnson
$ git config --global --get user.email
alice@example.com
```

### Quiz: 3 MCQs

**Q1.** Which configuration level takes priority when the same setting exists in system, global, and local files?

a) System
b) Global
c) Local
d) They merge alphabetically

**Q2.** You run `git config --global user.name "Alice"` and then run `git config user.name "Bob"` inside a repository. What is the value of `user.name` in that repo?

a) Alice
b) Bob
c) An error because global and local conflict
d) It prompts you to choose

**Q3.** What does `git config --global core.autocrlf input` do on Linux?

a) Converts all files to CRLF on checkout
b) Converts CRLF to LF on commit, but does not touch files on checkout
c) Disables line-ending conversion entirely
d) Makes Git ignore all binary files
