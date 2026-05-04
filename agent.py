import anthropic
import os
import resend

resend.api_key = os.environ["RESEND_API_KEY"]

CRITERES = os.environ["CRITERES_EMPLOI"]

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

response = client.messages.create(
   model="claude-sonnet-4-5",
    max_tokens=4000,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{
        "role": "user",
        "content": f"""Tu es un agent de recherche d'emploi.
Cherche des offres publiées dans les dernières 24h sur LinkedIn, Welcome to the Jungle, Indeed et Pôle Emploi.
Critères : {CRITERES}
Retourne une liste de 5 à 10 offres avec pour chacune : titre, entreprise, lieu, salaire si mentionné, lien, et un résumé en 2 lignes."""
    }]
)

contenu = next(b.text for b in response.content if b.type == "text")

html = f"""
<h2>🔍 Offres d'emploi du jour</h2>
<pre style="font-family: Arial; font-size: 14px; line-height: 1.6">{contenu}</pre>
"""

resend.Emails.send({{
    "from": "agent@resend.dev",
    "to": os.environ["EMAIL_DESTINATAIRE"],
    "subject": "🔍 Tes offres d'emploi du jour",
    "html": html
}})

print("Email envoyé avec succès !")
