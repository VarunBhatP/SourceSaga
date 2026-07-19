"""
Local, fully free text generators for issue explanations.
"""
from typing import List, Tuple


def _extract_section(context: str, heading: str, fallback: str = "") -> str:
    marker = f"**{heading}:**"
    if marker not in context:
        return fallback

    after = context.split(marker, 1)[1].strip()
    for next_heading in ("**Description:**", "**Recent Comments:**"):
        if next_heading in after:
            after = after.split(next_heading, 1)[0].strip()
            break
    return after.strip() or fallback


def _extract_title_description_comments(context: str) -> Tuple[str, str, List[str]]:
    title = _extract_section(context, "Issue Title", "Untitled Issue")

    description = ""
    comments: List[str] = []

    if "**Description:**" in context:
        description_part = context.split("**Description:**", 1)[1]
        if "**Recent Comments:**" in description_part:
            description, comments_part = description_part.split("**Recent Comments:**", 1)
            comments = [line.strip("- ").strip() for line in comments_part.splitlines() if line.strip()]
        else:
            description = description_part

    description = description.strip() or "No detailed description was provided in the issue body."
    comments = comments[:3]
    return title, description, comments


def generate_solution_plan(context: str, issue_url: str) -> str:
    """Create a deterministic step-by-step plan from issue context."""
    title, description, comments = _extract_title_description_comments(context)
    repo_guess = issue_url.replace("https://github.com/", "").split("/issues/")[0]
    key_comment = comments[0] if comments else "No recent discussion is available, so the implementation should stay conservative."

    return f"""1. Understand the issue scope in `{repo_guess}` by reviewing the files and modules related to "{title}".

2. Reproduce or inspect the current behavior locally so you can confirm what is missing or incorrect before changing code.

3. Identify the main implementation area from the description below and map it to the smallest set of files needed:
{description[:500]}

4. Add or adjust the core logic in a minimal way, preferring small focused changes over broad refactors.

5. Preserve the existing public behavior unless the issue explicitly requires a breaking change.

6. Review recent discussion for extra constraints or expectations:
{key_comment[:300]}

7. Add validation, guard clauses, or error handling where the issue suggests edge cases or invalid input.

8. Test the updated flow manually and, if the project already has tests nearby, add or update targeted tests for the changed behavior.

9. Document the final behavior in code comments or docs only where it helps future contributors understand the fix.

10. Prepare the final contribution by summarizing what changed, why it solves the issue, and how it was verified."""


def generate_coding_prompt(context: str, solution_plan: str, issue_url: str) -> str:
    """Create a copy-pasteable coding prompt using the local plan."""
    title, description, comments = _extract_title_description_comments(context)
    repo_guess = issue_url.replace("https://github.com/", "").split("/issues/")[0]
    recent_discussion = "\n".join(f"- {comment}" for comment in comments) if comments else "- No recent comments were available."

    return f"""You are helping implement a GitHub issue in the repository `{repo_guess}`.

Issue title:
{title}

Issue description:
{description[:900]}

Recent discussion:
{recent_discussion[:500]}

Please produce a practical implementation for this issue using the following plan:
{solution_plan[:1200]}

Requirements:
1. Explain which files should be changed and why.
2. Provide code that is clean, minimal, and consistent with the existing project style.
3. Mention assumptions where the issue description is incomplete.
4. Include testing or manual verification steps.
5. Return the final answer in a way a contributor can directly apply to the codebase."""


def generate_proposal(context: str, solution_plan: str, issue_url: str) -> str:
    """Create a simple structured GSOC-style proposal without any API."""
    title, description, comments = _extract_title_description_comments(context)
    repo_guess = issue_url.replace("https://github.com/", "").split("/issues/")[0]
    challenge = comments[0] if comments else description[:220]

    return f"""# Google Summer of Code Project Proposal

## Project Title
Improving {title} in {repo_guess}

## Abstract
This proposal focuses on addressing the issue "{title}" in the repository `{repo_guess}`. The goal is to deliver a clear implementation, validate the behavior, and leave the codebase easier to maintain.

## Problem Statement
{description[:900]}

## Proposed Solution
{solution_plan[:1500]}

## Implementation Plan
### Weeks 1-2
Review the existing implementation, reproduce the issue, and confirm the expected behavior.

### Weeks 3-5
Implement the core code changes in the relevant modules and refine the main logic.

### Weeks 6-8
Handle edge cases, improve reliability, and align the solution with repository conventions.

### Weeks 9-10
Add or update tests and verify the behavior through focused manual checks.

### Weeks 11-12
Polish documentation, prepare the final patch, and summarize results for maintainers.

## Deliverables
- Working implementation for the requested issue
- Clear explanation of the technical approach
- Updated tests or verification notes
- Final contributor-ready summary

## Benefits
This work improves contributor onboarding, clarifies the issue resolution path, and provides maintainers with a focused, reviewable implementation.

## Risks And Notes
The issue may require additional repository-specific decisions during implementation. Current discussion suggests this important context:
{challenge[:500]}

## About Me
Add your background, relevant technical skills, and previous open source experience here."""
