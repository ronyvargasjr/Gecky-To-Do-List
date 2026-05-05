"""
services/ai_agent.py — AI Task Generator
==========================================
Exposes a single public function:

    generate_tasks(prompt: str) -> list[str]

Currently returns mock data.  To wire up a real LLM, replace the body of
generate_tasks() with an API call — see the TODO comment below.
"""

# ── Mock task library ─────────────────────────────────────────────────────────
# Keys are keywords that are matched (case-insensitive) against the prompt.

_MOCK_TASKS: dict[str, list[str]] = {
    "morning routine": [
        "Wake up at 7:00 AM",
        "Drink a glass of water",
        "15-minute meditation or stretching",
        "Eat a healthy breakfast",
        "Review today's goals",
    ],
    "workout": [
        "Warm up for 5 minutes",
        "Cardio: 20-minute run or bike",
        "Strength: 3 sets of push-ups",
        "Core: planks and crunches",
        "Cool down and stretch",
    ],
    "study": [
        "Review yesterday's notes",
        "Read the next chapter",
        "Take active, concise notes",
        "Complete practice problems",
        "Summarise key concepts",
    ],
    "project": [
        "Define project goals and scope",
        "Break project into milestones",
        "Set up folder structure",
        "Write initial documentation",
        "Schedule first review checkpoint",
    ],
    "shopping": [
        "Check pantry for what's missing",
        "Write the grocery list",
        "Look for discount coupons",
        "Go to the store",
        "Put groceries away when back",
    ],
    "email": [
        "Archive old emails",
        "Reply to pending messages",
        "Unsubscribe from unwanted lists",
        "Set up folders for important senders",
        "Draft any outstanding responses",
    ],
}

_DEFAULT_TASKS: list[str] = [
    "Define the goal clearly",
    "Research necessary resources",
    "Break it into smaller steps",
    "Set a realistic deadline",
    "Review and iterate on progress",
]


# ── Public API ────────────────────────────────────────────────────────────────

def generate_tasks(prompt: str) -> list[str]:
    """
    Return a list of task title strings based on *prompt*.

    Args:
        prompt: Natural-language description of what the user wants to do.

    Returns:
        A list of short task title strings.

    TODO — Replace the mock logic with a real LLM call, for example:

        from openai import OpenAI
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a productivity assistant. "
                 "Return a JSON array of 5 short task strings."},
                {"role": "user", "content": prompt},
            ],
        )
        import json
        return json.loads(response.choices[0].message.content)
    """
    prompt_lower = prompt.lower()

    # Simple keyword matching for the mock implementation
    for keyword, tasks in _MOCK_TASKS.items():
        if keyword in prompt_lower:
            return tasks

    # Fallback: prepend a context task then use the default list
    return [f"Start: {prompt}"] + _DEFAULT_TASKS
