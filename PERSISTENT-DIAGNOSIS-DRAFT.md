# Diagnose Studio draft persistence

Diagnose Studio now autosaves the in-progress form to browser `sessionStorage`.

## Behaviour
- Bug title, description, advisory severity and priority, language, source code,
  stack trace, terminal logs, and the PII-sanitization toggle are retained while
  navigating between application routes (Dashboard, Reports, Diagnose Studio, etc.).
- Returning to Diagnose Studio in the same browser tab restores the draft.
- The draft is cleared after a diagnosis completes successfully.
- The user can explicitly clear it using the **Clear draft** control.
- Draft data is tab-scoped browser storage; it is not uploaded until the user
  submits the form. Closing the tab ends the session and normally clears it.

## Verification
Manual browser acceptance test:
1. Open Diagnose Studio and enter values in several fields.
2. Navigate to Dashboard, then Reports, then back to Diagnose Studio.
3. Confirm all entered values and selections are restored.
4. Refresh the tab and confirm the draft is still present.
5. Click Clear draft and confirm the form returns to defaults.
6. Submit a valid report, complete diagnosis, return to Diagnose Studio, and
   confirm the prior draft has been cleared.

Note: this change persists the Diagnose Studio form draft. It does not alter
saved reports or diagnosis results in the backend.
