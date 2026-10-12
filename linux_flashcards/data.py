"""
Comprehensive database of Linux terminal commands for flashcard study, quizzes, and command challenges.
"""

CATEGORIES = [
    "Files & Navigation",
    "Viewing & Text Processing",
    "System Info & Performance",
    "Process Control",
    "Permissions & Security",
    "Networking & Web",
    "Archiving & Compression",
    "Pipes, Redirection & Utilities",
    "Services & Logs",
    "Disk & Storage Management",
]

DIFFICULTIES = ["Beginner", "Intermediate", "Advanced"]

COMMANDS = [
    # ==========================================
    # Category: Files & Navigation
    # ==========================================
    {
        "id": "pwd",
        "name": "pwd",
        "category": "Files & Navigation",
        "difficulty": "Beginner",
        "summary": "Print the current working directory path.",
        "description": "Outputs the full absolute pathname of the current working directory from the root directory (/)",
        "syntax": "pwd [OPTIONS]",
        "flags": {
            "-L": "Use PWD from environment, even if it contains symlinks (logical path).",
            "-P": "Avoid all symlinks and print the physical directory path.",
        },
        "examples": [
            {"cmd": "pwd", "desc": "Display the current directory path"},
            {"cmd": "pwd -P", "desc": "Resolve symlinks and print real physical path"},
        ],
        "hint": "Mnemonic: 'Print Working Directory'.",
        "challenge": {
            "scenario": "Display the exact physical path of the current directory, resolving any symbolic links.",
            "canonical": "pwd -P",
            "alternatives": ["pwd -P"],
            "keywords": ["pwd", "-P"],
        },
    },
    {
        "id": "ls",
        "name": "ls",
        "category": "Files & Navigation",
        "difficulty": "Beginner",
        "summary": "List directory contents with details and hidden files.",
        "description": "Lists files and directories. Supports sorting, permissions display, human-readable file sizes, and recursive traversal.",
        "syntax": "ls [OPTIONS] [FILE/DIR...]",
        "flags": {
            "-l": "Use a long listing format (permissions, owner, size, modification date).",
            "-a": "Do not ignore entries starting with . (show hidden files).",
            "-h": "With -l, print sizes in human readable format (e.g., 1K 234M 2G).",
            "-t": "Sort by modification time, newest first.",
            "-R": "List subdirectories recursively.",
            "-r": "Reverse order while sorting.",
        },
        "examples": [
            {"cmd": "ls -la", "desc": "Long list of all files, including hidden dotfiles"},
            {"cmd": "ls -lh", "desc": "Long list with human-readable file sizes (MB, GB)"},
            {"cmd": "ls -lt", "desc": "Sort by modification time (most recent first)"},
            {"cmd": "ls -lR", "desc": "Recursively list directory contents"},
        ],
        "hint": "Combine flags: -la or -lh are the most frequently used.",
        "challenge": {
            "scenario": "List all files including hidden ones in long format with human-readable file sizes.",
            "canonical": "ls -lah",
            "alternatives": ["ls -lha", "ls -alh", "ls -ahl", "ls -la -h", "ls -l -a -h"],
            "keywords": ["ls", "-l", "-a", "-h"],
        },
    },
    {
        "id": "cd",
        "name": "cd",
        "category": "Files & Navigation",
        "difficulty": "Beginner",
        "summary": "Change the current shell working directory.",
        "description": "A shell builtin command that navigates between directories in the filesystem hierarchy.",
        "syntax": "cd [DIRECTORY]",
        "flags": {
            "~": "Shortcut to navigate to the current user's home directory ($HOME).",
            "-": "Navigate to the previous working directory ($OLDPWD).",
            "..": "Move up one directory level to the parent directory.",
        },
        "examples": [
            {"cmd": "cd /var/log", "desc": "Switch to /var/log directory"},
            {"cmd": "cd ~", "desc": "Switch to your user home directory"},
            {"cmd": "cd -", "desc": "Toggle back to the previous directory you were in"},
            {"cmd": "cd ..", "desc": "Move up one level to parent folder"},
        ],
        "hint": "Mnemonic: 'Change Directory'. 'cd -' is a lifesaver for hopping back and forth.",
        "challenge": {
            "scenario": "Return to the previous directory you were working in.",
            "canonical": "cd -",
            "alternatives": ["cd -"],
            "keywords": ["cd", "-"],
        },
    },
    {
        "id": "cp",
        "name": "cp",
        "category": "Files & Navigation",
        "difficulty": "Beginner",
        "summary": "Copy files and directories.",
        "description": "Copies SOURCE to DEST, or multiple SOURCEs to a DIRECTORY. Requires -r or -R to copy folders recursively.",
        "syntax": "cp [OPTIONS] SOURCE DEST",
        "flags": {
            "-r, -R": "Copy directories recursively.",
            "-i": "Prompt before overwrite (interactive).",
            "-p": "Preserve specified attributes (mode, ownership, timestamps).",
            "-a": "Archive mode; preserves all file metadata, recursion, and links.",
            "-u": "Update: copy only when SOURCE is newer than DEST or DEST is missing.",
            "-v": "Verbose: explain what is being done.",
        },
        "examples": [
            {"cmd": "cp file.txt backup.txt", "desc": "Copy file.txt to backup.txt"},
            {"cmd": "cp -r project/ project_backup/", "desc": "Recursively copy directory project/"},
            {"cmd": "cp -a src/ dst/", "desc": "Archive copy preserving all permissions and symlinks"},
        ],
        "hint": "Use -a (archive) for full backups to preserve timestamps and ownership.",
        "challenge": {
            "scenario": "Recursively copy directory 'src' to 'backup' preserving all file attributes and permissions.",
            "canonical": "cp -a src backup",
            "alternatives": ["cp -a src/ backup/", "cp -a src backup/", "cp -rp src backup", "cp -a src/ backup"],
            "keywords": ["cp", "-a", "src", "backup"],
        },
    },
    {
        "id": "mv",
        "name": "mv",
        "category": "Files & Navigation",
        "difficulty": "Beginner",
        "summary": "Move or rename files and directories.",
        "description": "Renames SOURCE to DEST, or moves SOURCE(s) into DIRECTORY. Does not duplicate data when on the same filesystem.",
        "syntax": "mv [OPTIONS] SOURCE DEST",
        "flags": {
            "-i": "Prompt before overwrite.",
            "-n": "Do not overwrite an existing file (no-clobber).",
            "-u": "Update: move only when SOURCE is newer than destination file.",
            "-v": "Verbose output explaining what is moved.",
        },
        "examples": [
            {"cmd": "mv oldname.txt newname.txt", "desc": "Rename oldname.txt to newname.txt"},
            {"cmd": "mv *.log /var/log/archive/", "desc": "Move all .log files into archive folder"},
            {"cmd": "mv -i file.txt destination/", "desc": "Move file prompting before any overwrite"},
        ],
        "hint": "Moving a file in the same directory acts as renaming it.",
        "challenge": {
            "scenario": "Rename file 'draft.txt' to 'final.txt' safely with a prompt before overwriting an existing file.",
            "canonical": "mv -i draft.txt final.txt",
            "alternatives": ["mv -i draft.txt final.txt"],
            "keywords": ["mv", "-i", "draft.txt", "final.txt"],
        },
    },
    {
        "id": "rm",
        "name": "rm",
        "category": "Files & Navigation",
        "difficulty": "Beginner",
        "summary": "Remove (delete) files or directories.",
        "description": "Deletes specified files. Cannot be undone via standard Trash. Folders require -r (recursive).",
        "syntax": "rm [OPTIONS] FILE...",
        "flags": {
            "-r, -R": "Remove directories and their contents recursively.",
            "-f": "Force: ignore nonexistent files, never prompt before removing.",
            "-i": "Prompt before every removal.",
            "-I": "Prompt once before removing more than three files, or when recursing.",
            "-d": "Remove empty directories.",
        },
        "examples": [
            {"cmd": "rm temp.log", "desc": "Delete temp.log file"},
            {"cmd": "rm -rf build_cache/", "desc": "Force remove directory and all contents recursively without prompting"},
            {"cmd": "rm -i sensitive.key", "desc": "Prompt for confirmation before deletion"},
        ],
        "hint": "Be very careful with 'rm -rf' — Linux has no built-in undo for rm!",
        "challenge": {
            "scenario": "Recursively and forcefully remove the directory 'temp_build' without confirmation prompts.",
            "canonical": "rm -rf temp_build",
            "alternatives": ["rm -fr temp_build", "rm -r -f temp_build", "rm -rf temp_build/"],
            "keywords": ["rm", "-rf", "temp_build"],
        },
    },
    {
        "id": "mkdir",
        "name": "mkdir",
        "category": "Files & Navigation",
        "difficulty": "Beginner",
        "summary": "Create new directories.",
        "description": "Creates directory if it does not already exist. The -p flag creates parent directories as needed.",
        "syntax": "mkdir [OPTIONS] DIRECTORY...",
        "flags": {
            "-p": "Create intermediate parent directories as needed; no error if existing.",
            "-m": "Set file mode (permissions) directly (e.g., -m 755).",
            "-v": "Print a message for each created directory.",
        },
        "examples": [
            {"cmd": "mkdir projects", "desc": "Create a single directory named projects"},
            {"cmd": "mkdir -p app/src/components", "desc": "Create nested directory structure in one command"},
            {"cmd": "mkdir -m 700 private_keys", "desc": "Create folder with strict read/write/exec permissions for owner only"},
        ],
        "hint": "Mnemonic: 'Make Directory'. -p stands for 'parents'.",
        "challenge": {
            "scenario": "Create a nested directory path 'data/raw/2026' creating any missing parent folders.",
            "canonical": "mkdir -p data/raw/2026",
            "alternatives": ["mkdir -p data/raw/2026/"],
            "keywords": ["mkdir", "-p", "data/raw/2026"],
        },
    },
    {
        "id": "touch",
        "name": "touch",
        "category": "Files & Navigation",
        "difficulty": "Beginner",
        "summary": "Update file timestamps or create empty files.",
        "description": "Changes file access and modification times to the current time. If file does not exist, an empty file is created.",
        "syntax": "touch [OPTIONS] FILE...",
        "flags": {
            "-a": "Change only the access time.",
            "-m": "Change only the modification time.",
            "-c, --no-create": "Do not create any files if they do not exist.",
            "-d, --date=STRING": "Parse STRING and use it instead of current time.",
        },
        "examples": [
            {"cmd": "touch app.py", "desc": "Create empty app.py or update its timestamp if it exists"},
            {"cmd": "touch -c missing.txt", "desc": "Update timestamp only if missing.txt exists; don't create it"},
            {"cmd": "touch file1 file2 file3", "desc": "Create multiple empty files at once"},
        ],
        "hint": "Widely used to quickly scaffold placeholder files.",
        "challenge": {
            "scenario": "Create an empty file named '.env' or update its timestamp if it already exists.",
            "canonical": "touch .env",
            "alternatives": ["touch .env"],
            "keywords": ["touch", ".env"],
        },
    },
    {
        "id": "find",
        "name": "find",
        "category": "Files & Navigation",
        "difficulty": "Intermediate",
        "summary": "Search for files in a directory hierarchy based on attributes.",
        "description": "Searches for files matching criteria like name patterns, size, modification time, ownership, and permissions.",
        "syntax": "find [PATH] [CRITERIA] [ACTIONS]",
        "flags": {
            "-name PATTERN": "Base of file name matches shell pattern (case-sensitive).",
            "-iname PATTERN": "Case-insensitive name search.",
            "-type [f|d|l]": "Filter by file type (f=regular file, d=directory, l=symlink).",
            "-mtime -N/+N": "Modified less than / more than N days ago.",
            "-size [+/-]N[c|k|M|G]": "Filter by file size (e.g., +100M).",
            "-exec CMD {} +": "Execute CMD on each found file.",
        },
        "examples": [
            {"cmd": "find . -name \"*.py\"", "desc": "Find all Python files in current directory tree"},
            {"cmd": "find /var/log -type f -mtime -7", "desc": "Find regular files in /var/log modified in the last 7 days"},
            {"cmd": "find . -type f -size +50M", "desc": "Find files larger than 50 megabytes"},
            {"cmd": "find . -name \"*.tmp\" -delete", "desc": "Find and delete all temporary files"},
        ],
        "hint": "Always quote wildcard patterns like \"*.log\" so the shell doesn't expand them prematurely.",
        "challenge": {
            "scenario": "Find all regular files ending with '.log' in '/var/log' modified within the last 7 days.",
            "canonical": "find /var/log -type f -name \"*.log\" -mtime -7",
            "alternatives": [
                "find /var/log -name \"*.log\" -type f -mtime -7",
                "find /var/log -type f -name '*.log' -mtime -7",
                "find /var/log -mtime -7 -type f -name \"*.log\"",
            ],
            "keywords": ["find", "/var/log", "-type f", "*.log", "-mtime -7"],
        },
    },
    {
        "id": "tree",
        "name": "tree",
        "category": "Files & Navigation",
        "difficulty": "Intermediate",
        "summary": "List directory contents in a tree-like ASCII structure.",
        "description": "Produces a visual depth-indented directory tree listing with file and folder counts.",
        "syntax": "tree [OPTIONS] [DIRECTORY]",
        "flags": {
            "-L LEVEL": "Max display depth of the directory tree.",
            "-a": "All files are printed, including hidden files.",
            "-d": "List directories only.",
            "-I PATTERN": "Do not list files that match the given pattern (e.g., -I 'node_modules').",
        },
        "examples": [
            {"cmd": "tree", "desc": "Render the full folder structure"},
            {"cmd": "tree -L 2", "desc": "Display directory tree up to 2 levels deep"},
            {"cmd": "tree -d", "desc": "Display directory structure only, omitting files"},
        ],
        "hint": "Use '-L 2' to avoid terminal spam on deep directories like node_modules or .git.",
        "challenge": {
            "scenario": "Display a directory tree showing only folders (no files) up to 2 levels deep.",
            "canonical": "tree -d -L 2",
            "alternatives": ["tree -L 2 -d", "tree -dL 2"],
            "keywords": ["tree", "-d", "-L 2"],
        },
    },
    {
        "id": "ln",
        "name": "ln",
        "category": "Files & Navigation",
        "difficulty": "Intermediate",
        "summary": "Make links between files (symbolic or hard).",
        "description": "Creates links. By default creates hard links; with -s creates symbolic (soft) links pointing to target path.",
        "syntax": "ln [OPTIONS] TARGET LINK_NAME",
        "flags": {
            "-s": "Make symbolic (soft) links instead of hard links.",
            "-f": "Remove existing destination files (force).",
            "-v": "Verbose: print name of each linked file.",
        },
        "examples": [
            {"cmd": "ln -s /etc/nginx/sites-available/app /etc/nginx/sites-enabled/", "desc": "Create symlink in sites-enabled"},
            {"cmd": "ln -sf target.txt link.txt", "desc": "Create or overwrite symbolic link"},
        ],
        "hint": "Always use 'ln -s TARGET LINK'. Target comes first, link name second.",
        "challenge": {
            "scenario": "Create a symbolic link named 'python' pointing to '/usr/bin/python3'.",
            "canonical": "ln -s /usr/bin/python3 python",
            "alternatives": ["ln -s /usr/bin/python3 ./python"],
            "keywords": ["ln", "-s", "/usr/bin/python3", "python"],
        },
    },

    # ==========================================
    # Category: Viewing & Text Processing
    # ==========================================
    {
        "id": "cat",
        "name": "cat",
        "category": "Viewing & Text Processing",
        "difficulty": "Beginner",
        "summary": "Concatenate files and print on the standard output.",
        "description": "Reads files sequentially and outputs their content to stdout. Useful for viewing short files or concatenating.",
        "syntax": "cat [OPTIONS] [FILE...]",
        "flags": {
            "-n": "Number all output lines.",
            "-b": "Number nonempty output lines only.",
            "-E": "Display $ at end of each line.",
            "-s": "Suppress repeated empty output lines (squeeze).",
        },
        "examples": [
            {"cmd": "cat file.txt", "desc": "Print contents of file.txt to terminal"},
            {"cmd": "cat -n script.py", "desc": "Display file contents with line numbers"},
            {"cmd": "cat part1.txt part2.txt > full.txt", "desc": "Concatenate two files into one"},
        ],
        "hint": "Mnemonic: 'conCATenate'. For large files, prefer 'less' or 'head'/'tail'.",
        "challenge": {
            "scenario": "Display the contents of 'server.log' with line numbers on every line.",
            "canonical": "cat -n server.log",
            "alternatives": ["cat -n server.log"],
            "keywords": ["cat", "-n", "server.log"],
        },
    },
    {
        "id": "less",
        "name": "less",
        "category": "Viewing & Text Processing",
        "difficulty": "Beginner",
        "summary": "Opposite of 'more' — view file contents interactively one page at a time.",
        "description": "Terminal pager that allows backwards and forward scrolling, searching (/ for forward, ? for backward), and fast memory usage.",
        "syntax": "less [OPTIONS] FILE",
        "flags": {
            "-N": "Show line numbers on each line.",
            "-S": "Chop long lines rather than wrapping them.",
            "+F": "Continuously monitor and scroll new appended data (like tail -f).",
        },
        "examples": [
            {"cmd": "less bigfile.log", "desc": "Browse large file page by page (q to quit)"},
            {"cmd": "less -N code.py", "desc": "View file with line numbers"},
        ],
        "hint": "Inside less: '/' to search, 'n' for next match, 'q' to quit, 'G' for bottom, 'g' for top.",
        "challenge": {
            "scenario": "Open 'access.log' with line numbers displayed in an interactive pager.",
            "canonical": "less -N access.log",
            "alternatives": ["less -N access.log"],
            "keywords": ["less", "-N", "access.log"],
        },
    },
    {
        "id": "head",
        "name": "head",
        "category": "Viewing & Text Processing",
        "difficulty": "Beginner",
        "summary": "Output the first part of files (default first 10 lines).",
        "description": "Prints the beginning of files to standard output. Useful for quickly previewing headers or top rows.",
        "syntax": "head [OPTIONS] [FILE...]",
        "flags": {
            "-n [K]": "Print the first K lines instead of default 10.",
            "-c [K]": "Print the first K bytes.",
        },
        "examples": [
            {"cmd": "head data.csv", "desc": "Print first 10 lines of data.csv"},
            {"cmd": "head -n 25 error.log", "desc": "Print first 25 lines of error.log"},
        ],
        "hint": "Default line count is 10 if -n is omitted.",
        "challenge": {
            "scenario": "View the first 20 lines of 'config.yml'.",
            "canonical": "head -n 20 config.yml",
            "alternatives": ["head -20 config.yml", "head -n20 config.yml"],
            "keywords": ["head", "20", "config.yml"],
        },
    },
    {
        "id": "tail",
        "name": "tail",
        "category": "Viewing & Text Processing",
        "difficulty": "Beginner",
        "summary": "Output the last part of files (default last 10 lines) or follow live changes.",
        "description": "Prints the end of files. With -f, follows appended data in real-time, making it essential for watching server logs.",
        "syntax": "tail [OPTIONS] [FILE...]",
        "flags": {
            "-f": "Follow: output appended data as the file grows.",
            "-F": "Follow and retry: keep trying if file is rotated or temporarily unavailable.",
            "-n [K]": "Output the last K lines, instead of the last 10.",
        },
        "examples": [
            {"cmd": "tail -f /var/log/syslog", "desc": "Stream real-time log updates"},
            {"cmd": "tail -n 50 app.log", "desc": "Show last 50 lines of app.log"},
            {"cmd": "tail -n 100 -f access.log", "desc": "Show last 100 lines and keep following new entries"},
        ],
        "hint": "Ctrl+C exits a running 'tail -f' stream.",
        "challenge": {
            "scenario": "Monitor '/var/log/nginx/access.log' in real-time starting with the last 50 lines.",
            "canonical": "tail -n 50 -f /var/log/nginx/access.log",
            "alternatives": [
                "tail -f -n 50 /var/log/nginx/access.log",
                "tail -50f /var/log/nginx/access.log",
                "tail -fn 50 /var/log/nginx/access.log",
            ],
            "keywords": ["tail", "-f", "50", "/var/log/nginx/access.log"],
        },
    },
    {
        "id": "grep",
        "name": "grep",
        "category": "Viewing & Text Processing",
        "difficulty": "Beginner",
        "summary": "Search text using regular expressions and print matching lines.",
        "description": "Global Regular Expression Print. Searches input files for lines matching a pattern and writes them to standard output.",
        "syntax": "grep [OPTIONS] PATTERN [FILE...]",
        "flags": {
            "-i": "Ignore case distinctions in patterns and input.",
            "-r, -R": "Read all files under each directory recursively.",
            "-n": "Prefix each line of output with the 1-based line number.",
            "-v": "Invert the sense of matching, to select non-matching lines.",
            "-c": "Suppress normal output; print a count of matching lines.",
            "-l": "Print only names of FILEs with matching lines.",
            "-E": "Interpret PATTERN as an extended regular expression (like egrep).",
        },
        "examples": [
            {"cmd": "grep -i \"error\" /var/log/syslog", "desc": "Case-insensitive search for 'error'"},
            {"cmd": "grep -rn \"TODO\" src/", "desc": "Search recursively in src/ showing line numbers"},
            {"cmd": "grep -v \"#\" config.conf", "desc": "Filter out commented lines starting with #"},
            {"cmd": "grep -c \"404\" access.log", "desc": "Count how many lines contain 404"},
        ],
        "hint": "Mnemonic: 'Global Regular Expression Print'. '-rn' is great for codebase searches.",
        "challenge": {
            "scenario": "Recursively search for the string 'FATAL' case-insensitively in 'src/' displaying line numbers.",
            "canonical": "grep -rni \"FATAL\" src/",
            "alternatives": [
                "grep -rin \"FATAL\" src/",
                "grep -rni FATAL src/",
                "grep -rin FATAL src/",
                "grep -rn -i \"FATAL\" src/",
                "grep -r -n -i \"FATAL\" src/",
            ],
            "keywords": ["grep", "-r", "-n", "-i", "FATAL", "src"],
        },
    },
    {
        "id": "wc",
        "name": "wc",
        "category": "Viewing & Text Processing",
        "difficulty": "Beginner",
        "summary": "Print newline, word, and byte counts for each file.",
        "description": "Word Count. Analyzes files or standard input and tallies lines, words, characters, or bytes.",
        "syntax": "wc [OPTIONS] [FILE...]",
        "flags": {
            "-l": "Print the newline counts (number of lines).",
            "-w": "Print the word counts.",
            "-c": "Print the byte counts.",
            "-m": "Print the character counts.",
        },
        "examples": [
            {"cmd": "wc -l access.log", "desc": "Count the number of lines in access.log"},
            {"cmd": "ls | wc -l", "desc": "Count number of files and directories in current folder"},
            {"cmd": "wc -w essay.txt", "desc": "Count total words in essay.txt"},
        ],
        "hint": "Pipe into 'wc -l' to count items in any list.",
        "challenge": {
            "scenario": "Count the number of lines in file 'dataset.csv'.",
            "canonical": "wc -l dataset.csv",
            "alternatives": ["wc -l dataset.csv"],
            "keywords": ["wc", "-l", "dataset.csv"],
        },
    },
    {
        "id": "sort",
        "name": "sort",
        "category": "Viewing & Text Processing",
        "difficulty": "Intermediate",
        "summary": "Sort lines of text files alphabetically or numerically.",
        "description": "Sorts lines from standard input or files and writes sorted result to standard output.",
        "syntax": "sort [OPTIONS] [FILE...]",
        "flags": {
            "-n": "Compare according to string numerical value (e.g., 2 before 10).",
            "-r": "Reverse the result of comparisons (descending).",
            "-u": "Output only unique lines.",
            "-k POS1[,POS2]": "Sort via a key/column position.",
            "-t SEP": "Use SEP as field delimiter.",
        },
        "examples": [
            {"cmd": "sort names.txt", "desc": "Sort lines alphabetically"},
            {"cmd": "sort -n scores.txt", "desc": "Sort numbers numerically instead of lexicographically"},
            {"cmd": "sort -nr values.txt", "desc": "Sort numbers numerically in descending order"},
            {"cmd": "sort -t: -k3 -n /etc/passwd", "desc": "Sort passwd by UID (3rd field delimited by :)"},
        ],
        "hint": "Always add -n when sorting numbers, or 100 will sort before 20!",
        "challenge": {
            "scenario": "Sort lines in 'scores.txt' in reverse (descending) numerical order.",
            "canonical": "sort -nr scores.txt",
            "alternatives": ["sort -rn scores.txt", "sort -n -r scores.txt", "sort -r -n scores.txt"],
            "keywords": ["sort", "-n", "-r", "scores.txt"],
        },
    },
    {
        "id": "uniq",
        "name": "uniq",
        "category": "Viewing & Text Processing",
        "difficulty": "Intermediate",
        "summary": "Report or omit repeated adjacent lines.",
        "description": "Filters adjacent matching lines from INPUT. Note: non-adjacent duplicates must be sorted first!",
        "syntax": "uniq [OPTIONS] [INPUT [OUTPUT]]",
        "flags": {
            "-c": "Prefix lines by the number of occurrences.",
            "-d": "Only print duplicate lines.",
            "-u": "Only print unique lines (lines that appeared only once).",
            "-i": "Ignore differences in case when comparing.",
        },
        "examples": [
            {"cmd": "sort ip_list.txt | uniq", "desc": "Deduplicate IP addresses"},
            {"cmd": "sort log.txt | uniq -c | sort -nr", "desc": "Count frequency of lines, sorted highest to lowest"},
            {"cmd": "sort users.txt | uniq -d", "desc": "List only users that appear more than once"},
        ],
        "hint": "Remember to run through 'sort' first, because 'uniq' only checks adjacent lines.",
        "challenge": {
            "scenario": "Count the occurrences of each unique line in 'visitors.txt' (assuming it is already sorted).",
            "canonical": "uniq -c visitors.txt",
            "alternatives": ["uniq -c visitors.txt"],
            "keywords": ["uniq", "-c", "visitors.txt"],
        },
    },
    {
        "id": "cut",
        "name": "cut",
        "category": "Viewing & Text Processing",
        "difficulty": "Intermediate",
        "summary": "Remove sections from each line of files (columns / fields).",
        "description": "Extracts fields delimited by a character or character byte positions from each line of standard input or files.",
        "syntax": "cut [OPTIONS] [FILE...]",
        "flags": {
            "-d DELIM": "Use DELIM instead of TAB for field delimiter.",
            "-f LIST": "Select only these fields (columns).",
            "-c LIST": "Select only these character positions.",
        },
        "examples": [
            {"cmd": "cut -d: -f1 /etc/passwd", "desc": "Extract list of all usernames from /etc/passwd"},
            {"cmd": "cut -d',' -f1,3 data.csv", "desc": "Extract columns 1 and 3 from comma-separated CSV"},
            {"cmd": "cut -c1-10 logs.txt", "desc": "Extract the first 10 characters of each line"},
        ],
        "hint": "-d sets delimiter, -f chooses field numbers (1-indexed).",
        "challenge": {
            "scenario": "Extract the 1st column (usernames) from '/etc/passwd' which uses ':' as delimiter.",
            "canonical": "cut -d: -f1 /etc/passwd",
            "alternatives": ["cut -d':' -f1 /etc/passwd", "cut -d : -f 1 /etc/passwd"],
            "keywords": ["cut", "-d", ":", "-f1", "/etc/passwd"],
        },
    },
    {
        "id": "sed",
        "name": "sed",
        "category": "Viewing & Text Processing",
        "difficulty": "Advanced",
        "summary": "Stream editor for filtering and transforming text.",
        "description": "Performs text transformations on an input stream (a file or input from a pipeline) using regex substitutions.",
        "syntax": "sed [OPTIONS] 'COMMAND' [FILE...]",
        "flags": {
            "-i": "Edit files in place (directly update file on disk).",
            "-e SCRIPT": "Add the script to the commands to be executed.",
            "-n": "Suppress automatic printing of pattern space.",
        },
        "examples": [
            {"cmd": "sed 's/foo/bar/g' file.txt", "desc": "Replace all occurrences of 'foo' with 'bar' and print output"},
            {"cmd": "sed -i 's/localhost/127.0.0.1/g' config.env", "desc": "In-place replace localhost in config.env"},
            {"cmd": "sed -n '10,20p' document.txt", "desc": "Print lines 10 through 20 only"},
        ],
        "hint": "Syntax: sed 's/search/replace/g'. Flag 'g' replaces globally on each line.",
        "challenge": {
            "scenario": "Replace all occurrences of 'http://' with 'https://' inside 'config.json' directly in-place.",
            "canonical": "sed -i 's#http://#https://#g' config.json",
            "alternatives": [
                "sed -i 's/http:\\/\\//https:\\/\\//g' config.json",
                "sed -i 's|http://|https://|g' config.json",
                "sed -i 's#http://#https://#g' config.json",
            ],
            "keywords": ["sed", "-i", "http", "https", "config.json"],
        },
    },
    {
        "id": "awk",
        "name": "awk",
        "category": "Viewing & Text Processing",
        "difficulty": "Advanced",
        "summary": "Pattern scanning and text column processing language.",
        "description": "A powerful data extraction and reporting tool. Splits input into fields ($1, $2, ... $NF) by whitespace or custom delimiter.",
        "syntax": "awk [OPTIONS] 'PATTERN {ACTION}' [FILE...]",
        "flags": {
            "-F FS": "Use FS as the input field separator (default is whitespace).",
            "-v VAR=VAL": "Assign value to variable before execution.",
        },
        "examples": [
            {"cmd": "awk '{print $1}' access.log", "desc": "Print the first column (e.g. client IP) of every line"},
            {"cmd": "awk -F: '{print $1, $7}' /etc/passwd", "desc": "Print usernames and default shells separated by colon"},
            {"cmd": "awk '$3 > 100 {print $1, $3}' data.txt", "desc": "Print column 1 and 3 where column 3 is greater than 100"},
            {"cmd": "awk '{sum += $2} END {print sum}' numbers.txt", "desc": "Calculate the sum of all numbers in column 2"},
        ],
        "hint": "$0 is the whole line, $1 is column 1, $NF is the last column, NR is line number.",
        "challenge": {
            "scenario": "Print the 2nd column of each line in 'report.txt' using default whitespace delimiter.",
            "canonical": "awk '{print $2}' report.txt",
            "alternatives": ["awk '{print $2}' report.txt", "awk '{ print $2 }' report.txt"],
            "keywords": ["awk", "{print $2}", "report.txt"],
        },
    },

    # ==========================================
    # Category: System Info & Performance
    # ==========================================
    {
        "id": "uname",
        "name": "uname",
        "category": "System Info & Performance",
        "difficulty": "Beginner",
        "summary": "Print system information and kernel version.",
        "description": "Prints information about the machine architecture, OS kernel name, release version, and hostname.",
        "syntax": "uname [OPTIONS]",
        "flags": {
            "-a": "Print all system info (kernel name, network node hostname, kernel release, version, machine architecture).",
            "-r": "Print the kernel release version.",
            "-m": "Print the machine hardware architecture (e.g., x86_64, aarch64).",
        },
        "examples": [
            {"cmd": "uname -a", "desc": "Display full kernel and system architecture information"},
            {"cmd": "uname -r", "desc": "Display current Linux kernel release version"},
        ],
        "hint": "Mnemonic: 'Unix NAME'. '-a' gives you everything at a glance.",
        "challenge": {
            "scenario": "Print all operating system and kernel release details.",
            "canonical": "uname -a",
            "alternatives": ["uname -a"],
            "keywords": ["uname", "-a"],
        },
    },
    {
        "id": "top",
        "name": "top",
        "category": "System Info & Performance",
        "difficulty": "Beginner",
        "summary": "Display real-time Linux processes and system resource usage.",
        "description": "Provides an ongoing live look at CPU usage, memory utilization, load average, and active threads.",
        "syntax": "top [OPTIONS]",
        "flags": {
            "-b": "Batch mode: suitable for sending output to other programs or a file.",
            "-n [NUM]": "Number of iterations to exit after.",
            "-p [PID]": "Monitor only the specified process ID.",
            "-u [USER]": "Monitor processes owned by the given user.",
        },
        "examples": [
            {"cmd": "top", "desc": "Open interactive process monitor (q to quit)"},
            {"cmd": "top -u www-data", "desc": "Monitor processes owned by user www-data"},
            {"cmd": "top -b -n 1 > snapshot.txt", "desc": "Capture single batch snapshot of system resources"},
        ],
        "hint": "Inside top: 'M' sorts by memory, 'P' sorts by CPU, 'k' kills a process, 'q' quits.",
        "challenge": {
            "scenario": "Run top in batch mode for exactly 1 iteration to capture a single snapshot.",
            "canonical": "top -b -n 1",
            "alternatives": ["top -bn 1", "top -b -n1", "top -bn1"],
            "keywords": ["top", "-b", "-n", "1"],
        },
    },
    {
        "id": "htop",
        "name": "htop",
        "category": "System Info & Performance",
        "difficulty": "Beginner",
        "summary": "Interactive visual process viewer and task manager.",
        "description": "An enhanced, full-color, interactive replacement for top with horizontal and vertical scrolling, mouse support, and tree views.",
        "syntax": "htop [OPTIONS]",
        "flags": {
            "-u [USER]": "Show only processes of a given user.",
            "-p [PIDS]": "Show only the given PIDs.",
            "-d [DELAY]": "Delay between updates, in tenths of seconds.",
        },
        "examples": [
            {"cmd": "htop", "desc": "Launch color interactive process viewer"},
            {"cmd": "htop -u ray", "desc": "Show processes owned by user ray"},
        ],
        "hint": "Press F5 in htop to switch between list and tree process hierarchy view.",
        "challenge": {
            "scenario": "Open htop filtered to show only processes owned by user 'nginx'.",
            "canonical": "htop -u nginx",
            "alternatives": ["htop -u nginx"],
            "keywords": ["htop", "-u", "nginx"],
        },
    },
    {
        "id": "df",
        "name": "df",
        "category": "System Info & Performance",
        "difficulty": "Beginner",
        "summary": "Report filesystem disk space usage.",
        "description": "Displays the amount of available and used disk space on mounted filesystems.",
        "syntax": "df [OPTIONS] [FILE...]",
        "flags": {
            "-h": "Print sizes in human readable powers of 1024 (e.g., 10G, 450M).",
            "-T": "Print filesystem type (ext4, btrfs, tmpfs, etc.).",
            "-i": "List inode information instead of block usage.",
        },
        "examples": [
            {"cmd": "df -h", "desc": "Display mounted disk usage in human-readable gigabytes/megabytes"},
            {"cmd": "df -hT", "desc": "Display human-readable usage along with filesystem type"},
            {"cmd": "df -i", "desc": "Check inode usage (useful when disk is full due to too many files)"},
        ],
        "hint": "Mnemonic: 'Disk Free'. Always run with '-h'.",
        "challenge": {
            "scenario": "Check disk space usage for all mounted filesystems in human-readable format.",
            "canonical": "df -h",
            "alternatives": ["df -h"],
            "keywords": ["df", "-h"],
        },
    },
    {
        "id": "du",
        "name": "du",
        "category": "System Info & Performance",
        "difficulty": "Intermediate",
        "summary": "Estimate file and directory space usage.",
        "description": "Summarizes disk usage of each file and directory recursively.",
        "syntax": "du [OPTIONS] [FILE/DIR...]",
        "flags": {
            "-s": "Display only a total sum for each argument (summary).",
            "-h": "Print sizes in human readable format (e.g., 1K 234M 2G).",
            "-d N, --max-depth=N": "Print total for a directory only if it is N or fewer levels below.",
        },
        "examples": [
            {"cmd": "du -sh /var/log", "desc": "Show total disk space occupied by /var/log folder"},
            {"cmd": "du -h --max-depth=1 /home", "desc": "Show size of each top-level folder in /home"},
            {"cmd": "du -ah . | sort -rh | head -n 10", "desc": "Find top 10 largest files/folders in current directory"},
        ],
        "hint": "Mnemonic: 'Disk Usage'. 'du -sh *' shows size of all items in current folder.",
        "challenge": {
            "scenario": "Print the total summary disk usage of directory '/var/log' in human-readable format.",
            "canonical": "du -sh /var/log",
            "alternatives": ["du -sh /var/log/", "du -hs /var/log", "du -hs /var/log/"],
            "keywords": ["du", "-s", "-h", "/var/log"],
        },
    },
    {
        "id": "free",
        "name": "free",
        "category": "System Info & Performance",
        "difficulty": "Beginner",
        "summary": "Display amount of free and used memory in the system.",
        "description": "Displays the total amount of free and used physical RAM and swap memory in the system, as well as the buffers and caches.",
        "syntax": "free [OPTIONS]",
        "flags": {
            "-h": "Display output in human-readable units (e.g., MB, GB).",
            "-m": "Display the amount of memory in megabytes.",
            "-g": "Display the amount of memory in gigabytes.",
            "-s N": "Continuously update display every N seconds.",
        },
        "examples": [
            {"cmd": "free -h", "desc": "Show RAM and swap usage in human-readable format"},
            {"cmd": "free -m", "desc": "Show RAM and swap usage in exact megabytes"},
        ],
        "hint": "Look at the 'available' column, not just 'free', as Linux uses idle memory for caches.",
        "challenge": {
            "scenario": "Show system RAM and swap usage in human-readable format (MB/GB).",
            "canonical": "free -h",
            "alternatives": ["free -h"],
            "keywords": ["free", "-h"],
        },
    },
    {
        "id": "ps",
        "name": "ps",
        "category": "System Info & Performance",
        "difficulty": "Intermediate",
        "summary": "Report a snapshot of the current processes.",
        "description": "Displays information about a selection of the active processes running on the system.",
        "syntax": "ps [OPTIONS]",
        "flags": {
            "aux": "BSD style: a (all users), u (user-oriented format), x (processes without controlling tty).",
            "-ef": "Standard UNIX style: -e (every process), -f (full format listing).",
            "-u USER": "Select processes by user name or ID.",
            "--sort": "Specify sort column, e.g. --sort=-%cpu or --sort=-%mem.",
        },
        "examples": [
            {"cmd": "ps aux", "desc": "List every running process on the system with user, CPU, and memory stats"},
            {"cmd": "ps -ef", "desc": "Full process tree snapshot showing PPID (parent process ID)"},
            {"cmd": "ps aux | grep nginx", "desc": "Find running nginx worker processes"},
        ],
        "hint": "'ps aux' (BSD style, no leading dash) or 'ps -ef' (POSIX style with dash).",
        "challenge": {
            "scenario": "Display all running processes on the system using BSD style flags with user-oriented format.",
            "canonical": "ps aux",
            "alternatives": ["ps aux"],
            "keywords": ["ps", "aux"],
        },
    },
    {
        "id": "lsof",
        "name": "lsof",
        "category": "System Info & Performance",
        "difficulty": "Intermediate",
        "summary": "List open files and active network connections.",
        "description": "LiSt Open Files. In Linux everything is a file, so lsof lists regular files, directories, libraries, and network sockets.",
        "syntax": "lsof [OPTIONS]",
        "flags": {
            "-i :PORT": "Find processes listening on or connected to a network port (e.g., -i :8080).",
            "-u USER": "List files opened by specified user.",
            "-p PID": "List files opened by specified process ID.",
            "+D DIR": "List open files under directory recursively.",
        },
        "examples": [
            {"cmd": "lsof -i :80", "desc": "Find process listening on port 80"},
            {"cmd": "lsof -u ray", "desc": "List all files opened by user ray"},
            {"cmd": "lsof /var/log/syslog", "desc": "Find which process is currently writing to syslog"},
        ],
        "hint": "Invaluable for troubleshooting 'Address already in use' errors.",
        "challenge": {
            "scenario": "Find which process is currently listening on or using port 8080.",
            "canonical": "lsof -i :8080",
            "alternatives": ["lsof -i:8080", "lsof -i tcp:8080"],
            "keywords": ["lsof", "-i", "8080"],
        },
    },
    {
        "id": "uptime",
        "name": "uptime",
        "category": "System Info & Performance",
        "difficulty": "Beginner",
        "summary": "Tell how long the system has been running and load averages.",
        "description": "Prints current time, uptime duration, number of active logged-in users, and system load averages over the last 1, 5, and 15 minutes.",
        "syntax": "uptime [OPTIONS]",
        "flags": {
            "-p": "Show uptime in pretty, human-readable format.",
            "-s": "Show date and time since system is up.",
        },
        "examples": [
            {"cmd": "uptime", "desc": "Show system uptime and 1, 5, 15 min load averages"},
            {"cmd": "uptime -p", "desc": "Pretty format, e.g. 'up 2 weeks, 3 days, 1 hour'"},
        ],
        "hint": "Load average numbers correspond to the average number of threads in the run queue.",
        "challenge": {
            "scenario": "Display how long the machine has been running in pretty format.",
            "canonical": "uptime -p",
            "alternatives": ["uptime -p"],
            "keywords": ["uptime", "-p"],
        },
    },

    # ==========================================
    # Category: Process Control
    # ==========================================
    {
        "id": "kill",
        "name": "kill",
        "category": "Process Control",
        "difficulty": "Beginner",
        "summary": "Send a signal to a process (default TERM / 15).",
        "description": "Sends a specified termination signal to a process specified by PID. Signal 15 (SIGTERM) allows graceful shutdown, while 9 (SIGKILL) forces immediate termination.",
        "syntax": "kill [OPTIONS] [SIGNAL] PID...",
        "flags": {
            "-9, -SIGKILL": "Force terminate process immediately without cleanup.",
            "-15, -SIGTERM": "Gracefully request process to terminate (default).",
            "-l": "List all available signal names.",
        },
        "examples": [
            {"cmd": "kill 1234", "desc": "Send graceful SIGTERM to PID 1234"},
            {"cmd": "kill -9 1234", "desc": "Force kill PID 1234 immediately"},
            {"cmd": "kill -l", "desc": "List all signal names and numbers"},
        ],
        "hint": "Try SIGTERM (15) first before reaching for SIGKILL (-9).",
        "challenge": {
            "scenario": "Forcefully terminate process with PID 4521 using SIGKILL.",
            "canonical": "kill -9 4521",
            "alternatives": ["kill -SIGKILL 4521", "kill -s 9 4521", "kill -s SIGKILL 4521"],
            "keywords": ["kill", "9", "4521"],
        },
    },
    {
        "id": "pkill",
        "name": "pkill",
        "category": "Process Control",
        "difficulty": "Intermediate",
        "summary": "Signal processes based on name and other attributes.",
        "description": "Looks up processes by matching their process command name and sends the specified signal to all matches.",
        "syntax": "pkill [OPTIONS] PATTERN",
        "flags": {
            "-f": "Match against the full command line string, not just process name.",
            "-9": "Send SIGKILL instead of SIGTERM.",
            "-u USER": "Match only processes owned by specified user.",
            "-e": "Display what process was killed (echo).",
        },
        "examples": [
            {"cmd": "pkill firefox", "desc": "Send SIGTERM to all processes named firefox"},
            {"cmd": "pkill -9 -f \"python3 worker.py\"", "desc": "Force kill process matching full script name"},
        ],
        "hint": "Use 'pgrep' first to see which PIDs will match before running 'pkill'!",
        "challenge": {
            "scenario": "Terminate all processes matching the full command line name 'celery' using the -f flag.",
            "canonical": "pkill -f celery",
            "alternatives": ["pkill -f celery"],
            "keywords": ["pkill", "-f", "celery"],
        },
    },
    {
        "id": "killall",
        "name": "killall",
        "category": "Process Control",
        "difficulty": "Intermediate",
        "summary": "Kill processes by exact name.",
        "description": "Sends a signal to all processes running any of the specified commands by exact binary name.",
        "syntax": "killall [OPTIONS] NAME...",
        "flags": {
            "-s SIGNAL": "Send specified signal (e.g. -s 9 or -s KILL).",
            "-i": "Interactively ask for confirmation before killing each process.",
            "-u USER": "Kill only processes owned by specified user.",
        },
        "examples": [
            {"cmd": "killall nginx", "desc": "Kill all running instances of nginx"},
            {"cmd": "killall -u bob", "desc": "Kill all processes belonging to user bob"},
        ],
        "hint": "Unlike pkill which uses regex matching, killall uses exact process names.",
        "challenge": {
            "scenario": "Kill all running instances of 'apache2' with interactive confirmation before killing each.",
            "canonical": "killall -i apache2",
            "alternatives": ["killall -i apache2"],
            "keywords": ["killall", "-i", "apache2"],
        },
    },
    {
        "id": "nohup",
        "name": "nohup",
        "category": "Process Control",
        "difficulty": "Intermediate",
        "summary": "Run a command immune to hangups, outputting to a non-tty.",
        "description": "Stands for 'No Hang Up'. Prevents the command from receiving SIGHUP signals when the terminal shell disconnects.",
        "syntax": "nohup COMMAND [ARG...] &",
        "flags": {
            "&": "Run the command in the background (shell operator).",
        },
        "examples": [
            {"cmd": "nohup ./backup.sh > backup.log 2>&1 &", "desc": "Run backup script in background safely detached from SSH session"},
            {"cmd": "nohup python3 server.py &", "desc": "Run server.py ignoring SIGHUP (outputs to nohup.out by default)"},
        ],
        "hint": "Essential when running long commands over remote SSH sessions.",
        "challenge": {
            "scenario": "Run './train_model.sh' in the background ignoring terminal hangup signals.",
            "canonical": "nohup ./train_model.sh &",
            "alternatives": ["nohup ./train_model.sh &"],
            "keywords": ["nohup", "train_model.sh", "&"],
        },
    },

    # ==========================================
    # Category: Permissions & Security
    # ==========================================
    {
        "id": "chmod",
        "name": "chmod",
        "category": "Permissions & Security",
        "difficulty": "Beginner",
        "summary": "Change file access permissions (modes).",
        "description": "Modifies read (r=4), write (w=2), and execute (x=1) permissions for user (u), group (g), and others (o).",
        "syntax": "chmod [OPTIONS] MODE FILE...",
        "flags": {
            "-R": "Change files and directories recursively.",
            "+x": "Add execute permission for all users.",
            "755": "rwxr-xr-x: Owner full access; group and others read and execute.",
            "644": "rw-r--r--: Owner read/write; group and others read-only.",
            "600": "rw-------: Owner read/write; no access for anyone else (ideal for SSH keys).",
        },
        "examples": [
            {"cmd": "chmod +x script.sh", "desc": "Make script.sh executable"},
            {"cmd": "chmod 600 ~/.ssh/id_rsa", "desc": "Set private SSH key permissions to owner-only"},
            {"cmd": "chmod -R 755 /var/www/html", "desc": "Recursively set directory to standard readable/executable mode"},
        ],
        "hint": "4 = Read, 2 = Write, 1 = Execute. Sum them up: 4+2+1=7 (rwx), 4+2=6 (rw-), 4+1=5 (r-x).",
        "challenge": {
            "scenario": "Make 'deploy.sh' executable for the owner, group, and others.",
            "canonical": "chmod +x deploy.sh",
            "alternatives": ["chmod +x deploy.sh", "chmod 755 deploy.sh"],
            "keywords": ["chmod", "+x", "deploy.sh"],
        },
    },
    {
        "id": "chown",
        "name": "chown",
        "category": "Permissions & Security",
        "difficulty": "Intermediate",
        "summary": "Change file owner and group.",
        "description": "Changes the user and/or group ownership of each given file. Requires superuser privileges to change user ownership.",
        "syntax": "chown [OPTIONS] [OWNER][:[GROUP]] FILE...",
        "flags": {
            "-R": "Operate on files and directories recursively.",
            "-v": "Verbose: output a diagnostic for every file processed.",
        },
        "examples": [
            {"cmd": "chown ray:ray file.txt", "desc": "Change both user and group owner to ray"},
            {"cmd": "chown -R www-data:www-data /var/www", "desc": "Recursively change ownership of web directory"},
            {"cmd": "chown root file.conf", "desc": "Change owner to root without changing group"},
        ],
        "hint": "Format is 'user:group'. Separate with a colon.",
        "challenge": {
            "scenario": "Recursively change ownership of '/var/www/html' to user 'www-data' and group 'www-data'.",
            "canonical": "chown -R www-data:www-data /var/www/html",
            "alternatives": ["chown -R www-data:www-data /var/www/html/"],
            "keywords": ["chown", "-R", "www-data:www-data", "/var/www/html"],
        },
    },
    {
        "id": "sudo",
        "name": "sudo",
        "category": "Permissions & Security",
        "difficulty": "Beginner",
        "summary": "Execute a command with superuser (root) security privileges.",
        "description": "Stands for 'Superuser DO'. Allows a permitted user to execute a command as the superuser or another user as specified in /etc/sudoers.",
        "syntax": "sudo [OPTIONS] COMMAND",
        "flags": {
            "-i": "Simulate initial login; get an interactive root login shell with root's environment.",
            "-u USER": "Run command as specified USER instead of root.",
            "-l": "List allowed and forbidden commands for the invoking user.",
        },
        "examples": [
            {"cmd": "sudo apt update", "desc": "Update system package lists with root permissions"},
            {"cmd": "sudo -i", "desc": "Switch to an interactive root shell"},
            {"cmd": "sudo -u postgres psql", "desc": "Run postgres command line as user postgres"},
        ],
        "hint": "Mnemonic: 'SuperUser DO'. Avoid doing everything as root; use sudo for individual tasks.",
        "challenge": {
            "scenario": "Open an interactive root login shell using sudo.",
            "canonical": "sudo -i",
            "alternatives": ["sudo -i"],
            "keywords": ["sudo", "-i"],
        },
    },
    {
        "id": "whoami",
        "name": "whoami",
        "category": "Permissions & Security",
        "difficulty": "Beginner",
        "summary": "Print the effective username of the current session.",
        "description": "Displays the username associated with the current effective user ID.",
        "syntax": "whoami",
        "flags": {},
        "examples": [
            {"cmd": "whoami", "desc": "Verify if you are currently running as regular user or root"},
        ],
        "hint": "Useful in scripts to verify if a script is being run as root.",
        "challenge": {
            "scenario": "Check the active username of your current terminal session.",
            "canonical": "whoami",
            "alternatives": ["whoami"],
            "keywords": ["whoami"],
        },
    },

    # ==========================================
    # Category: Networking & Web
    # ==========================================
    {
        "id": "curl",
        "name": "curl",
        "category": "Networking & Web",
        "difficulty": "Beginner",
        "summary": "Transfer data from or to a server using HTTP, HTTPS, FTP, etc.",
        "description": "Client URL tool. Widely used for testing APIs, downloading files, sending HTTP POST payloads, and inspecting response headers.",
        "syntax": "curl [OPTIONS] URL",
        "flags": {
            "-I, --head": "Fetch the HTTP response headers only.",
            "-O, --remote-name": "Write output to a local file named like the remote file.",
            "-o FILE": "Write output to custom FILE name.",
            "-L, --location": "Follow HTTP redirects (301, 302).",
            "-X METHOD": "Specify custom request method (GET, POST, PUT, DELETE).",
            "-H HEADER": "Pass custom HTTP header to server.",
            "-d DATA": "Sends the specified data in a POST request.",
            "-s, --silent": "Silent mode: don't show progress meter or error messages.",
        },
        "examples": [
            {"cmd": "curl -I https://example.com", "desc": "Inspect HTTP headers of website"},
            {"cmd": "curl -O https://example.com/archive.zip", "desc": "Download file keeping original filename"},
            {"cmd": "curl -s https://api.ipify.org", "desc": "Fetch public IP address silently"},
            {"cmd": "curl -X POST -d '{\"key\":\"val\"}' -H \"Content-Type: application/json\" https://api.dev/data", "desc": "Send JSON POST request"},
        ],
        "hint": "Add '-L' to follow redirects; without it, you may only receive 301 Moved Permanently.",
        "challenge": {
            "scenario": "Fetch only the HTTP headers from 'https://api.github.com' following any redirects.",
            "canonical": "curl -IL https://api.github.com",
            "alternatives": ["curl -I -L https://api.github.com", "curl -LI https://api.github.com"],
            "keywords": ["curl", "-I", "-L", "api.github.com"],
        },
    },
    {
        "id": "wget",
        "name": "wget",
        "category": "Networking & Web",
        "difficulty": "Beginner",
        "summary": "Non-interactive network file downloader.",
        "description": "Downloads files via HTTP, HTTPS, and FTP. Supports recursive downloads, resume interrupted downloads, and background operation.",
        "syntax": "wget [OPTIONS] URL...",
        "flags": {
            "-c": "Continue getting a partially-downloaded file (resume).",
            "-O FILE": "Write documents to FILE.",
            "-b": "Go to background immediately after startup.",
            "-q": "Quiet mode (turn off output).",
            "-r": "Turn on recursive retrieving (spider/mirror websites).",
        },
        "examples": [
            {"cmd": "wget https://example.com/file.iso", "desc": "Download file.iso into current directory"},
            {"cmd": "wget -c https://example.com/large.iso", "desc": "Resume broken or interrupted download"},
            {"cmd": "wget -O myapp.deb https://example.com/download?id=4", "desc": "Save download under specific filename"},
        ],
        "hint": "Use -c to avoid starting giant downloads from scratch if connection drops.",
        "challenge": {
            "scenario": "Resume an interrupted download of 'https://example.com/data.tar.gz'.",
            "canonical": "wget -c https://example.com/data.tar.gz",
            "alternatives": ["wget -c https://example.com/data.tar.gz"],
            "keywords": ["wget", "-c", "data.tar.gz"],
        },
    },
    {
        "id": "ping",
        "name": "ping",
        "category": "Networking & Web",
        "difficulty": "Beginner",
        "summary": "Send ICMP ECHO_REQUEST packets to network hosts.",
        "description": "Tests network reachability between host and destination, measuring round-trip time (RTT) and packet loss.",
        "syntax": "ping [OPTIONS] DESTINATION",
        "flags": {
            "-c COUNT": "Stop after sending COUNT packets (default on Linux is infinite until Ctrl+C).",
            "-i INTERVAL": "Wait INTERVAL seconds between sending each packet (default 1s).",
            "-W TIMEOUT": "Time to wait for a response, in seconds.",
        },
        "examples": [
            {"cmd": "ping -c 4 8.8.8.8", "desc": "Send 4 test pings to Google DNS and stop"},
            {"cmd": "ping -c 3 google.com", "desc": "Verify DNS resolution and connectivity to google.com"},
        ],
        "hint": "On Linux, ping runs forever unless you specify '-c <count>' or hit Ctrl+C.",
        "challenge": {
            "scenario": "Send exactly 5 ICMP ping packets to '1.1.1.1' and stop.",
            "canonical": "ping -c 5 1.1.1.1",
            "alternatives": ["ping -c 5 1.1.1.1"],
            "keywords": ["ping", "-c", "5", "1.1.1.1"],
        },
    },
    {
        "id": "ssh",
        "name": "ssh",
        "category": "Networking & Web",
        "difficulty": "Intermediate",
        "summary": "OpenSSH remote login client.",
        "description": "Secure Shell client for logging into remote machines and executing commands securely over an encrypted connection.",
        "syntax": "ssh [OPTIONS] [USER@]HOSTNAME [COMMAND]",
        "flags": {
            "-p PORT": "Port to connect to on the remote host (default 22).",
            "-i IDENTITY_FILE": "Selects a file from which the identity (private key) for public key auth is read.",
            "-L [LOCAL_PORT]:HOST:HOSTPORT": "Local port forwarding tunnel.",
            "-v": "Verbose mode (useful for debugging SSH connection failures).",
        },
        "examples": [
            {"cmd": "ssh ubuntu@192.168.1.50", "desc": "Connect to remote host as user ubuntu"},
            {"cmd": "ssh -p 2222 root@myserver.com", "desc": "Connect to non-standard port 2222"},
            {"cmd": "ssh -i ~/.ssh/aws_key.pem ec2-user@54.21.0.1", "desc": "Connect using private key pem file"},
            {"cmd": "ssh -L 8080:localhost:80 user@remote", "desc": "Tunnel remote port 80 to local port 8080"},
        ],
        "hint": "Always protect private keys with chmod 600 or SSH will reject them.",
        "challenge": {
            "scenario": "Connect to host '10.0.0.5' on port 2222 as user 'deploy' using private key '~/.ssh/deploy_key'.",
            "canonical": "ssh -p 2222 -i ~/.ssh/deploy_key deploy@10.0.0.5",
            "alternatives": [
                "ssh -i ~/.ssh/deploy_key -p 2222 deploy@10.0.0.5",
                "ssh deploy@10.0.0.5 -p 2222 -i ~/.ssh/deploy_key",
            ],
            "keywords": ["ssh", "-p 2222", "-i", "deploy_key", "deploy@10.0.0.5"],
        },
    },
    {
        "id": "scp",
        "name": "scp",
        "category": "Networking & Web",
        "difficulty": "Intermediate",
        "summary": "Secure copy files between hosts over SSH.",
        "description": "Copies files between hosts on a network using the secure SSH protocol for data transfer and authentication.",
        "syntax": "scp [OPTIONS] SOURCE DEST",
        "flags": {
            "-P PORT": "Specifies the port to connect to on the remote host (uppercase P!).",
            "-r": "Recursively copy entire directories.",
            "-i IDENTITY_FILE": "Selects the identity (private key) file.",
        },
        "examples": [
            {"cmd": "scp file.txt user@server:/home/user/", "desc": "Upload local file to remote server"},
            {"cmd": "scp user@server:/var/log/app.log ./", "desc": "Download remote file to current directory"},
            {"cmd": "scp -r ./dist user@server:/var/www/", "desc": "Recursively upload folder to remote server"},
        ],
        "hint": "Note: in scp the port flag is capital '-P', whereas in ssh it is lowercase '-p'.",
        "challenge": {
            "scenario": "Recursively copy the local directory 'build' to remote host 'server.com' into '/tmp' as user 'admin'.",
            "canonical": "scp -r build admin@server.com:/tmp",
            "alternatives": ["scp -r build/ admin@server.com:/tmp", "scp -r build admin@server.com:/tmp/"],
            "keywords": ["scp", "-r", "build", "admin@server.com:/tmp"],
        },
    },
    {
        "id": "rsync",
        "name": "rsync",
        "category": "Networking & Web",
        "difficulty": "Intermediate",
        "summary": "Fast, versatile remote (and local) file-copying and sync tool.",
        "description": "Synchronizes files and directories between two locations. Transmits only differences using delta transfer algorithm.",
        "syntax": "rsync [OPTIONS] SRC... DEST",
        "flags": {
            "-a": "Archive mode: equals -rlptgoD (preserves permissions, owners, symlinks, recursive).",
            "-v": "Increase verbosity.",
            "-z": "Compress file data during the transfer.",
            "-P": "Equivalent to --partial --progress (shows progress bar, resumes broken transfers).",
            "--delete": "Delete extraneous files from destination that are not in source.",
            "--dry-run": "Perform a trial run with no changes made.",
        },
        "examples": [
            {"cmd": "rsync -avzP src/ dest/", "desc": "Sync folder locally with archive, compression, and progress"},
            {"cmd": "rsync -avz --delete site/ user@web:/var/www/site/", "desc": "Mirror folder to remote server, removing deleted files"},
            {"cmd": "rsync -av --dry-run src/ dest/", "desc": "Preview changes before executing sync"},
        ],
        "hint": "Trailing slash matters: 'src/' copies the contents, while 'src' copies the folder itself.",
        "challenge": {
            "scenario": "Synchronize 'data/' to 'backup/' in archive mode with progress and compression.",
            "canonical": "rsync -avzP data/ backup/",
            "alternatives": [
                "rsync -avzP data backup",
                "rsync -avz -P data/ backup/",
                "rsync -avPz data/ backup/",
            ],
            "keywords": ["rsync", "-avzP", "data", "backup"],
        },
    },
    {
        "id": "ss",
        "name": "ss",
        "category": "Networking & Web",
        "difficulty": "Intermediate",
        "summary": "Another utility to investigate sockets (modern replacement for netstat).",
        "description": "Dumps socket statistics. Faster and more detailed than legacy netstat. Can display TCP, UDP, listening sockets, and process IDs.",
        "syntax": "ss [OPTIONS]",
        "flags": {
            "-t": "Display TCP sockets.",
            "-u": "Display UDP sockets.",
            "-l": "Display only listening sockets.",
            "-p": "Show process using socket (requires root for non-owned processes).",
            "-n": "Do not try to resolve service names (display numeric port numbers like :80 instead of :http).",
        },
        "examples": [
            {"cmd": "ss -tulpn", "desc": "Show all listening TCP and UDP ports with process names numerically"},
            {"cmd": "ss -t -a", "desc": "Show all active TCP connections"},
        ],
        "hint": "Mnemonic: 'tulpn' = TCP, UDP, Listening, Processes, Numeric. Best one-liner for port checks.",
        "challenge": {
            "scenario": "Display all listening TCP and UDP sockets with process info in numeric format.",
            "canonical": "ss -tulpn",
            "alternatives": ["ss -tulnp", "ss -tlupn", "ss -tu -l -p -n"],
            "keywords": ["ss", "-tulpn"],
        },
    },

    # ==========================================
    # Category: Archiving & Compression
    # ==========================================
    {
        "id": "tar",
        "name": "tar",
        "category": "Archiving & Compression",
        "difficulty": "Intermediate",
        "summary": "Archive multiple files into a single tape archive (.tar, .tar.gz).",
        "description": "Bundles multiple files into a single archive file, optionally compressing it via gzip (-z), bzip2 (-j), or xz (-J).",
        "syntax": "tar [OPTIONS] [ARCHIVE_NAME] [TARGET...]",
        "flags": {
            "-c": "Create a new archive.",
            "-x": "Extract files from an archive.",
            "-t": "List the contents of an archive without extracting.",
            "-z": "Filter the archive through gzip (.tar.gz / .tgz).",
            "-v": "Verbosely list files processed.",
            "-f": "Use archive file specified.",
            "-C DIR": "Change to directory DIR before performing operations.",
        },
        "examples": [
            {"cmd": "tar -czvf archive.tar.gz /path/to/dir", "desc": "Create compressed gzip archive"},
            {"cmd": "tar -xzvf archive.tar.gz", "desc": "Extract gzip archive into current folder"},
            {"cmd": "tar -tf archive.tar.gz", "desc": "Preview files inside archive without extracting"},
            {"cmd": "tar -xzvf archive.tar.gz -C /opt/app", "desc": "Extract archive directly into /opt/app"},
        ],
        "hint": "c = Create, x = eXtract, z = gZip, v = Verbose, f = File. 'tar -czvf' to pack, 'tar -xzvf' to unpack.",
        "challenge": {
            "scenario": "Extract a compressed archive named 'data.tar.gz' verbosely into the current directory.",
            "canonical": "tar -xzvf data.tar.gz",
            "alternatives": ["tar -xvzf data.tar.gz", "tar -xzf data.tar.gz", "tar xzvf data.tar.gz"],
            "keywords": ["tar", "-x", "data.tar.gz"],
        },
    },
    {
        "id": "gzip",
        "name": "gzip",
        "category": "Archiving & Compression",
        "difficulty": "Beginner",
        "summary": "Compress files using Lempel-Ziv coding (LZ77).",
        "description": "Reduces the size of the named files and renames each with a .gz suffix. By default replaces the original file.",
        "syntax": "gzip [OPTIONS] [FILE...]",
        "flags": {
            "-d": "Decompress (same as gunzip).",
            "-k": "Keep (don't delete) input files during compression or decompression.",
            "-9": "Maximum compression level (slower, smaller size).",
            "-v": "Display compression ratio percentage.",
        },
        "examples": [
            {"cmd": "gzip database.sql", "desc": "Compress into database.sql.gz (replaces original)"},
            {"cmd": "gzip -k access.log", "desc": "Compress into access.log.gz keeping the original access.log"},
            {"cmd": "gzip -d backup.sql.gz", "desc": "Decompress file back to backup.sql"},
        ],
        "hint": "Use -k (keep) if you do not want your original file deleted upon compression.",
        "challenge": {
            "scenario": "Compress 'backup.sql' keeping the original uncompressed file intact.",
            "canonical": "gzip -k backup.sql",
            "alternatives": ["gzip -k backup.sql", "gzip --keep backup.sql"],
            "keywords": ["gzip", "-k", "backup.sql"],
        },
    },
    {
        "id": "zip",
        "name": "zip",
        "category": "Archiving & Compression",
        "difficulty": "Beginner",
        "summary": "Package and compress files into .zip format (compatible with Windows/macOS).",
        "description": "A compression and file packaging utility compatible with PKZIP format.",
        "syntax": "zip [OPTIONS] ARCHIVE_NAME.zip [FILES/DIRS...]",
        "flags": {
            "-r": "Travel the directory structure recursively.",
            "-e": "Encrypt the contents with a password.",
            "-q": "Quiet mode.",
        },
        "examples": [
            {"cmd": "zip archive.zip file1.txt file2.txt", "desc": "Zip individual files into archive.zip"},
            {"cmd": "zip -r project.zip project_dir/", "desc": "Recursively zip a directory and all subfiles"},
            {"cmd": "unzip project.zip", "desc": "Extract zip file contents"},
        ],
        "hint": "Unlike tar, zip requires '-r' when compressing a folder.",
        "challenge": {
            "scenario": "Recursively compress directory 'photos' into a file named 'photos.zip'.",
            "canonical": "zip -r photos.zip photos",
            "alternatives": ["zip -r photos.zip photos/", "zip -r photos.zip ./photos"],
            "keywords": ["zip", "-r", "photos.zip", "photos"],
        },
    },

    # ==========================================
    # Category: Pipes, Redirection & Utilities
    # ==========================================
    {
        "id": "pipe",
        "name": "| (pipe)",
        "category": "Pipes, Redirection & Utilities",
        "difficulty": "Beginner",
        "summary": "Redirect the standard output of one command to standard input of another.",
        "description": "Connects commands together in a pipeline: CMD1 stdout -> CMD2 stdin.",
        "syntax": "CMD1 | CMD2",
        "flags": {},
        "examples": [
            {"cmd": "cat access.log | grep \"404\" | wc -l", "desc": "Count occurrences of 404 in log file"},
            {"cmd": "ps aux | grep node", "desc": "Find running node processes"},
        ],
        "hint": "The cornerstone of Unix philosophy: small programs combined with pipes.",
        "challenge": {
            "scenario": "Count how many files are in the current directory by piping 'ls' into 'wc -l'.",
            "canonical": "ls | wc -l",
            "alternatives": ["ls | wc -l"],
            "keywords": ["ls", "|", "wc -l"],
        },
    },
    {
        "id": "redirect",
        "name": "> and >> (redirect)",
        "category": "Pipes, Redirection & Utilities",
        "difficulty": "Beginner",
        "summary": "Redirect standard output to a file (> overwrites, >> appends).",
        "description": "Writes standard output stream directly to a file on disk. > truncates/overwrites, >> appends to end.",
        "syntax": "CMD > FILE (overwrite) or CMD >> FILE (append)",
        "flags": {
            "2>&1": "Redirect standard error (file descriptor 2) to standard output (file descriptor 1).",
            "&>": "Bash shortcut to redirect both stdout and stderr to a file.",
        },
        "examples": [
            {"cmd": "echo \"Hello\" > file.txt", "desc": "Write Hello to file.txt, overwriting any previous content"},
            {"cmd": "echo \"New log entry\" >> file.txt", "desc": "Append to file.txt without deleting existing content"},
            {"cmd": "./run.sh > output.log 2>&1", "desc": "Capture both normal output and errors into output.log"},
        ],
        "hint": "Double arrow (>>) appends; single arrow (>) completely overwrites existing file!",
        "challenge": {
            "scenario": "Append the string 'DONE' to the end of file 'status.log'.",
            "canonical": "echo 'DONE' >> status.log",
            "alternatives": ["echo \"DONE\" >> status.log", "echo DONE >> status.log"],
            "keywords": ["echo", "DONE", ">>", "status.log"],
        },
    },
    {
        "id": "tee",
        "name": "tee",
        "category": "Pipes, Redirection & Utilities",
        "difficulty": "Intermediate",
        "summary": "Read from standard input and write to standard output AND files simultaneously.",
        "description": "Splits the output stream into two like a T-pipe: displays on screen and saves to a file at the same time.",
        "syntax": "CMD | tee [OPTIONS] [FILE...]",
        "flags": {
            "-a, --append": "Append to the given files, do not overwrite.",
        },
        "examples": [
            {"cmd": "make | tee build.log", "desc": "Watch compilation live while saving complete output into build.log"},
            {"cmd": "echo \"127.0.0.1 custom.local\" | sudo tee -a /etc/hosts", "desc": "Safely append line to protected /etc/hosts using sudo"},
        ],
        "hint": "'sudo tee -a' is the standard way to write to root-owned files from a normal shell.",
        "challenge": {
            "scenario": "Append the line 'nameserver 8.8.8.8' to '/etc/resolv.conf' using sudo and tee.",
            "canonical": "echo 'nameserver 8.8.8.8' | sudo tee -a /etc/resolv.conf",
            "alternatives": [
                "echo \"nameserver 8.8.8.8\" | sudo tee -a /etc/resolv.conf",
                "echo nameserver 8.8.8.8 | sudo tee -a /etc/resolv.conf",
            ],
            "keywords": ["echo", "nameserver 8.8.8.8", "sudo", "tee", "-a", "/etc/resolv.conf"],
        },
    },
    {
        "id": "xargs",
        "name": "xargs",
        "category": "Pipes, Redirection & Utilities",
        "difficulty": "Intermediate",
        "summary": "Build and execute command lines from standard input items.",
        "description": "Reads items from standard input (delimited by spaces or newlines) and passes them as arguments to a command.",
        "syntax": "INPUT_STREAM | xargs [OPTIONS] [COMMAND]",
        "flags": {
            "-I REPLACE_STR": "Replace occurrences of REPLACE_STR in the command with names read from stdin.",
            "-n MAX_ARGS": "Use at most MAX_ARGS arguments per command line.",
            "-P MAX_PROCS": "Run up to MAX_PROCS processes at a time in parallel.",
            "-0, --null": "Input items are terminated by a null character (pairs with find -print0).",
        },
        "examples": [
            {"cmd": "find . -name \"*.bak\" | xargs rm", "desc": "Delete all found backup files"},
            {"cmd": "cat urls.txt | xargs -n 1 -P 4 curl -O", "desc": "Download 4 URLs at a time in parallel"},
            {"cmd": "find . -type f -name \"*.log\" -print0 | xargs -0 rm", "desc": "Safely delete files even with spaces in filenames"},
        ],
        "hint": "Pair 'find -print0' with 'xargs -0' to safely handle filenames containing spaces.",
        "challenge": {
            "scenario": "Safely delete all .tmp files found by 'find . -name \"*.tmp\" -print0' using xargs.",
            "canonical": "find . -name \"*.tmp\" -print0 | xargs -0 rm",
            "alternatives": [
                "find . -name '*.tmp' -print0 | xargs -0 rm",
                "find . -type f -name \"*.tmp\" -print0 | xargs -0 rm",
            ],
            "keywords": ["find", "*.tmp", "-print0", "xargs", "-0", "rm"],
        },
    },

    # ==========================================
    # Category: Services & Logs
    # ==========================================
    {
        "id": "systemctl",
        "name": "systemctl",
        "category": "Services & Logs",
        "difficulty": "Intermediate",
        "summary": "Control the systemd system and service manager.",
        "description": "Manages systemd services, daemons, targets, and system states (start, stop, restart, enable, disable, status).",
        "syntax": "systemctl [COMMAND] [UNIT]",
        "flags": {
            "status": "Show runtime status of a service unit.",
            "start": "Start one or more service units.",
            "stop": "Stop one or more service units.",
            "restart": "Restart one or more service units.",
            "enable": "Enable one or more units to start automatically at boot.",
            "disable": "Disable units from starting automatically at boot.",
            "daemon-reload": "Reload systemd manager configuration after editing unit files.",
        },
        "examples": [
            {"cmd": "sudo systemctl status nginx", "desc": "Check if nginx service is active, running, or failed"},
            {"cmd": "sudo systemctl restart docker", "desc": "Restart docker service"},
            {"cmd": "sudo systemctl enable --now postgresql", "desc": "Enable postgresql for boot AND start it immediately"},
            {"cmd": "sudo systemctl daemon-reload", "desc": "Reload systemd configuration after creating new .service file"},
        ],
        "hint": "'enable' configures automatic startup on reboot; 'start' runs it right now. Use '--now' for both.",
        "challenge": {
            "scenario": "Check the runtime status of the 'nginx' service.",
            "canonical": "systemctl status nginx",
            "alternatives": ["sudo systemctl status nginx"],
            "keywords": ["systemctl", "status", "nginx"],
        },
    },
    {
        "id": "journalctl",
        "name": "journalctl",
        "category": "Services & Logs",
        "difficulty": "Intermediate",
        "summary": "Query and view the systemd journal logs.",
        "description": "Retrieves and formats indexed log messages written by the kernel, system services, and stdout/stderr of daemon processes.",
        "syntax": "journalctl [OPTIONS]",
        "flags": {
            "-u UNIT": "Show logs for the specified service unit only.",
            "-f": "Follow: continuously print new log entries in real-time.",
            "-n [LINES]": "Show only the most recent LINES entries (default 10).",
            "-b": "Show messages from the current boot only.",
            "-p PRIORITY": "Filter by message priority (err, warning, info, etc.).",
        },
        "examples": [
            {"cmd": "journalctl -u nginx -f", "desc": "Stream real-time logs for nginx service"},
            {"cmd": "journalctl -b -p err", "desc": "Show error priority logs since current boot"},
            {"cmd": "journalctl -u myapp.service -n 50", "desc": "View last 50 log lines for myapp"},
        ],
        "hint": "Pairs with systemctl. If a service fails to start, 'journalctl -xeu <service>' explains why.",
        "challenge": {
            "scenario": "Continuously follow real-time logs for the service 'docker.service'.",
            "canonical": "journalctl -u docker.service -f",
            "alternatives": [
                "journalctl -f -u docker.service",
                "journalctl -fu docker",
                "journalctl -u docker -f",
                "sudo journalctl -u docker -f",
            ],
            "keywords": ["journalctl", "-u", "docker", "-f"],
        },
    },
    {
        "id": "crontab",
        "name": "crontab",
        "category": "Services & Logs",
        "difficulty": "Intermediate",
        "summary": "Maintain scheduled recurring cron table jobs for individual users.",
        "description": "Schedules automated jobs to run at fixed times, dates, or intervals using the 5-field cron syntax (min hour day-of-month month day-of-week).",
        "syntax": "crontab [OPTIONS]",
        "flags": {
            "-e": "Edit current user's crontab using default text editor ($EDITOR).",
            "-l": "Display current user's crontab entries.",
            "-r": "Remove the current crontab file completely.",
            "-u USER": "Specify user name whose crontab is to be viewed/edited (superuser only).",
        },
        "examples": [
            {"cmd": "crontab -l", "desc": "List all active scheduled cron jobs for current user"},
            {"cmd": "crontab -e", "desc": "Open editor to add or modify recurring cron jobs"},
            {"cmd": "0 2 * * * /backup.sh", "desc": "Cron syntax: run backup.sh every day at 02:00 AM"},
        ],
        "hint": "Remember: min (0-59), hour (0-23), day (1-31), month (1-12), day of week (0-7).",
        "challenge": {
            "scenario": "View (list) the active scheduled cron jobs for your current user.",
            "canonical": "crontab -l",
            "alternatives": ["crontab -l"],
            "keywords": ["crontab", "-l"],
        },
    },

    # ==========================================
    # Category: Disk & Storage Management
    # ==========================================
    {
        "id": "lsblk",
        "name": "lsblk",
        "category": "Disk & Storage Management",
        "difficulty": "Beginner",
        "summary": "List information about all block storage devices (disks & partitions).",
        "description": "Lists block devices in a tree-like hierarchy showing device names, partition types, mount points, and sizes.",
        "syntax": "lsblk [OPTIONS]",
        "flags": {
            "-f": "Output info about filesystems (FSTYPE, LABEL, UUID, MOUNTPOINTS).",
            "-a": "List all devices including empty devices.",
            "-m": "Output info about device permissions and ownership.",
        },
        "examples": [
            {"cmd": "lsblk", "desc": "Show tree of disks, partitions (sda1, nvme0n1p1, etc.), and mount points"},
            {"cmd": "lsblk -f", "desc": "Show filesystem types (ext4, vfat, swap) and filesystem UUIDs"},
        ],
        "hint": "Mnemonic: 'LiSt BLocK devices'. Fast, clean way to identify USB drives or NVMe SSD partitions.",
        "challenge": {
            "scenario": "List block storage devices showing filesystem types and UUIDs.",
            "canonical": "lsblk -f",
            "alternatives": ["lsblk -f"],
            "keywords": ["lsblk", "-f"],
        },
    },
    {
        "id": "mount",
        "name": "mount",
        "category": "Disk & Storage Management",
        "difficulty": "Intermediate",
        "summary": "Mount a storage filesystem to a directory in the Linux hierarchy.",
        "description": "Attaches the filesystem found on a block device to the directory tree at the specified mountpoint.",
        "syntax": "mount [OPTIONS] DEVICE DIR",
        "flags": {
            "-t TYPE": "Specify the filesystem type (ext4, nfs, iso9660, vfat).",
            "-o OPTIONS": "Mount options (ro=read-only, rw=read-write, noexec, remount).",
            "-a": "Mount all filesystems mentioned in /etc/fstab.",
        },
        "examples": [
            {"cmd": "sudo mount /dev/sdb1 /mnt/usb", "desc": "Mount partition /dev/sdb1 to /mnt/usb directory"},
            {"cmd": "sudo mount -o remount,rw /", "desc": "Remount root filesystem in read-write mode in rescue environment"},
            {"cmd": "sudo mount -a", "desc": "Mount all devices configured in /etc/fstab"},
        ],
        "hint": "Always ensure destination directory exists before mounting to it.",
        "challenge": {
            "scenario": "Mount the partition '/dev/sdb1' to '/mnt/backup'.",
            "canonical": "sudo mount /dev/sdb1 /mnt/backup",
            "alternatives": [
                "mount /dev/sdb1 /mnt/backup",
                "sudo mount /dev/sdb1 /mnt/backup/",
                "mount /dev/sdb1 /mnt/backup/",
            ],
            "keywords": ["mount", "/dev/sdb1", "/mnt/backup"],
        },
    },
    {
        "id": "umount",
        "name": "umount",
        "category": "Disk & Storage Management",
        "difficulty": "Intermediate",
        "summary": "Unmount filesystems safely from the directory tree.",
        "description": "Detaches the file system(s) from the file hierarchy. Can specify either the device name or the mount directory.",
        "syntax": "umount [OPTIONS] {DIR|DEVICE}",
        "flags": {
            "-l, --lazy": "Lazy unmount: detach immediately, clean up references when no longer busy.",
            "-f, --force": "Force unmount (in case of an unreachable NFS system).",
        },
        "examples": [
            {"cmd": "sudo umount /mnt/usb", "desc": "Safely unmount filesystem by mount point"},
            {"cmd": "sudo umount /dev/sdb1", "desc": "Safely unmount by device path"},
            {"cmd": "sudo umount -l /mnt/nfs", "desc": "Lazy unmount busy filesystem"},
        ],
        "hint": "Notice spelling: 'umount' (no 'n' after 'u'!). If busy, check with 'lsof +D /mnt/path'.",
        "challenge": {
            "scenario": "Safely unmount the device mounted at '/mnt/usb'.",
            "canonical": "sudo umount /mnt/usb",
            "alternatives": ["umount /mnt/usb", "sudo umount /mnt/usb/", "umount /mnt/usb/"],
            "keywords": ["umount", "/mnt/usb"],
        },
    },
   {   'category': 'Networking & Web',
        'challenge': {   'alternatives': [   'ip -br addr',
                                             'ip -brief a',
                                             'ip -c -br a',
                                             'ip addr show'],
                         'canonical': 'ip -br a',
                         'keywords': ['ip', 'a'],
                         'scenario': 'Display a brief summary of all network '
                                     'interfaces and their IP addresses.'},
        'description': 'The modern replacement for ifconfig, route, and '
                       'netstat. Essential tool for inspecting IP addresses, '
                       'link status, and routing tables.',
        'difficulty': 'Intermediate',
        'examples': [   {   'cmd': 'ip addr show',
                            'desc': 'Display all IP addresses on all network '
                                    'interfaces'},
                        {   'cmd': 'ip -br a',
                            'desc': 'Brief overview of interface names, '
                                    'UP/DOWN status, and IP addresses'},
                        {   'cmd': 'ip route',
                            'desc': 'Display current default gateway and '
                                    'routing table'},
                        {   'cmd': 'sudo ip link set eth0 up',
                            'desc': 'Bring the network interface eth0 up'}],
        'flags': {   '-br': 'Brief mode: concise single-line interface '
                            'summaries.',
                     '-c': 'Use colorized output for enhanced readability.',
                     'addr (or a)': 'Manage and view IP addresses on network '
                                    'interfaces.',
                     'link (or l)': 'Manage and view network interfaces / link '
                                    'states.',
                     'route (or r)': 'View and manipulate the kernel routing '
                                     'table.'},
        'hint': 'Mnemonic: ip a replaces ifconfig, and ip r replaces route -n. '
                'Add -c -br for clean colored output.',
        'id': 'ip',
        'name': 'ip',
        'summary': 'Show and manipulate routing, network devices, interfaces '
                   'and tunnels.',
        'syntax': 'ip [OPTIONS] OBJECT {COMMAND | help}'},
    {   'category': 'Networking & Web',
        'challenge': {   'alternatives': ['dig +short github.com'],
                         'canonical': 'dig github.com +short',
                         'keywords': ['dig', 'github.com', '+short'],
                         'scenario': 'Perform a short DNS lookup for '
                                     'github.com returning only the IP '
                                     'address.'},
        'description': 'Flexible tool for interrogating DNS name servers. '
                       'Performs DNS lookups and displays answers returned '
                       'from queried name servers.',
        'difficulty': 'Intermediate',
        'examples': [   {   'cmd': 'dig example.com',
                            'desc': 'Perform full DNS lookup for domain'},
                        {   'cmd': 'dig example.com +short',
                            'desc': 'Output only the resolved IP address'},
                        {   'cmd': 'dig @8.8.8.8 example.com MX',
                            'desc': 'Query Google DNS for Mail Exchange (MX) '
                                    'records'},
                        {   'cmd': 'dig +trace example.com',
                            'desc': 'Trace complete DNS resolution from root '
                                    'servers down'}],
        'flags': {   '+short': 'Provide terse answer only, ideal for shell '
                               'scripts.',
                     '+trace': 'Trace the full delegation path from root DNS '
                               'servers down.',
                     '@SERVER': 'Query a specific nameserver (e.g., @8.8.8.8) '
                                'instead of default resolver.',
                     'ANY / MX / TXT': 'Query specific DNS record types.'},
        'hint': 'Always use +short when you just need the IP address without '
                'verbose headers and stats.',
        'id': 'dig',
        'name': 'dig',
        'summary': 'Domain Information Groper — DNS lookup utility.',
        'syntax': 'dig [@server] [OPTIONS] DOMAIN [RECORD_TYPE]'},
    {   'category': 'Files & Navigation',
        'challenge': {   'alternatives': ['which git'],
                         'canonical': 'which git',
                         'keywords': ['which', 'git'],
                         'scenario': 'Find the path to the git executable in '
                                     'your current PATH.'},
        'description': 'Searches the directories listed in the current user '
                       'PATH environment variable and prints the absolute path '
                       'of the executable found.',
        'difficulty': 'Beginner',
        'examples': [   {   'cmd': 'which python3',
                            'desc': 'Find the exact path of the python3 '
                                    'executable (e.g. /usr/bin/python3)'},
                        {   'cmd': 'which -a node',
                            'desc': 'Find all node executables installed in '
                                    'your PATH'}],
        'flags': {   '-a': 'Print all matching pathnames of each argument '
                           'across PATH.'},
        'hint': 'If which does not find a command, it is either not installed '
                'or not in your '
                '/home/ray/.gemini/antigravity/bin:/home/ray/.config/Antigravity/bin:/home/ray/.local/bin:/home/ray/.local/bin:/home/ray/.local/bin:/home/ray/.local/bin:/home/ray/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/snap/bin:/home/ray/.lmstudio/bin:/home/ray/.lmstudio/apps/bionic/bin:/home/ray/.lmstudio/bin:/home/ray/Android/Sdk/cmdline-tools/latest/bin:/home/ray/Android/Sdk/platform-tools:/home/ray/Android/Sdk/emulator:/home/ray/.lmstudio/apps/bionic/bin:/home/ray/.lmstudio/bin:/home/ray/.lmstudio/apps/bionic/bin.',
        'id': 'which',
        'name': 'which',
        'summary': 'Locate the executable file path associated with a given '
                   'command.',
        'syntax': 'which [OPTIONS] COMMAND...'},
    {   'category': 'Files & Navigation',
        'challenge': {   'alternatives': ['file --mime data.bin'],
                         'canonical': 'file -i data.bin',
                         'keywords': ['file', '-i', 'data.bin'],
                         'scenario': 'Check the true MIME type and charset '
                                     'encoding of data.bin.'},
        'description': 'Tests each argument in an attempt to classify it. '
                       'Reads magic numbers and headers to determine if a file '
                       'is ELF binary, JPEG, ASCII text, etc.',
        'difficulty': 'Beginner',
        'examples': [   {   'cmd': 'file image.unknown',
                            'desc': 'Inspect true file format regardless of '
                                    'extension'},
                        {   'cmd': 'file -i script.sh',
                            'desc': 'Show MIME type and charset encoding (e.g. '
                                    'text/x-shellscript; charset=utf-8)'}],
        'flags': {   '-b': 'Brief mode; do not prepend filenames to output '
                           'lines.',
                     '-i, --mime': 'Output mime type strings instead of human '
                                   'readable text.',
                     '-z': 'Try to look inside compressed files.'},
        'hint': 'Linux does not care about file extensions like .exe or .txt — '
                'file examines the actual byte signature.',
        'id': 'file',
        'name': 'file',
        'summary': 'Determine file type using magic numbers rather than file '
                   'extension.',
        'syntax': 'file [OPTIONS] FILE...'},
    {   'category': 'Pipes, Redirection & Utilities',
        'challenge': {   'alternatives': ['man 5 crontab'],
                         'canonical': 'man 5 crontab',
                         'keywords': ['man', '5', 'crontab'],
                         'scenario': 'Open section 5 of the manual to view the '
                                     'file format documentation for crontab.'},
        'description': 'Formats and displays reference manuals for Linux '
                       'commands, system calls, library functions, and '
                       'configuration files.',
        'difficulty': 'Beginner',
        'examples': [   {   'cmd': 'man tar',
                            'desc': 'Open the official manual page for tar'},
                        {   'cmd': 'man 5 crontab',
                            'desc': 'Open manual page explaining crontab file '
                                    'syntax (Section 5)'},
                        {   'cmd': 'man -k firewall',
                            'desc': 'Search all manual descriptions mentioning '
                                    'firewall'}],
        'flags': {   '-k KEYWORD': 'Equivalent to apropos: search manual page '
                                   'descriptions for keywords.',
                     '1': 'User commands (e.g., man 1 printf).',
                     '5': 'File formats and conventions (e.g., man 5 '
                          'crontab).'},
        'hint': 'Navigate with arrow keys or Space, search with /, press q to '
                'quit.',
        'id': 'man',
        'name': 'man',
        'summary': 'An interface to the system reference manual pages.',
        'syntax': 'man [SECTION] COMMAND'},
    {   'category': 'Pipes, Redirection & Utilities',
        'challenge': {   'alternatives': [   "history | grep 'ssh'",
                                             'history | grep "ssh"'],
                         'canonical': 'history | grep ssh',
                         'keywords': ['history', '|', 'grep', 'ssh'],
                         'scenario': 'Search your terminal history for past '
                                     'commands containing ssh.'},
        'description': 'Displays the history list of commands entered in '
                       'terminal sessions with line numbers. Allows '
                       're-executing past commands easily.',
        'difficulty': 'Beginner',
        'examples': [   {   'cmd': 'history 20',
                            'desc': 'View the last 20 executed commands'},
                        {   'cmd': 'history | grep docker',
                            'desc': 'Search past executed docker commands'},
                        {   'cmd': '!542',
                            'desc': 'Re-run command number 542 from history'},
                        {   'cmd': '!!',
                            'desc': 'Re-run the immediately preceding command '
                                    '(often used with sudo !!)'}],
        'flags': {   '-c': 'Clear the history list by deleting all entries.',
                     '-d OFFSET': 'Delete the history entry at position '
                                  'OFFSET.',
                     '-w': 'Write current shell history to the history file '
                           '(~/.bash_history).'},
        'hint': 'Tip: sudo !! re-runs your previous command with sudo '
                'privileges if you forgot!',
        'id': 'history',
        'name': 'history',
        'summary': 'Display or manipulate the shell command execution history '
                   'list.',
        'syntax': 'history [OPTIONS] [N]'},
    {   'category': 'Pipes, Redirection & Utilities',
        'challenge': {   'alternatives': ['alias ll="ls -la"'],
                         'canonical': "alias ll='ls -la'",
                         'keywords': ['alias', 'll=', 'ls -la'],
                         'scenario': 'Create an alias named ll that runs ls '
                                     '-la.'},
        'description': 'Instructs the shell to replace one string with another '
                       'when used as the first word of a command line.',
        'difficulty': 'Beginner',
        'examples': [   {   'cmd': 'alias',
                            'desc': 'List all currently active aliases'},
                        {   'cmd': "alias ll='ls -la'",
                            'desc': 'Create alias ll that expands to ls -la'},
                        {   'cmd': "alias update='sudo apt update && sudo apt "
                                   "upgrade -y'",
                            'desc': 'Create full system update shortcut'},
                        {'cmd': 'unalias ll', 'desc': 'Remove the alias ll'}],
        'flags': {'-p': 'Print all defined aliases in reusable format.'},
        'hint': 'To make aliases permanent across reboots, add them to your '
                '~/.bashrc or ~/.zshrc file.',
        'id': 'alias',
        'name': 'alias',
        'summary': 'Define or display shell command shortcuts and aliases.',
        'syntax': "alias [NAME[='VALUE'] ... ]"},
    {   'category': 'Pipes, Redirection & Utilities',
        'challenge': {   'alternatives': [   'export '
                                             'PATH=/home/ray/.gemini/antigravity/bin:/home/ray/.config/Antigravity/bin:/home/ray/.local/bin:/home/ray/.local/bin:/home/ray/.local/bin:/home/ray/.local/bin:/home/ray/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/snap/bin:/home/ray/.lmstudio/bin:/home/ray/.lmstudio/apps/bionic/bin:/home/ray/.lmstudio/bin:/home/ray/Android/Sdk/cmdline-tools/latest/bin:/home/ray/Android/Sdk/platform-tools:/home/ray/Android/Sdk/emulator:/home/ray/.lmstudio/apps/bionic/bin:/home/ray/.lmstudio/bin:/home/ray/.lmstudio/apps/bionic/bin:/opt/bin',
                                             'export '
                                             'PATH="/home/ray/.gemini/antigravity/bin:/home/ray/.config/Antigravity/bin:/home/ray/.local/bin:/home/ray/.local/bin:/home/ray/.local/bin:/home/ray/.local/bin:/home/ray/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/snap/bin:/home/ray/.lmstudio/bin:/home/ray/.lmstudio/apps/bionic/bin:/home/ray/.lmstudio/bin:/home/ray/Android/Sdk/cmdline-tools/latest/bin:/home/ray/Android/Sdk/platform-tools:/home/ray/Android/Sdk/emulator:/home/ray/.lmstudio/apps/bionic/bin:/home/ray/.lmstudio/bin:/home/ray/.lmstudio/apps/bionic/bin:/opt/bin"'],
                         'canonical': 'export '
                                      'PATH="/home/ray/.gemini/antigravity/bin:/home/ray/.config/Antigravity/bin:/home/ray/.local/bin:/home/ray/.local/bin:/home/ray/.local/bin:/home/ray/.local/bin:/home/ray/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/snap/bin:/home/ray/.lmstudio/bin:/home/ray/.lmstudio/apps/bionic/bin:/home/ray/.lmstudio/bin:/home/ray/Android/Sdk/cmdline-tools/latest/bin:/home/ray/Android/Sdk/platform-tools:/home/ray/Android/Sdk/emulator:/home/ray/.lmstudio/apps/bionic/bin:/home/ray/.lmstudio/bin:/home/ray/.lmstudio/apps/bionic/bin:/opt/bin"',
                         'keywords': ['export', 'PATH', '/opt/bin'],
                         'scenario': 'Append /opt/bin to the current PATH '
                                     'environment variable.'},
        'description': 'Marks shell variables to be exported to the '
                       'environment of subsequently executed child processes.',
        'difficulty': 'Intermediate',
        'examples': [   {   'cmd': 'export EDITOR=nano',
                            'desc': 'Set default editor environment variable '
                                    'to nano'},
                        {   'cmd': 'export '
                                   'PATH="/home/ray/.gemini/antigravity/bin:/home/ray/.config/Antigravity/bin:/home/ray/.local/bin:/home/ray/.local/bin:/home/ray/.local/bin:/home/ray/.local/bin:/home/ray/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/snap/bin:/home/ray/.lmstudio/bin:/home/ray/.lmstudio/apps/bionic/bin:/home/ray/.lmstudio/bin:/home/ray/Android/Sdk/cmdline-tools/latest/bin:/home/ray/Android/Sdk/platform-tools:/home/ray/Android/Sdk/emulator:/home/ray/.lmstudio/apps/bionic/bin:/home/ray/.lmstudio/bin:/home/ray/.lmstudio/apps/bionic/bin:/usr/local/go/bin"',
                            'desc': 'Prepend/append directory to system PATH'},
                        {   'cmd': 'export',
                            'desc': 'List all environment variables exported '
                                    'in current session'}],
        'flags': {   '-n': 'Remove export property from variable (keeps local '
                           'shell variable).',
                     '-p': 'Display list of all exported variables and values '
                           'in current shell.'},
        'hint': 'Without export, a variable exists only in the current shell '
                'and is invisible to subshells and scripts.',
        'id': 'export',
        'name': 'export',
        'summary': 'Set environment variables to be passed to child processes.',
        'syntax': 'export [-fn] [NAME[=VALUE] ...] or export -p'},
    {   'category': 'Viewing & Text Processing',
        'challenge': {   'alternatives': ['diff -u app_v1.py app_v2.py'],
                         'canonical': 'diff -u app_v1.py app_v2.py',
                         'keywords': ['diff', '-u', 'app_v1.py', 'app_v2.py'],
                         'scenario': 'Compare app_v1.py and app_v2.py using '
                                     'unified diff format.'},
        'description': 'Compares files line by line and outputs what lines '
                       'need to change to make the files identical. Basis of '
                       'patch and git diff.',
        'difficulty': 'Intermediate',
        'examples': [   {   'cmd': 'diff -u file_old.py file_new.py',
                            'desc': 'Generate unified diff between two files'},
                        {   'cmd': 'diff -y --suppress-common-lines file1.txt '
                                   'file2.txt',
                            'desc': 'Side-by-side comparison of differences '
                                    'only'},
                        {   'cmd': 'diff -rq dir1/ dir2/',
                            'desc': 'Quick summary of differing files between '
                                    'two directories'}],
        'flags': {   '-q': 'Report only whether files differ, not the details.',
                     '-r': 'Recursively compare any subdirectories found.',
                     '-u, -U NUM': 'Output NUM (default 3) lines of unified '
                                   'context (standard diff format).',
                     '-w': 'Ignore all white space differences.',
                     '-y': 'Output side by side in two columns.'},
        'hint': 'The -u (unified diff) format is the standard format used by '
                'git patches.',
        'id': 'diff',
        'name': 'diff',
        'summary': 'Compare files line by line and display differences.',
        'syntax': 'diff [OPTIONS] FILES...'},
    {   'category': 'Services & Logs',
        'challenge': {   'alternatives': [   'dmesg -T | grep -i "error"',
                                             'dmesg -T | grep error'],
                         'canonical': 'dmesg -T | grep -i error',
                         'keywords': ['dmesg', '-T', '|', 'grep', 'error'],
                         'scenario': 'Print kernel ring buffer logs with '
                                     'human-readable timestamps filtered for '
                                     'error.'},
        'description': 'Diagnostic tool for viewing bootup logs, hardware plug '
                       'events (USB, PCIe, drives), OOM (Out of Memory) kills, '
                       'and kernel errors.',
        'difficulty': 'Intermediate',
        'examples': [   {   'cmd': 'dmesg -T | grep -i error',
                            'desc': 'Search kernel messages for errors with '
                                    'human timestamps'},
                        {   'cmd': 'dmesg -T | tail -n 20',
                            'desc': 'View the most recent 20 kernel messages'},
                        {   'cmd': 'dmesg -T | grep -i oom',
                            'desc': 'Check if kernel Out-Of-Memory killer '
                                    'terminated any processes'}],
        'flags': {   '-T, --ctime': 'Print human-readable timestamps instead '
                                    'of seconds since boot.',
                     '-l LEVEL': 'Restrict output to specified level (emerg, '
                                 'alert, crit, err, warn, notice, info, '
                                 'debug).',
                     '-w, --follow': 'Wait for and follow new kernel '
                                     'messages.'},
        'hint': 'Whenever you plug in a new USB drive or experience a silent '
                'crash, dmesg -T shows what happened.',
        'id': 'dmesg',
        'name': 'dmesg',
        'summary': 'Print or control the kernel ring buffer messages.',
        'syntax': 'dmesg [OPTIONS]'},
    {   'category': 'Disk & Storage Management',
        'challenge': {   'alternatives': [   'dd if=arch.iso of=/dev/sdb bs=4M '
                                             'status=progress',
                                             'sudo dd if=arch.iso of=/dev/sdb '
                                             'status=progress bs=4M'],
                         'canonical': 'sudo dd if=arch.iso of=/dev/sdb bs=4M '
                                      'status=progress',
                         'keywords': [   'dd',
                                         'if=arch.iso',
                                         'of=/dev/sdb',
                                         'bs=4M',
                                         'status=progress'],
                         'scenario': 'Write ISO arch.iso to device /dev/sdb '
                                     'with 4MB block size and live progress.'},
        'description': 'Copies raw blocks from input (if=) to output (of=). '
                       'Used for disk cloning, writing bootable USB OS images, '
                       'and wiping drives.',
        'difficulty': 'Advanced',
        'examples': [   {   'cmd': 'sudo dd if=ubuntu.iso of=/dev/sdX bs=4M '
                                   'status=progress',
                            'desc': 'Burn bootable ISO image to USB drive'},
                        {   'cmd': 'dd if=/dev/urandom of=random.dat bs=1M '
                                   'count=10',
                            'desc': 'Generate a 10MB test file containing '
                                    'random bytes'},
                        {   'cmd': 'sudo dd if=/dev/sda of=/dev/sdb bs=64K '
                                   'status=progress',
                            'desc': 'Direct raw bit-for-bit drive clone'}],
        'flags': {   'bs=BYTES': 'Read and write up to BYTES at a time (e.g. '
                                 'bs=4M).',
                     'count=N': 'Copy only N input blocks.',
                     'if=FILE': 'Input file / device.',
                     'of=FILE': 'Output file / device.',
                     'status=progress': 'Display periodic transfer progress '
                                        'statistics.'},
        'hint': 'Nickname: Disk Destroyer! Double-check of= target device path '
                'carefully or you can wipe your OS.',
        'id': 'dd',
        'name': 'dd',
        'summary': 'Convert and copy a file (low-level block copy).',
        'syntax': 'dd if=SOURCE of=TARGET [OPTIONS]'},
    {   'category': 'Pipes, Redirection & Utilities',
        'challenge': {   'alternatives': [   'apt update && apt install -y git',
                                             'sudo apt-get update && sudo '
                                             'apt-get install -y git'],
                         'canonical': 'sudo apt update && sudo apt install -y '
                                      'git',
                         'keywords': ['apt', 'update', 'install', '-y', 'git'],
                         'scenario': 'Refresh package repositories and install '
                                     'package git answering yes '
                                     'automatically.'},
        'description': 'Handles installing, updating, removing, and querying '
                       'software packages with automatic dependency '
                       'resolution.',
        'difficulty': 'Beginner',
        'examples': [   {   'cmd': 'sudo apt update && sudo apt upgrade -y',
                            'desc': 'Refresh repositories and upgrade '
                                    'installed packages'},
                        {   'cmd': 'sudo apt install -y htop git curl',
                            'desc': 'Install multiple software packages '
                                    'non-interactively'},
                        {   'cmd': 'apt search nginx',
                            'desc': 'Search repository for packages related to '
                                    'nginx'},
                        {   'cmd': 'sudo apt autoremove',
                            'desc': 'Remove orphaned dependencies no longer '
                                    'needed'}],
        'flags': {   '-y': 'Automatically answer yes to all confirmation '
                           'prompts.',
                     'install': 'Install specified package and required '
                                'dependencies.',
                     'purge': 'Remove package AND all configuration files.',
                     'remove': 'Remove package but keep configuration files.',
                     'search': 'Search package names and descriptions for a '
                               'keyword.',
                     'update': 'Download updated package lists from '
                               'repositories.',
                     'upgrade': 'Upgrade all installed packages to newest '
                                'versions.'},
        'hint': 'apt update updates the list of available software; apt '
                'upgrade actually performs the upgrades.',
        'id': 'apt',
        'name': 'apt',
        'summary': 'High-level command line package manager for Debian and '
                   'Ubuntu.',
        'syntax': 'apt [COMMAND] [PACKAGE...]'}
]

# Quick lookup dict by ID
COMMAND_MAP = {c["id"]: c for c in COMMANDS}
