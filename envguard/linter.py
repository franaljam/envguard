"""Lint .env files for style and naming convention issues."""
from dataclasses import dataclass, field
from typing import Dict, List
import re


@dataclass
class LintIssue:
    key: str
    message: str
    severity: str  # 'error' | 'warning'


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    def has_issues(self) -> bool:
        return bool(self.issues)

    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    def summary(self) -> str:
        e, w = len(self.errors()), len(self.warnings())
        return f"{e} error(s), {w} warning(s)"


_UPPER_SNAKE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_NO_LEADING_DIGIT = re.compile(r'^[0-9]')


def lint_env(env: Dict[str, str], *, allow_lowercase: bool = False) -> LintResult:
    result = LintResult()
    for key, value in env.items():
        if not key:
            result.issues.append(LintIssue(key="(empty)", message="Empty key found", severity="error"))
            continue

        if _NO_LEADING_DIGIT.match(key):
            result.issues.append(LintIssue(key=key, message="Key must not start with a digit", severity="error"))

        if not allow_lowercase and key != key.upper():
            result.issues.append(LintIssue(key=key, message="Key should be UPPER_SNAKE_CASE", severity="warning"))

        if ' ' in key:
            result.issues.append(LintIssue(key=key, message="Key contains spaces", severity="error"))

        if value.startswith(' ') or value.endswith(' '):
            result.issues.append(LintIssue(key=key, message="Value has leading or trailing whitespace", severity="warning"))

        if '\n' in value:
            result.issues.append(LintIssue(key=key, message="Value contains newline character", severity="warning"))

    return result
