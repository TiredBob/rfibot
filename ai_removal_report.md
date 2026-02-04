I have completed the requested tasks:

1.  **Removed AI functionality**:
    *   Confirmed `google-genai` was a dependency via `uv.lock`.
    *   Deleted `uv.lock` and regenerated it using `uv pip install .` and `uv lock` to ensure `google-genai` is no longer a dependency, as it is not listed in `pyproject.toml`.
    *   Verified no explicit usage of `google.generativeai`, `google-genai`, or common AI patterns in Python files.
2.  **Updated `README.md`**:
    *   Removed all references to "Gemini" and "AI Integration".
    *   Refined the "Install Dependencies" section.
3.  **Reviewed `USAGE.md`**: Confirmed no AI references were present, so no changes were needed.

All these changes have been committed and successfully pushed to the remote `main` branch.