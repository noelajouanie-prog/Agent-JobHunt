import anthropic
import os
import resend

resend.api_key = os.environ["RESEND_API_KEY"]
CRITERES = os.environ["CRITERES_EMPLOI"]
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

tools = [{"type": "web_search_20250305", "name": "web_search"}]

messages = [{
    "role": "user",
    "content": f"""Tu es un agent de recherche d'emploi expert.
Utilise la recherche web pour trouver des offres d'emploi selon les critères suivants.
Essaie de trouver au moins 10 offres, mais ne retourne que des offres qui respectent strictement tous les critères.

{CRITERES}"""
}]

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=6000,
    tools=tools,
    tool_choice={"type": "any"},
    messages=messages,
)

while response.stop_reason == "pause_turn":
    messages.append({"role": "assistant", "content": response.content})
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=6000,
        tools=tools,
        messages=messages,
    )

contenu = "\n".join(b.text for b in response.content if b.type == "text")

html = f"""
<h2>🔍 Offres d'emploi du jour</h2>
<pre style="font-family: Arial; font-size: 14px; line-height: 1.6">{contenu}</pre>
"""

resend.Emails.send({
    "from": "onboarding@resend.dev",
    "to": os.environ["EMAIL_DESTINATAIRE"],
    "subject": "🔍 Tes offres d'emploi du jour",
    "html": html
})

print("Email envoyé avec succès !")
