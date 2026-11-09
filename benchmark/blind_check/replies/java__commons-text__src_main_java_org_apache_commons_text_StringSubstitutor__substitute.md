```java
private int substitute(final TextStringBuilder buf, final int offset, final int length,
        List<String> priorVariables) {
    final StringMatcher prefixMatcher = getVariablePrefixMatcher();
    final StringMatcher suffixMatcher = getVariableSuffixMatcher();
    final char escapeCh = getEscapeChar();
    final StringMatcher valueDelimMatcher = getValueDelimiterMatcher();
    final boolean substitutionInVariablesEnabled = isEnableSubstitutionInVariables();
    final boolean substitutionInValuesDisabled = isDisableSubstitutionInValues();
    final boolean undefinedVariableException = isEnableUndefinedVariableException();
    final boolean preserveEsc = isPreserveEscapes();
    final boolean top = priorVariables == null;
    boolean altered = false;
    int lengthChange = 0;
    char[] chars = buf.buffer;
    int bufEnd = offset + length;
    int pos = offset;
    while (pos < bufEnd) {
        final int startMatchLen = prefixMatcher.isMatch(chars, pos, offset, bufEnd);
        if (startMatchLen == 0) {
            pos++;
            continue;
        }
        if (pos > offset && chars[pos - 1] == escapeCh) {
            if (preserveEsc) {
                pos++;
                continue;
            }
            buf.deleteCharAt(pos - 1);
            chars = buf.buffer;
            lengthChange--;
            altered = true;
            bufEnd--;
            continue;
        }
        final int startPos = pos;
        pos += startMatchLen;
        int nestedVarCount = 0;
        while (pos < bufEnd) {
            if (substitutionInVariablesEnabled) {
                final int nestedLen = prefixMatcher.isMatch(chars, pos, offset, bufEnd);
                if (nestedLen != 0) {
                    nestedVarCount++;
                    pos += nestedLen;
                    continue;
                }
            }
            final int endMatchLen = suffixMatcher.isMatch(chars, pos, offset, bufEnd);
            if (endMatchLen == 0) {
                pos++;
                continue;
            }
            if (nestedVarCount > 0) {
                nestedVarCount--;
                pos += endMatchLen;
                continue;
            }
            String varNameExpr = new String(chars, startPos + startMatchLen, pos - startPos - startMatchLen);
            if (substitutionInVariablesEnabled) {
                final TextStringBuilder bufName = new TextStringBuilder(varNameExpr);
                substitute(bufName, 0, bufName.length());
                varNameExpr = bufName.toString();
            }
            pos += endMatchLen;
            final int endPos = pos;
            String varName = varNameExpr;
            String varDefaultValue = null;
            if (valueDelimMatcher != null) {
                final char[] exprChars = varNameExpr.toCharArray();
                for (int i = 0; i < exprChars.length; i++) {
                    if (!substitutionInVariablesEnabled
                            && prefixMatcher.isMatch(exprChars, i, i, exprChars.length) != 0) {
                        break;
                    }
                    final int delimLen = valueDelimMatcher.isMatch(exprChars, i, 0, exprChars.length);
                    if (delimLen != 0) {
                        varName = varNameExpr.substring(0, i);
                        varDefaultValue = varNameExpr.substring(i + delimLen);
                        break;
                    }
                }
            }
            if (priorVariables == null) {
                priorVariables = new ArrayList<>();
                priorVariables.add(buf.substring(offset, bufEnd));
            }
            checkCyclicSubstitution(varName, priorVariables);
            priorVariables.add(varName);
            String varValue = resolveVariable(varName, buf, startPos, endPos);
            if (varValue == null) {
                varValue = varDefaultValue;
            }
            if (varValue != null) {
                final int varLen = varValue.length();
                buf.replace(startPos, endPos, varValue);
                altered = true;
                int change = 0;
                if (!substitutionInValuesDisabled) {
                    change = substitute(buf, startPos, varLen, priorVariables);
                }
                change = change + varLen - (endPos - startPos);
                pos += change;
                bufEnd += change;
                lengthChange += change;
                chars = buf.buffer;
            } else if (undefinedVariableException) {
                throw new IllegalArgumentException(String.format(
                    "Cannot resolve variable '%s' (enableSubstitutionInVariables=%s).",
                    varName, substitutionInVariablesEnabled));
            }
            priorVariables.remove(priorVariables.size() - 1);
            break;
        }
    }
    if (top) {
        return altered ? 1 : 0;
    }
    return lengthChange;
}
```
