def evaluate(expr, variables):
    return evaluateExpression(preprocess(expr), variables)

def evaluateExpression(expr, variables):
    result, charIndex = getValue(expr, variables, 0)
    while charIndex < len(expr):
        char = expr[charIndex]
        value, offset = getValue(expr, variables, charIndex + 1)
        if char == "+": result += value
        if char == "*": result *= value
        charIndex += offset + 1
    return result

def getValue(expr, variables, index):
    if expr[index] == "(":
        localExpression = getLocalExpression(expr, index)
        value = evaluateExpression(localExpression, variables)
        charCount = len(localExpression) + 2
    else:
        variableName = getVariableName(expr, index)
        value = variables[variableName]
        charCount = len(variableName)
    return value, charCount

def getVariableName(expr, firstCharIndex):
    charCount = len(expr)
    char = expr[firstCharIndex]
    lastCharIndex = firstCharIndex
    while char not in "+*)":
        lastCharIndex += 1
        if lastCharIndex < charCount:
            char = expr[lastCharIndex]
        else:
            break
    return expr[firstCharIndex:lastCharIndex]

def getLocalExpression(expr, openBracketIndex):
    localExpressionCount = 1
    closeBracketIndex = openBracketIndex + 1
    while localExpressionCount:
        char = expr[closeBracketIndex]
        if char == "(": localExpressionCount += 1
        if char == ")": localExpressionCount -= 1
        closeBracketIndex += 1
    return expr[openBracketIndex + 1:closeBracketIndex - 1]

def preprocess(expr):
    expr = expr.replace(" ", "")
    plusIndices = [i for i, char in enumerate(expr) if char == "+"]
    if len(plusIndices) == 0: return expr
    plusIndices.append(len(expr))
    newExpr = expr[:plusIndices[0]]
    for i in range(len(plusIndices) - 1):
        localExpression = expr[plusIndices[i] + 1:plusIndices[i + 1]]
        isLocal = expr[plusIndices[i] + 1] == "(" and expr[plusIndices[i + 1] -1] == ")"
        if "*" in localExpression and not isLocal:
            newExpr += f"+({localExpression})"
        else:
            newExpr += f"+{localExpression}"
    return newExpr
