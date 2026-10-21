# TD 1 comparison view

Derived from the long comparison CSV; one final result per cell.

| Model | C01 | C02 | C03 | C04 | C05 | C06 | C07 | C08 | C09 | C10 | C11 | C12 | C13 | C14 | C15 | C16 | C17 | C18 | C19 | C20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| openai/gpt-oss-120b | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | OK | WRONG | OK | WRONG | OK | WRONG | OK |
| openai/gpt-oss-20b | OK | WRONG | OK | OK | OK | OK | OK | WRONG | OK | OK | WRONG | OK | OK | OK | OK | OK | OK | OK | OK | OK |
| cohere/north-mini-code:free | OK | WRONG | OK | OK | OK | OK | OK | WRONG | WRONG | OK | WRONG | OK | OK | OK | WRONG | WRONG | WRONG | OK | WRONG | OK |
| qwen/qwen3.8-27b | OK | OK | OK | OK | OK | OK | OK | OK | WRONG | OK | OK | OK | OK | OK | WRONG | OK | WRONG | 429 | WRONG | OK |
| dots-studio/dots-3-note-preview:free | OK | WRONG | OK | OK | OK | OK | OK | SQL | WRONG | WRONG | WRONG | OK | OK | OK | WRONG | WRONG | WRONG | WRONG | WRONG | OK |
