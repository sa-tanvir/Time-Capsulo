```java
private static LevenshteinResults findDetailedResults(final CharSequence left,
                                                      final CharSequence right,
                                                      final int[][] matrix,
                                                      final boolean swapped) {
    int delCount = 0;
    int addCount = 0;
    int substituteCount = 0;
    int rowIndex = right.length();
    int columnIndex = left.length();
    int dataAtLeft;
    int dataAtTop;
    int dataAtDiagonal;
    int data;
    while (rowIndex >= 0 && columnIndex >= 0) {
        dataAtLeft = columnIndex == 0 ? -1 : matrix[rowIndex][columnIndex - 1];
        dataAtTop = rowIndex == 0 ? -1 : matrix[rowIndex - 1][columnIndex];
        dataAtDiagonal = rowIndex > 0 && columnIndex > 0 ? matrix[rowIndex - 1][columnIndex - 1] : -1;
        if (dataAtLeft == -1 && dataAtTop == -1 && dataAtDiagonal == -1) {
            break;
        }
        data = matrix[rowIndex][columnIndex];
        if (columnIndex > 0 && rowIndex > 0 && left.charAt(columnIndex - 1) == right.charAt(rowIndex - 1)) {
            columnIndex--;
            rowIndex--;
            continue;
        }
        if (data - 1 == dataAtLeft && data <= dataAtDiagonal && data <= dataAtTop
                || dataAtDiagonal == -1 && dataAtTop == -1) {
            columnIndex--;
            if (swapped) {
                addCount++;
            } else {
                delCount++;
            }
        } else if (data - 1 == dataAtTop && data <= dataAtDiagonal && data <= dataAtLeft
                || dataAtDiagonal == -1 && dataAtLeft == -1) {
            rowIndex--;
            if (swapped) {
                delCount++;
            } else {
                addCount++;
            }
        } else {
            substituteCount++;
            columnIndex--;
            rowIndex--;
        }
    }
    return new LevenshteinResults(addCount + delCount + substituteCount, addCount, delCount, substituteCount);
}
```
