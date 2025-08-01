def basicChecker(output: bytes, answer: bytes) -> tuple[bool, str]:
    outputStr = output.decode().rstrip('\n')
    answerStr = answer.decode().rstrip('\n')
    outputLines = outputStr.splitlines()
    answerLines = answerStr.splitlines()
    if len(outputLines) != len(answerLines):
        return (False, "Output and answer have different number of lines.")
    for i in range(len(outputLines)):
        if outputLines[i].rstrip() != answerLines[i].rstrip():
            return (False, f"Line {i + 1} does not match.")
    return (True, "Output matches the answer.")
