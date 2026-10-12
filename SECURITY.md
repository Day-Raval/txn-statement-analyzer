# Security policy

## Reporting a vulnerability

Email **dayesh.raval@gmail.com** with the subject `txn-statement-analyzer security`, or open a private security advisory at https://github.com/Day-Raval/txn-statement-analyzer/security/advisories/new.

Please include what you found, how to reproduce it, and which agent you used. You will get a reply within 7 days, and confirmed issues are fixed in a new release listed in CHANGELOG.md.

Never attach a real bank statement to a report. Reproduce the issue with a synthetic CSV like `examples/sample-statement.csv`.

## Scope

The plugin contains markdown instructions, a local install script and a Python script that uses only the standard library. The script reads the CSV you point it at and the bundled `references/categories.md`, prints JSON to the terminal, makes no network calls and writes no files. The skill has no MCP servers.
