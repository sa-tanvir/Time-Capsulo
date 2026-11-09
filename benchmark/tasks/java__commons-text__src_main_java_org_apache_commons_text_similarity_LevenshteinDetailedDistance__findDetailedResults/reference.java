private static LevenshteinResults findDetailedResults(final CharSequence left,
                                                      final CharSequence right,
                                                      final int[][] matrix,
                                                      final boolean swapped) {

    int delCount = 0;
    int addCount = 0;
    int subCount = 0;

    int rowIndex = right.length();
    int columnIndex = left.length();

    int dataAtLeft = 0;
    int dataAtTop = 0;
    int dataAtDiagonal = 0;
    int data = 0;
    boolean deleted = false;
    boolean added = false;

    while (rowIndex >= 0 && columnIndex >= 0) {

        if (columnIndex == 0) {
            dataAtLeft = -1;
        } else {
            dataAtLeft = matrix[rowIndex][columnIndex - 1];
        }
        if (rowIndex == 0) {
            dataAtTop = -1;
        } else {
            dataAtTop = matrix[rowIndex - 1][columnIndex];
        }
        if (rowIndex > 0 && columnIndex > 0) {
            dataAtDiagonal = matrix[rowIndex - 1][columnIndex - 1];
        } else {
            dataAtDiagonal = -1;
        }
        if (dataAtLeft == -1 && dataAtTop == -1 && dataAtDiagonal == -1) {
            break;
        }
        data = matrix[rowIndex][columnIndex];

        // case in which the character at left and right are the same,
        // in this case none of the counters will be incremented.
        if (columnIndex > 0 && rowIndex > 0 && left.charAt(columnIndex - 1) == right.charAt(rowIndex - 1)) {
            columnIndex--;
            rowIndex--;
            continue;
        }

        // handling insert and delete cases.
        deleted = false;
        added = false;
        if (data - 1 == dataAtLeft && (data <= dataAtDiagonal && data <= dataAtTop)
                || (dataAtDiagonal == -1 && dataAtTop == -1)) { // NOPMD
            columnIndex--;
            if (swapped) {
                addCount++;
                added = true;
            } else {
                delCount++;
                deleted = true;
            }
        } else if (data - 1 == dataAtTop && (data <= dataAtDiagonal && data <= dataAtLeft)
                || (dataAtDiagonal == -1 && dataAtLeft == -1)) { // NOPMD
            rowIndex--;
            if (swapped) {
                delCount++;
                deleted = true;
            } else {
                addCount++;
                added = true;
            }
        }

        // substituted case
        if (!added && !deleted) {
            subCount++;
            columnIndex--;
            rowIndex--;
        }
    }
    return new LevenshteinResults(addCount + delCount + subCount, addCount, delCount, subCount);
}
