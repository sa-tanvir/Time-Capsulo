Workload: seeded progressions over int, float (dyadic values, so exact), Fraction, Decimal, mixed
int/float/Fraction argument types, and datetime/timedelta; 1-, 2- and 3-argument forms, positive and
negative steps, ~3% zero steps (ValueError). Up to 40 / 300 / 2k items per call (S/M/L).
Check mode hashes (type name, exact value) of every produced item; time mode just materialises the lists.
