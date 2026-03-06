NEW PATH
- I think i want to scape my github commit history and use it to generate a summary of daily work / commits / contributions.
  - Not sure how far back in history I can go to recover some of my old commits.
- Use AI to generate the captain's log content, based on a set of instructions and formatting rules.
- Id like to hook it up to some cron job so that it updates daily (every night)
  - Ideally it would also automatically create a new entry in the captain's log.
- I would also like to add manual entries to the captain's log, such as some interesting findings or notes.
- I don't think i want to have it hosted anywhere for now, just markdown files pushed to github


UNKNOWNS
- What is the best way to scrape my github commit history?
- How to setup Cron job, (likely GCP)
  - GCP function?
  - env support if deploying to GCP
- Which AI model to use
  - Was thinking Claude Sonnet 4.6 (best at creative writing) which I want.
- Instructions for AI model.
- Structure of each file
- How to automatically commit new entry to github?
