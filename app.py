from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from groq import Groq
import os
import json
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "coverflex-secret-2024")

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CONVERSATIONS_DIR = "conversations"
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

KNOWLEDGE_BASE = """
COVERFLEX — OVERVIEW & HISTORY

What is Coverflex?
All-in-one platform for flexible benefits and compensation management. Allows companies to offer more benefits to employees while reducing operational and fiscal costs. Founded in 2019 (operational in 2021), headquartered in Braga, Portugal.

Key facts:
- 3,600+ company clients since launch in 2021
- 200,000+ active users, €80M+ processed
- 101 employees across Europe and Latin America
- Revenue CAGR: 312.98% — 4th fastest growing startup in Southern Europe (Sifted/FT 2024)
- B Corp certified since September 2023
- €20M total funding (€5M pre-seed Breega + €15M Series A SCOR Ventures 2023)
- Markets: Portugal (market leader), Spain (2022-23), Italy (2023 via EatsReady acquisition)

Mission: Make compensation easier, transparent and flexible.
Purpose: "Reinventing compensation, ensuring that work pays more."
Vision: Be the reference platform for Compensation-as-a-Service for European companies.

Founders:
- Miguel Santo Amaro — Co-Founder & CEO. Forbes 30 Under 30, Endeavor Entrepreneur.
  Quote: "The way we work is changing, but compensation has not evolved for decades. Coverflex is changing that."
- Nuno Pinto — Co-Founder & CBO
- Rui Carvalho — Co-Founder & COO
- Luís Rocha — Co-Founder & CMO
- Tiago Fernandes — Co-Founder & CTO

Senior leadership:
- João Franqueira — CPO
- Bruno Oliveira — VP of Engineering
- Carlos Silva — Chief Architect
- Eduardo Gaspar Rull — Head of Sales
- Chiara Bassi — Country Manager Italy

Awards:
- Great Place to Work Portugal 2023: 1st place (51-100 employees category)
- Great Place to Work Europe: 15th place (50-499 employees)
- Most Loved Workplace (Newsweek 2025): top 100 most loved companies worldwide — only remote company on the list

---

PRODUCT — COVERFLEX WALLET

Coverflex Wallet: all-in-one solution combining meal allowance, flexible benefits, insurance and discounts on a single VISA card and platform.

Plans:
- Meal: meal allowance only (100% digital, full VISA network)
- Childcare: childcare vouchers only
- Wallet: all-in-one (includes Meal, Childcare and all benefits)

Coverflex Card:
- VISA card with two separate wallets: meal balance + benefits balance
- Works across full VISA network (restaurants, supermarkets, food establishments)
- Coverflex Meal also works in: Glovo, UberEats, Too Good to Go, Just Eat
- Legal limit: up to 8 meal vouchers per transaction (legal requirement, not Coverflex limitation)
- Some actions (e.g. updating bank details) require web version at my.coverflex.com

Available benefits:
- Coverflex Childcare: vouchers for nurseries/kindergartens for children <7 years. Tax-exempt (IRS + Social Security). 140% IRC increase for company.
- Education Expenses
- Health & Wellness
- Gym & Fitness
- Senior Expenses
- Savings & Retirement
- Public Transport
- Professional Training
- Technology
- Donations

Categories by usage method:
- Reimbursement only: Technology, Professional Training, Parking, Public Transport
- Mixed (card or reimbursement): Education, Health, Wellness, Gym, Senior Expenses

Coverflex AI:
WhatsApp assistant for questions about benefits, taxes, insurance and reimbursements.

App Coverflex:
- Available for iOS (App Store) and Android (Google Play)
- Web version: my.coverflex.com
- Languages: Portuguese, English, Spanish, Italian
- Features: check balance, request reimbursements, activate/manage card, add insurance dependents
- Exclusive access for employees of client companies (invitation required)

Integrations: Personio, BambooHR (native). REST API for custom integrations.

---

CUSTOMERS & MARKET

Ideal Customer Profile (ICP):
- Companies 50-500 employees, tech-forward, focused on talent retention

Reference clients: Santander, Natixis, Bolt, Revolut, OysterHR, Rows, Smartex, Emma, Remote, PwC, Unbabel

Competitive positioning (vs Edenred and Sodexo):
- Edenred/Sodexo in Italy charge up to 20% commission per transaction and pay merchants in 60-90 days
- Coverflex: sustainable fees + 24h payment, lower TCO, better employee experience

Common objections:
1. "Edenred/Sodexo is cheaper" → Lower TCO + better experience + lower merchant fees
2. "Complex integration" → REST API + native connectors + assisted onboarding
3. "Regulation/compliance" → Bank of Portugal license; GDPR; Italy: INPS welfare aziendale

---

CULTURE & VALUES

Core values: Extreme Employee Obsession (Rule #1 AND #2), Transparency, Integrity, Accountability, Continuous learning

Work mode: 100% remote-first, flexible hours, in-person meetings 2x/year

Brand manifesto: "We adapt. We change and grow. We're not measured by our titles."

Glassdoor rating 4.7/5: "Unusual transparency and openness. High ambition mixed with rationality."

---

EMPLOYEE BENEFITS (INTERNAL)

- Stock Options via VSOP for ALL employees — pool +11%, managed on Ledgy
- Coverflex Card (employees use their own product)
- Health insurance with family coverage
- 25 working days paid vacation — request via rh@coverflex.com
- Extended parental leave: 2 additional paid weeks; children's birthdays are a day off
- 3 Caring Days/year for social impact projects
- MacBook provided
- Remote Work Budget: €1,000/year
- Personal Growth Budget: €1,000/year
- Onboarding Budget: €500 one-time

Salary references:
- Customer Success Manager: €33,000-40,000 base + bonus
- AI Engineer: €50,000-60,000 base + VSOP
- Backend Engineer: €50,000-80,000 base + VSOP
- Key Account Manager (Spain): €35,000-45,000 base + commissions

---

INTERNAL ONBOARDING

First steps:
1. Welcome email from notifications@coverflex.com
2. Create account at my.coverflex.com
3. Set up NIF/tax number, address, IBAN
4. Add health insurance dependents within 30 days
5. Receive and activate Coverflex card (up to 2 weeks)
6. Join Slack — introduce yourself in #general

Tools: my.coverflex.com, Slack, Google Calendar, Notion, GitHub, Linear, HubSpot, Intercom

CEO quote: "If you've worked at a startup before, you will adapt quickly; if not, buckle up!" — Miguel Santo Amaro

---

REIMBURSEMENT PROCESS

Steps:
1. Pay with personal card
2. Get invoice with name + tax number
3. Photo of invoice
4. Upload to Coverflex platform, correct category
5. Reimbursement within 2 business days after approval

Rejection reasons: illegible invoice, wrong tax number, insufficient balance, ineligible expense

---

HEALTH INSURANCE

Coverage: Hospitalization €50,000 (90% insurer), Outpatient €5,000, Childbirth €3,000, Medications €250, Serious illnesses €1,000,000
Waiting periods: Hospitalization/Outpatient/Medications 90 days, Childbirth 365 days, Serious illnesses 180 days
Dependents cost (Mar 2025-Feb 2026): €76.33/month, children <18: €62.08/month

---

CONTACTS & SUPPORT

- Portugal: help@coverflex.com
- Spain: ayuda@coverflex.com
- Italy: aiuto@coverflex.com
- HR: rh@coverflex.com
- IT Support: it-support@coverflex.com
- Slack: #general, #hr, #support, #tech, #product
"""

RELATED_QUESTIONS = {
    "card": ["How do I check my balance?", "Where can I use the Coverflex card?", "How do I block my card if lost?"],
    "meal": ["Can I use it in delivery apps?", "What's the limit per transaction?", "How does the meal balance work?"],
    "benefit": ["How do I activate my benefits?", "What benefit categories exist?", "How do I request a reimbursement?"],
    "vacation": ["How do I request vacation days?", "What are Caring Days?", "What is the parental leave policy?"],
    "insurance": ["How do I add dependents?", "What are the waiting periods?", "Where can I use health insurance?"],
    "remote": ["What is the Personal Growth Budget?", "What is the Onboarding Budget?", "How does remote work work?"],
    "stock": ["What is VSOP?", "How are stock options managed?", "What are the other internal benefits?"],
    "reimburs": ["How long does reimbursement take?", "What documents do I need?", "Which categories allow reimbursement?"],
    "onboard": ["What tools will I need?", "When do I receive the Coverflex card?", "How do I add insurance dependents?"],
    "default": ["How does the Coverflex card work?", "What benefits are available?", "How do I contact support?"]
}

def get_related(question):
    q = question.lower()
    for key in RELATED_QUESTIONS:
        if key in q:
            return RELATED_QUESTIONS[key]
    return RELATED_QUESTIONS["default"]

def get_conversations():
    convs = []
    for f in sorted(os.listdir(CONVERSATIONS_DIR), reverse=True):
        if f.endswith('.json'):
            try:
                with open(os.path.join(CONVERSATIONS_DIR, f)) as fp:
                    data = json.load(fp)
                    convs.append({
                        "id": f.replace('.json', ''),
                        "title": data.get("title", "Conversation"),
                        "date": data.get("date", ""),
                        "messages": data.get("messages", [])
                    })
            except:
                pass
    return convs[:20]

def save_conv(conv_id, messages, title="New Chat"):
    path = os.path.join(CONVERSATIONS_DIR, f"{conv_id}.json")
    data = {
        "id": conv_id,
        "title": title,
        "date": datetime.now().strftime("%d/%m · %H:%M"),
        "messages": messages
    }
    with open(path, 'w') as f:
        json.dump(data, f)

def load_conv(conv_id):
    path = os.path.join(CONVERSATIONS_DIR, f"{conv_id}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def build_messages(message, history, lang):
    if lang == 'pt':
        system = """És o assistente de conhecimento interno da Coverflex — fintech portuguesa líder em benefícios flexíveis, fundada em 2021, presente em Portugal, Espanha e Itália.
Respondes SEMPRE em Português de Portugal. Tom profissional, claro e direto.
Regras: usa a knowledge base; se não souberes indica rh@coverflex.com ou help@coverflex.com; sê concreto; varia as aberturas; usa formatação clara."""
    else:
        system = """You are the internal knowledge assistant for Coverflex — a leading Portuguese fintech in flexible benefits, founded in 2021, present in Portugal, Spain and Italy.
You ALWAYS respond in English. Professional, clear and direct tone.
Rules: use the knowledge base; if unsure direct to rh@coverflex.com or help@coverflex.com; be specific; vary your openings; use clear formatting."""

    messages = [{"role": "system", "content": system + "\n\nKnowledge Base:\n" + KNOWLEDGE_BASE}]
    for h in history[-8:]:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": message})
    return messages

@app.route('/')
def index():
    return render_template('index.html')

# ── REGULAR ENDPOINT (used by frontend) ──
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    history = data.get('history', [])
    conv_id = data.get('conv_id', str(uuid.uuid4()))
    lang = data.get('lang', 'en')

    messages = build_messages(message, history, lang)

    try:
        r = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1000,
            temperature=0.65
        )
        response = r.choices[0].message.content
        related = get_related(message)
        all_messages = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": response}
        ]
        title = message[:40] + "..." if len(message) > 40 else message
        save_conv(conv_id, all_messages, title)
        return jsonify({"response": response, "related": related, "conv_id": conv_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/conversations', methods=['GET'])
def conversations():
    return jsonify(get_conversations())

@app.route('/api/conversations/<conv_id>', methods=['GET'])
def get_conversation(conv_id):
    conv = load_conv(conv_id)
    if conv:
        return jsonify(conv)
    return jsonify({"error": "Not found"}), 404

@app.route('/api/conversations/<conv_id>', methods=['DELETE'])
def delete_conversation(conv_id):
    path = os.path.join(CONVERSATIONS_DIR, f"{conv_id}.json")
    if os.path.exists(path):
        os.remove(path)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
