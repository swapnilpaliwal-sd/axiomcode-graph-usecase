# Notes API: requirements

| ID | Requirement |
|---|---|
| S1 | Only a logged-in user can change notes. |
| S2 | Every deletion of a note is written to the audit log. |
| S3 | Only the store (`src/store.ts`) talks to the database driver. |
| S4 | Every admin endpoint checks that the caller is an admin. |

Words used above, as they appear in this codebase:

- **endpoint / handler**: a function in `src/handlers/`.
- **change notes**: add or remove a note, i.e. call `SqlNoteStore.add` or `SqlNoteStore.remove`.
- **logged-in check**: `requireUser`. **admin check**: `requireAdmin`.
- **audit log**: `audit`.
- **database driver**: `exec` in `src/driver.ts`.
