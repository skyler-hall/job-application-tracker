# AI Usage Documentation

## Tools Used

- **Claude (Anthropic, Claude Opus 5.5 in the Claude app):** my main tool for this project. I used it as a
  pair programmer: planning the build order, generating code for each feature, explaining what the code
  does, and debugging setup problems.
- **Pylance (VS Code Python checker):** not generative AI, but its warnings shaped a few decisions below.

## How I Worked With AI

I built the project one feature at a time and made a commit after each step, instead of asking for the
whole app at once. For each step, Claude explained the plan and gave me the code. I added it to my files,
ran it, tested it in the browser, and committed once it worked. When something broke, I pasted the exact
error or a screenshot and we fixed it together.

## Key Prompts

1. *(Pasted the assignment page and project spec)* "Let's do this." Then: "I want to work with you, not
   push one commit." This changed the approach from generating everything at once to building step by step.
2. "I want to add what round I'm in for the company, and also any events too. I want to store that as well."
   This led to the `current_round` column and the `events` table.
3. "Where are the rounds I'm at with companies I'm interviewing for?" This led to the "Currently
   Interviewing" dashboard table and the applications section on each company page.
4. "For the CSS can we give it a black and purple theme?" Then: "Let's use dark pink, lime greens, and
   dark orange too." This created the final color theme.
5. "Just give me the changes so it looks like I edited the files rather than copying and pasting." I wanted
   to make each change myself and understand where it goes in the file.
6. "This codebase seems redundant." I asked about the repeated CRUD code (see Lessons Learned).
7. Debugging prompts where I pasted errors, like the GitHub `GH007` private email error,
   `mysql is not recognized`, and `Access denied for user 'root'@'localhost'`.

## What AI Generated

- The database schema (`schema.sql`) with foreign keys, `ON DELETE` rules, a `CHECK` constraint, and sample data
- The database helper functions in `database.py` (`query_all`, `query_one`, `execute`) and all CRUD queries
- Flask routes in `app.py` for all 5 tables and the Job Match page
- Form validation in `validators.py`
- The Job Match algorithm in `matching.py` and its unit tests
- The HTML templates and `style.css`
- A first draft of the README and this file

## What I Changed or Decided

- **Added features beyond the spec:** I asked for `current_round` on applications and a 5th table,
  `events`, for career fairs and networking. I also asked to see my interview rounds per company.
- **Design:** I picked the color theme (black, purple, dark pink, lime green, and dark orange).
- **Process:** I asked to work incrementally with one commit per feature, and to get edits as changes to my
  existing files instead of whole-file replacements, so I understood every addition.
- **Setup fixes I worked through:**
  - Switched my git email to my GitHub `noreply` address after GitHub rejected my push (GH007).
  - Added MySQL's `bin` folder to PATH when PowerShell didn't recognize `mysql`.
  - Used `-e "source schema.sql"` because PowerShell doesn't support `<` redirection.
  - Re-saved `requirements.txt` as UTF-8 after PowerShell wrote it as UTF-16.
  - Caught that my `.gitignore` only had `.env` in it and added the Python cache and venv folders.
  - Committed template files I had missed (they still showed as untracked after a commit).
- **Code review and debugging:**
  - Pylance showed 40+ type errors because the MySQL driver doesn't say what type a row is. I added
    type hints to `query_all`, `query_one`, and `execute` (`-> list[dict[str, Any]]`), plus an `assert`
    for the dashboard `COUNT(*)` query, which always returns one row. That brought it to 0 errors.
  - The Pylance errors also exposed a real bug: the application validation code never got added to
    `validators.py`, so adding or editing an application would have crashed. I added it and tested the form.

## Lessons Learned

- **Small steps beat one big generation.** Building and committing one feature at a time made errors easy
  to find, and it gave me a real commit history instead of one giant commit.
- **AI code still needs testing.** I tested each page in the browser before committing, including the
  error cases (empty fields, bad emails, salary min bigger than max).
- **AI can't see my machine.** Most of my problems were environment issues (PATH, PowerShell syntax, git
  settings, file encoding). Pasting the exact error message got me the fastest fix.
- **Notice patterns in the code.** I noticed the CRUD code repeats for every table. AI explained that
  a shared helper, Flask Blueprints, or an ORM like SQLAlchemy could reduce it. We kept it explicit for
  this project because the SQL is part of what this database course grades, and because it's easier to
  read and explain.
- **Security basics matter.** Parameterized queries (`%s`) prevent SQL injection, deletes should only happen
  through POST, and passwords belong in `.env`, never in GitHub.
- **Checker warnings can hide real bugs.** Most Pylance warnings were type-hint noise, but one of them
  pointed to code I had never pasted in. Reading the warnings instead of ignoring them caught a crash
  before my demo.
