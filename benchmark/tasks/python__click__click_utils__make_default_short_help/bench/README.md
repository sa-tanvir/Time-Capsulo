Workload: (help_text, max_length) pairs. S starts with hand-written edge cases (empty/whitespace help, the
click test docstrings, first word too long, abbreviations, max_length 0) followed by 3000 random cases;
random help texts have up to 2K words of 1-12 chars (letters and `~/-_.,:`) joined by mixed whitespace,
occasionally one word ending in `.`, and max_length in [0, 7K], with K = 10 (S), 100 (M), 1000 (L).
The driver calls `make_default_short_help(text, max_length)` per case and hashes the repr of each result.
