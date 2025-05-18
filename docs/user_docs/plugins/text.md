# Text Plugin

The Text Plugin provides powerful text processing operations, allowing you to search, transform, and analyze text data through natural language commands.

## Overview

Text processing is a fundamental aspect of data manipulation and analysis. The Text Plugin gives you tools to search for patterns, replace text, count occurrences, and perform various transformations on text data with intuitive commands.

## Verbs

| Verb | Aliases | Description |
|------|---------|-------------|
| `grep` | `search`, `find-text` | Search for patterns in text |
| `sed` | `replace` | Stream editor for filtering and transforming text |
| `awk` | `process` | Pattern scanning and processing language |
| `sort` | | Sort lines of text |
| `uniq` | `unique` | Report or omit repeated lines |
| `wc` | `count` | Count lines, words, and characters |
| `head` | `top` | Output the first part of files |
| `tail` | `bottom` | Output the last part of files |
| `cut` | | Remove sections from each line of files |
| `tr` | `translate` | Translate or delete characters |

## Usage Examples

### Searching Text

```
# Basic search
search for "error" in logfile.txt
grep 'error' logfile.txt

# Case-insensitive search
find ERROR in logs ignoring case
grep -i 'ERROR' logs

# Recursive search
search for "TODO" in all Python files recursively
grep -r 'TODO' *.py

# Context lines
show 2 lines before and after each match of "error" in log.txt
grep -C 2 'error' log.txt
```

### Replacing Text

```
# Basic replacement
replace "old" with "new" in file.txt
sed 's/old/new/g' file.txt

# In-place editing
replace all occurrences of "typo" with "correction" in document.md and save changes
sed -i 's/typo/correction/g' document.md

# Multiple replacements
replace "error" with "warning" and "critical" with "error" in log.txt
sed -e 's/error/warning/g' -e 's/critical/error/g' log.txt
```

### Text Processing with AWK

```
# Print specific columns
show the 2nd and 4th columns of data.csv
awk '{print $2, $4}' data.csv

# Filter rows
show lines in access.log where the 9th field is greater than 1000
awk '$9 > 1000' access.log

# Calculate sum
calculate the sum of values in the 3rd column of data.txt
awk '{sum += $3} END {print sum}' data.txt
```

### Sorting Text

```
# Basic sort
sort the lines in names.txt alphabetically
sort names.txt

# Numeric sort
sort numbers.txt numerically
sort -n numbers.txt

# Reverse sort
sort file.txt in reverse order
sort -r file.txt

# Sort by column
sort data.csv by the 2nd column numerically
sort -k2,2n data.csv
```

### Finding Unique Lines

```
# Show unique lines
show unique lines in list.txt
uniq list.txt

# Count occurrences
count occurrences of each line in data.txt
sort data.txt | uniq -c

# Find duplicates
find duplicate lines in file.txt
sort file.txt | uniq -d
```

### Counting Text Elements

```
# Count lines
count the number of lines in file.txt
wc -l file.txt

# Count words
how many words are in document.txt
wc -w document.txt

# Count characters
count characters in message.txt
wc -c message.txt

# Count all (lines, words, characters)
get full count statistics for file.txt
wc file.txt
```

### Viewing File Portions

```
# View beginning of file
show the first 10 lines of large_file.txt
head large_file.txt

# View custom number of lines
show the first 20 lines of log.txt
head -n 20 log.txt

# View end of file
show the last 10 lines of log.txt
tail log.txt

# Monitor file updates
monitor the end of log.txt for new entries
tail -f log.txt
```

### Extracting Columns

```
# Extract specific columns
extract the 2nd and 3rd columns from data.csv using comma as delimiter
cut -d',' -f2,3 data.csv

# Change delimiter
extract usernames from /etc/passwd
cut -d':' -f1 /etc/passwd
```

### Character Translation

```
# Convert case
convert file.txt to uppercase
cat file.txt | tr 'a-z' 'A-Z'

# Delete characters
remove all digits from file.txt
cat file.txt | tr -d '0-9'

# Replace whitespace
replace spaces with tabs in file.txt
cat file.txt | tr ' ' '\t'
```

## Advanced Usage

### Text Processing Pipelines

```
# Find, sort, and count
find all error messages in logs, sort them, and count occurrences
grep 'ERROR' *.log | sort | uniq -c | sort -nr

# Extract and process data
extract the 3rd column from data.csv, sort numerically and show top 5 values
cut -d',' -f3 data.csv | sort -n | tail -n 5

# Find lines matching pattern and extract specific field
find lines containing "user" in log.txt and extract the timestamp
grep "user" log.txt | awk '{print $1, $2}'
```

### Regular Expressions

```
# Match with regex
find all email addresses in contacts.txt
grep -E "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" contacts.txt

# Advanced replacement with regex
replace all phone numbers with the format "PHONE: XXX-XXX-XXXX"
sed -E 's/([0-9]{3})-([0-9]{3})-([0-9]{4})/PHONE: \1-\2-\3/g' contacts.txt
```

## Configuration

The Text Plugin can be configured in your PlainSpeak configuration file:

```toml
[plugins.text]
# Default options for grep
grep_ignore_case = true
grep_recursive = false

# Default options for output
show_line_numbers = true
color_output = true

# File options
default_encoding = "utf-8"
max_output_lines = 1000     # For safety with large files
```

## Best Practices

1. **Use specific patterns**: Be as specific as possible with search patterns to avoid unwanted matches.
2. **Back up files before inline editing**: Create backups before using in-place edits with `sed -i`.
3. **Test complex regex**: Test complex regular expressions on a small sample before applying to large files.
4. **Handle large files carefully**: Use `head`, `tail`, or `grep` with constraints when dealing with very large files.
5. **Escape special characters**: Remember to escape special characters in patterns (e.g., `\.` for a literal period).

## Troubleshooting

### Common Issues

1. **Pattern not matching**: Check if you need case-insensitive search or if special characters need escaping.
2. **Command affecting incorrect lines**: Verify your pattern to ensure it only matches the intended text.
3. **Performance issues**: Processing very large files may be slow; consider using tools like `head` or `tail` to work with subsets.
4. **Character encoding issues**: Specify the correct encoding if files contain special characters.

### Error Messages

| Error Message | Possible Solution |
|---------------|-------------------|
| "No such file or directory" | Check if the specified file exists and the path is correct |
| "Binary file matches" | Use `grep -a` to process binary files as text |
| "Invalid regular expression" | Fix syntax in your regular expression pattern |
| "Unexpected EOF" | Check for missing closing quotes or brackets |
| "Unterminated address regex" | Ensure delimiters are properly used in `sed` commands |
