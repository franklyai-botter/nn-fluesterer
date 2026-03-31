"""Optionaler KI-Pass via Groq API: Füllwörter entfernen, Grammatik korrigieren."""


def cleanup(text: str, api_key: str, language: str = "de") -> str:
    if not text or not api_key:
        return text

    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        if language == "de":
            system_prompt = (
                "Du bereinigst diktierten Text. "
                "Entferne Füllwörter (äh, ähm, halt, also, sozusagen), "
                "korrigiere Grammatik und Zeichensetzung. "
                "Gib NUR den bereinigten Text zurück, keine Erklärungen."
            )
        else:
            system_prompt = (
                "Clean up this dictated text. "
                "Remove filler words (uh, um, like, you know), "
                "fix grammar and punctuation. "
                "Return ONLY the cleaned text, no explanations."
            )

        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.1,
            max_tokens=1024,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[AI Cleanup] Fehler: {e} — Originaltext wird verwendet.")
        return text
