import anthropic
import os
import resend
import time
from datetime import datetime, timedelta

resend.api_key = os.environ["RESEND_API_KEY"]
CRITERES = os.environ["CRITERES_EMPLOI"]
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

date_limite = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")

ENTREPRISES = [
    # AI Tools
    "Harvey", "Dust", "Legora", "Mistral AI", "Writer",
    "Hugging Face", "Cohere", "Glean", "Weights & Biases", "Scale AI",
    # CRM / Sales
    "HubSpot", "Salesforce", "Zendesk", "Freshworks", "Pipedrive",
    # Cybersécurité
    "Cloudflare", "CrowdStrike", "Palo Alto Networks", "SentinelOne",
    "Wiz", "Okta", "Zscaler", "Netskope",
    # Cloud / Infra
    "Cisco", "Microsoft", "Google", "SAP", "Akamai", "Fastly",
    # Database / Data
    "Snowflake", "Databricks", "MongoDB", "Elastic", "Confluent",
    # HR Tech
    "Workday", "Deel", "Personio", "Rippling",
    # Payment / Fintech
    "Stripe", "Adyen", "Checkout.com", "Spendesk", "Pennylane",
    "Kyriba", "Ivalua", "Tipalti",
    # Marketing Tech
    "Braze", "Contentsquare", "Klaviyo", "Amplitude",
    # DevOps / Monitoring
    "Datadog", "GitLab", "HashiCorp", "PagerDuty",
    "Dynatrace", "New Relic", "Grafana Labs",
    # Collaboration / Productivité
    "Notion", "Atlassian", "Miro", "Monday.com",
    "Asana", "Smartsheet", "ClickUp",
    # Sales Intelligence
    "Gong", "Outreach", "Salesloft", "Highspot", "Seismic", "Showpad",
    # Communication / CPaaS
    "Twilio", "Sinch", "Zoom", "RingCentral",
    # Legal Tech
    "Ironclad", "Juro", "Clio",
    # ERP / Finance
    "Coupa", "Workiva", "Sage", "Celonis",
    # Customer Success / Support
    "Gainsight", "Intercom", "Medallia", "Sprinklr",
    # Integration / iPaaS
    "MuleSoft", "Workato", "Boomi",
    # E-commerce / Retail Tech
    "Mirakl", "Commercetools", "Shopify", "Contentful",
    # French scale-ups B2B
    "Qonto", "Pigment", "Alan", "360Learning",
    # Autres
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

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=8000,
    tools=tools,
    tool_choice={"type": "any"},
    messages=messages,
)

while response.stop_reason == "pause_turn":
    messages.append({"role": "assistant", "content": response.content})
    time.sleep(30)
    response = client.messages.create(
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
