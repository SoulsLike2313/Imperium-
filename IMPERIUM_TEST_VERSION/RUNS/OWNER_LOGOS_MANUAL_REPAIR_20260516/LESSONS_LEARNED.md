# Lessons Learned

## Lesson 1: Candidate dirty is not always failure

Precommit candidate mode must distinguish:
- dirty inside IMPERIUM_TEST_VERSION = allowed candidate state;
- dirty outside IMPERIUM_TEST_VERSION = blocker.

## Lesson 2: Interpreter identity is part of truth

"Python installed" is not enough. Scripts must use the exact interpreter with required packages.

## Lesson 3: Screenshot count is not evidence quality

Captured count is fake if multiple dashboards overwrite the same file.

Required evidence:
- captured count;
- failed count;
- blocked count;
- unique screenshot paths;
- no duplicate output paths.

## Lesson 4: Truth systems must avoid self-reference loops

RUN_ALL cannot validate current master run by reading previous master receipt as a blocker.

## Lesson 5: Policy files must not contain raw examples that scanners block

Encoding policies should use safe notation, codepoints, or descriptions.

## Lesson 6: Owner comments are first-class memory

When Owner explains why a repair matters, that must be stored as memory-linked context, not lost in chat.

## Lesson 7: Chat history is not enough

Everything important must be transformed into:
- memory zone;
- addressable file;
- receipt;
- owner comment;
- future task candidate;
- plan input.
