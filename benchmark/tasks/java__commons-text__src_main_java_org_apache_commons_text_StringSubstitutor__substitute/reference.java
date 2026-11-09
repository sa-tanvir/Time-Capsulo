private int substitute(final TextStringBuilder buf, final int offset, final int length,
        List<String> priorVariables) {
    final StringMatcher pfxMatcher = getVariablePrefixMatcher();
    final StringMatcher suffMatcher = getVariableSuffixMatcher();
    final char escape = getEscapeChar();
    final StringMatcher valueDelimMatcher = getValueDelimiterMatcher();
    final boolean substitutionInVariablesEnabled = isEnableSubstitutionInVariables();
    final boolean substitutionInValuesDisabled = isDisableSubstitutionInValues();
    final boolean undefinedVariableException = isEnableUndefinedVariableException();

    final boolean top = priorVariables == null;
    boolean altered = false;
    int lengthChange = 0;
    char[] chars = buf.buffer;
    int bufEnd = offset + length;
    int pos = offset;
    while (pos < bufEnd) {
        final int startMatchLen = pfxMatcher.isMatch(chars, pos, offset, bufEnd);
        if (startMatchLen == 0) {
            pos++;
        } else {
            // found variable start marker
            if (pos > offset && chars[pos - 1] == escape) {
                // escaped
                if (preserveEscapes) {
                    pos++;
                    continue;
                }
                buf.deleteCharAt(pos - 1);
                chars = buf.buffer; // in case buffer was altered
                lengthChange--;
                altered = true;
                bufEnd--;
            } else {
                // find suffix
                final int startPos = pos;
                pos += startMatchLen;
                int endMatchLen = 0;
                int nestedVarCount = 0;
                while (pos < bufEnd) {
                    if (substitutionInVariablesEnabled && pfxMatcher.isMatch(chars, pos, offset, bufEnd) != 0) {
                        // found a nested variable start
                        endMatchLen = pfxMatcher.isMatch(chars, pos, offset, bufEnd);
                        nestedVarCount++;
                        pos += endMatchLen;
                        continue;
                    }

                    endMatchLen = suffMatcher.isMatch(chars, pos, offset, bufEnd);
                    if (endMatchLen == 0) {
                        pos++;
                    } else {
                        // found variable end marker
                        if (nestedVarCount == 0) {
                            String varNameExpr = new String(chars, startPos + startMatchLen,
                                    pos - startPos - startMatchLen);
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
                                final char[] varNameExprChars = varNameExpr.toCharArray();
                                int valueDelimiterMatchLen = 0;
                                for (int i = 0; i < varNameExprChars.length; i++) {
                                    // if there's any nested variable when nested variable substitution disabled,
                                    // then stop resolving name and default value.
                                    if (!substitutionInVariablesEnabled && pfxMatcher.isMatch(varNameExprChars, i,
                                            i, varNameExprChars.length) != 0) {
                                        break;
                                    }
                                    if (valueDelimMatcher.isMatch(varNameExprChars, i, 0,
                                            varNameExprChars.length) != 0) {
                                        valueDelimiterMatchLen = valueDelimMatcher.isMatch(varNameExprChars, i, 0,
                                                varNameExprChars.length);
                                        varName = varNameExpr.substring(0, i);
                                        varDefaultValue = varNameExpr.substring(i + valueDelimiterMatchLen);
                                        break;
                                    }
                                }
                            }

                            // on the first call initialize priorVariables
                            if (priorVariables == null) {
                                priorVariables = new ArrayList<>();
                                priorVariables.add(new String(chars, offset, length));
                            }

                            // handle cyclic substitution
                            checkCyclicSubstitution(varName, priorVariables);
                            priorVariables.add(varName);

                            // resolve the variable
                            String varValue = resolveVariable(varName, buf, startPos, endPos);
                            if (varValue == null) {
                                varValue = varDefaultValue;
                            }
                            if (varValue != null) {
                                final int varLen = varValue.length();
                                buf.replace(startPos, endPos, varValue);
                                altered = true;
                                int change = 0;
                                if (!substitutionInValuesDisabled) { // recursive replace
                                    change = substitute(buf, startPos, varLen, priorVariables);
                                }
                                change = change + varLen - (endPos - startPos);
                                pos += change;
                                bufEnd += change;
                                lengthChange += change;
                                chars = buf.buffer; // in case buffer was altered
                            } else if (undefinedVariableException) {
                                throw new IllegalArgumentException(String.format(
                                        "Cannot resolve variable '%s' (enableSubstitutionInVariables=%s).", varName,
                                        enableSubstitutionInVariables));
                            }

                            // remove variable from the cyclic stack
                            priorVariables.remove(priorVariables.size() - 1);
                            break;
                        }
                        nestedVarCount--;
                        pos += endMatchLen;
                    }
                }
            }
        }
    }
    if (top) {
        return altered ? 1 : 0;
    }
    return lengthChange;
}
