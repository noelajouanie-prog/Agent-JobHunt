import anthropic
import os
import resend
import time
from datetime import datetime, timedelta

resend.api_key = os.environ["RESEND_API_KEY"]
CRITERES = os.environ["CRITERES_EMPLOI"]
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

date_limite = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")

def api_call(**kwargs):
    for attempt in range(5):
        try:
            return client.messages.create(**kwargs)
        except anthropic.RateLimitError:
            if attempt == 4:
                raise
            wait = 60 * (attempt + 1)
            print(f"Rate limit atteint, attente {wait}s...")
            time.sleep(wait)

ENTREPRISES = [
    "Harvey", "Dust", "Legora", "Mistral AI", "Writer",
    "Hugging Face", "Cohere", "Glean", "Weights & Biases", "Scale AI",
    "HubSpot", "Salesforce", "Zendesk", "Freshworks", "Pipedrive",
    "Cloudflare", "CrowdStrike", "Palo Alto Networks", "SentinelOne",
    "Wiz", "Okta", "Zscaler", "Netskope",
    "Cisco", "Microsoft", "Google", "SAP", "Akamai", "Fastly",
    "Snowflake", "Databricks", "MongoDB", "Elastic", "Confluent",
    "Workday", "Deel", "Personio", "Rippling",
    "Stripe", "Adyen", "Checkout.com", "Spendesk", "Pennylane",
    "Kyriba", "Ivalua", "Tipalti",
    "Braze", "Contentsquare", "Klaviyo", "Amplitude",
    "Datadog", "GitLab", "HashiCorp", "PagerDuty",
    "Dynatrace", "New Relic", "Grafana Labs",
    "Notion", "Atlassian", "Miro", "Monday.com",
    "Asana", "Smartsheet", "ClickUp",
    "Gong", "Outreach", "Salesloft", "Highspot", "Seismic", "Showpad",
    "Twilio", "Sinch", "Zoom", "RingCentral",
    "Ironclad", "Juro", "Clio",
    "Coupa", "Workiva", "Sage", "Celonis",
    "Gainsight", "Intercom", "Medallia", "Sprinklr",
    "MuleSoft", "Workato", "Boomi",
    "Mirakl", "Commercetools", "Shopify", "Contentful",
    "Qonto", "Pigment", "Alan", "360Learning",
    "Veeva Systems", "DocuSign", "ServiceNow", "ThoughtSpot",
]

entreprises_str = ", ".join(ENTREPRISES)

tools = [{"type": "web_search_20250305", "name": "web_search"}]

messages = [{
    "role": "user",
    "content": f"""Tu es un agent de recherche d'emploi expert.
Utilise la recherche web pour trouver des offres d'emploi selon les critères suivants.
Essaie de trouver au moins 10 offres, mais ne retourne que des offres qui respectent strictement tous les critères.

Règles de recherche obligatoires :
- Recherche UNIQUEMENT des offres publiées après le {date_limite}. Ajoute `after:{date_limite}` à toutes tes requêtes Google.
- N'utilise JAMAIS Welcome to the Jungle. Ajoute `-site:welcometothejungle.com` à toutes tes requêtes.
- Commence par des recherches générales sur LinkedIn, Indeed et Pôle Emploi.
- Effectue ensuite des recherches ciblées sur les pages carrière de ces entreprises : {entreprises_str}
  Pour chaque entreprise, recherche : "[nom entreprise] Account Executive OR Account Manager Paris CDI after:{date_limite}"

{CRITERES}"""
}]

response = api_call(
    model="claude-sonnet-4-6",
    max_tokens=8000,
    tools=tools,
    tool_choice={"type": "any"},
    messages=messages,
)

while response.stop_reason == "pause_turn":
    messages.append({"role": "assistant", "content": response.content})
    time.sleep(30)
    response = api_call(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        tools=tools,
        messages=messages,
    )

contenu = "\n".join(b.text for b in response.content if b.type == "text")

html = f"""
<h2>Offres d'emploi du jour</h2>
<pre style="font-family: Arial; font-size: 14px; line-height: 1.6">{contenu}</pre>
"""

resend.Emails.send({
    "from": "onboarding@resend.dev",
    "to": os.environ["EMAIL_DESTINATAIRE"],
    "subject": "Tes offres d'emploi du jour",
    "html": html,
})

print("Email envoyé avec succès !")
