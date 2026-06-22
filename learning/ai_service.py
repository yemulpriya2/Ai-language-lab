import json
import os
import urllib.error
import urllib.request


def _local_fallback(language_name, learner_level, prompt):
    return {
        "reply": (
            f"Coach mode active for {language_name}. You are currently at {learner_level} level. "
            f"Try this fun drill: answer your own question in 3 short sentences, then say them aloud with expression. "
            f"Now improve this prompt with one new word: {prompt[:120]}"
        ),
        "provider": "local-ai",
        "used_external_ai": False,
    }


def generate_tutor_reply(language_name, learner_level, prompt):
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    api_url = os.environ.get("OPENAI_BASE_URL", "").strip()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()

    if not api_key:
        return _local_fallback(language_name, learner_level, prompt)

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a playful but practical language tutor. Keep answers short, supportive, and structured. "
                    "Always provide: one explanation, one mini exercise, and one funny memory tip."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Language: {language_name}\n"
                    f"Learner level: {learner_level}\n"
                    f"Question: {prompt}\n"
                    "Respond in plain text with clear sections."
                ),
            },
        ],
        "temperature": 0.8,
    }

    request = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)
            content = data["choices"][0]["message"]["content"].strip()
            return {
                "reply": content,
                "provider": model,
                "used_external_ai": True,
            }
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError):
        return _local_fallback(language_name, learner_level, prompt)
