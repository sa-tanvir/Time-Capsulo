Line: 'p' TAB text. S: 42 edge strings + 300 random; M: 5000 strings with up to 200 leading zeros; L: 5000 strings with up to 2000 leading zeros (values < 1e18 so no overflow).
Driver calls `handle_padspec_(it, end)` (private, via -fno-access-control) and hashes width, side and consumed length.
