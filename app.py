from flask import Flask, render_template, request, jsonify, session
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
WhatsApp assistant for questions about benefits, taxes, insurance and reimbursements. Allows reimbursement requests with photo of invoice. Team handles thousands of conversations/week with 100% accuracy target.

App Coverflex:
- Available for iOS (App Store) and Android (Google Play)
- Web version: my.coverflex.com
- Languages: Portuguese, English, Spanish, Italian
- Features: check balance, request reimbursements, activate/manage card, add insurance dependents, view benefit categories, contact support
- Exclusive access for employees of client companies (invitation required)

Integrations: Personio, BambooHR (native). REST API for custom integrations.

---

CUSTOMERS & MARKET

Ideal Customer Profile (ICP):
- Companies 50-500 employees
- Tech-forward, focused on talent retention
- Dedicated Head of People

Reference clients: Santander, Natixis, Bolt, Revolut, OysterHR, Rows, Smartex, Emma, Remote, PwC, Unbabel

Real testimonials:
- Humberto Ayres Pereira (CEO Rows): "Coverflex enables Rows to offer a modern and efficient compensation package without complexity. We save time with Coverflex digital processes for HR and Finance."
- Rita Franca (Head of People, Unbabel): "It's a very easy solution to implement, understand and manage. We know we're giving our people the best we can."

Competitive positioning (vs Edenred and Sodexo):
- Edenred/Sodexo in Italy charge up to 20% commission per transaction and pay merchants in 60-90 days
- Coverflex: sustainable fees + 24h payment
- Lower total cost of ownership
- Better employee experience (modern app, autonomy, flexibility)
- Competitors solve only one pain point; Coverflex is a 360° solution

Common objections and responses:
1. "Edenred/Sodexo is cheaper" → Lower TCO + better employee experience + lower merchant fees
2. "Complex integration" → REST API + native Personio/BambooHR connectors + assisted onboarding
3. "Regulation/compliance" → Bank of Portugal license; GDPR compliance; Italy: INPS welfare aziendale compliance
4. "Data security" → Sandbox demo available + certifications (ISO)

---

CULTURE & VALUES

Core values:
- Extreme Employee Obsession (Rule #1 AND Rule #2 of Coverflex — official quote)
- Transparency
- Integrity
- Accountability
- Continuous learning
- Culture that values questions — "there are no stupid questions"

Work mode:
- 100% remote-first since founding
- In-person meetings at least 2x per year (team retreats)
- Flexible hours — no clock-in, agreed with team
- All Hands periodically + open Q&A with leadership

Brand manifesto:
"We adapt. We change and grow. We're not measured by our titles. We focus on connecting, on personalisation, on adding value."

Glassdoor (culture rating: 4.7/5):
"Unusual transparency and openness. High ambition mixed with experience/rationality. Average team quality is very high."

---

EMPLOYEE BENEFITS (INTERNAL)

Compensation package:
- Stock Options via VSOP (Virtual Stock Option Plan) for ALL employees — pool of +11%. Managed on Ledgy platform.
- Coverflex Card (employees use their own product)
- Health insurance with family coverage option
- 25 working days paid vacation per year — request via rh@coverflex.com
- Extended parental leave: 2 additional paid weeks beyond legal maximum; children's birthdays are a day off
- 3 Caring Days per year: for projects with positive social impact (in-person or remote)
- MacBook provided

Annual budgets:
- Remote Work Budget: €1,000/year for technology (monitor, chair, etc.), coworking, or working away from home
- Personal Growth Budget: €1,000/year for courses, training, books, physical/psychological wellness, coaching
- Onboarding Budget: €500 (one-time, for new employees) to improve home workspace — available as soon as account is active

Salary references:
- Customer Success Manager: €33,000-40,000 base + bonus
- AI Engineer: €50,000-60,000 base + VSOP
- Backend Engineer: €50,000-80,000 base + VSOP
- Key Account Manager (Spain): €35,000-45,000 base + commissions
- Commercial roles: variable component (OTE 70/30 or 80/20)

---

INTERNAL ONBOARDING

First steps (first week):
1. Wait for welcome email (notifications@coverflex.com)
2. Create account at my.coverflex.com via invite link
3. Set up personal data: NIF/tax number, address, IBAN
4. Add health insurance dependents (deadline: 30 days — after that there's a waiting period)
5. Receive and activate Coverflex card when it arrives (up to 2 weeks)
6. Explore documentation on Notion
7. Join Slack and introduce yourself in #general channel

Tools to set up:
- my.coverflex.com — manage benefits and card
- Slack — daily communication; priority channels: #general, #hr, #support, #tech, #product
- Google Calendar — meetings and team agenda
- Notion — internal documentation (HR policies, product manuals, operational processes, FAQs)
- GitHub — code (technical team)
- Linear — product management
- HubSpot — CRM (commercial team)
- Intercom — customer support

First week checklist:
✅ Coverflex account active and data configured
✅ Dependents added to insurance (if applicable, within 30 days)
✅ Coverflex card received and activated
✅ Slack active — introduction in #general
✅ Notion documentation explored
✅ First team meeting
✅ First reimbursement submitted (e.g. Onboarding Budget of €500)
✅ Coverflex AI on WhatsApp set up

CEO quote about onboarding culture:
"If you've worked at a startup before, you will adapt quickly; if not, buckle up, because you are in for one hell of a ride." — Miguel Santo Amaro

---

CLIENT ONBOARDING

Process for company:
1. Platform subscription
2. Coverflex sends KYB form (~1 week after start)
3. Submission of required documents
4. Platform configuration and employee invitation
5. Employees receive welcome email and create account

Required KYB documents:
- Signed KYB form: shareholder data (name, tax number, country, % capital), signed by manager
- Permanent Certificate (or Deed of Incorporation): proves legal constitution
- RCBE (Central Register of Beneficial Owners): complete, updated
- Colored copies of ID card (front and back) or passport of all managers

Accepted formats: PDF, JPG, PNG (max 25MB)
Deadline: documents not sent in 15 days → account blocked

---

REIMBURSEMENT PROCESS

Steps:
1. Pay with personal card
2. Request invoice with name and tax number (date and amount visible)
3. Take photo of invoice
4. Upload to Coverflex platform, select correct category
5. After approval: reimbursement within 2 business days

Rejection reasons:
- Illegible invoice
- Incorrect/missing tax number
- Insufficient balance
- Expense not eligible in selected category
- Company internal policy

Important rules:
- Expenses paid with Coverflex card CANNOT be claimed as reimbursement
- Health expenses paid with Coverflex card do not count for tax purposes
- If pending request with wrong document: cancel and create new one

---

HEALTH INSURANCE

Coverage:
- Hospitalization: €50,000 | network: 90% insurer + 10% employee (min €250, max €500)
- Outpatient consultations: €5,000
- Childbirth: €3,000 | 90% insurer
- Medications: €250 | 80% insurer + 20% employee
- Prosthetics and orthotics: €1,000 (includes glasses and contact lenses)
- Serious illnesses: €1,000,000 for cancer, neurosurgery, cardiac bypass, transplants
- Outside network: 50% insurer + 50% employee

Waiting periods:
- Hospitalization: 90 days
- Outpatient consultations: 90 days
- Medications: 90 days
- Childbirth: 365 days
- Serious illnesses: 180 days (always applicable)

Dependents:
- Add via app → "Health Insurance" → "Add dependents"
- Deadline: 30 days after start
- Who can add: spouse/partner and children
- Monthly cost per dependent (Mar 2025 – Feb 2026): €76.33/month; children <18: €62.08/month

---

LOGIN & ACCESS

First access:
1. Follow invite link from company email
2. Click "Create account"
3. Set password and confirm data (tax number, address, IBAN)

Normal login:
- Coverflex app (iOS/Android) or my.coverflex.com
- Email + password + two-factor authentication code via SMS (valid 10 minutes)

Common problems:
- Expired invite link → request new invite via support chat or help@coverflex.com
- SMS code not received → wait up to 10 min, request new code
- Forgot password → "Recover password" → email with link for new password
- Change account email → only Coverflex team can do this; request via support chat

---

TECH STACK

Backend: Elixir, Phoenix, Phoenix LiveView, PostgreSQL, AWS, Kubernetes
DevOps: GitHub, GitHub Actions, ConfigCat, Datadog

AI team: OpenAI API, Vercel SDK, Langsmith/Braintrust/Langfuse, Cursor/Codex/Claude Code

Data stack: BigQuery, DBT, Semantic Layer, Prefect, Python, Hex, Lightdash, GCP, Terraform

Technical leadership:
- CTO and Co-Founder: Tiago Fernandes
- VP of Engineering: Bruno Oliveira
- Chief Architect: Carlos Silva

---

RECRUITMENT PROCESS

Steps:
1. CV/LinkedIn Screening — feedback within 7 days
2. Role-Fit Questionnaire — async questionnaire
3. Hiring Manager Interview — 45-60 min
4. Case / Work Sample — 20-30 min
5. Cultural Interview — 30-45 min
6. Final Conversation with CEO/C-Level — 30-45 min

Details:
- No cover letter required
- Decision within 4 weeks
- AI in recruitment: Teamtailor (CV anonymization) and ChatGPT (structured interview notes) — transparently; all applications reviewed by humans

---

CONTACTS & SUPPORT

- Portugal support: help@coverflex.com
- Spain support: ayuda@coverflex.com
- Italy support: aiuto@coverflex.com
- Human Resources: rh@coverflex.com
- Technical Support: it-support@coverflex.com
- Coverflex AI on WhatsApp: quick questions 24/7

Internal communication:
- Slack: #general, #hr, #support, #tech, #product + team channels
- Meetings: Google Calendar
- Documentation: Notion and Google Drive
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    history = data.get('history', [])
    conv_id = data.get('conv_id', str(uuid.uuid4()))
    lang = data.get('lang', 'en')

    if lang == 'pt':
        system = """És o assistente de conhecimento interno da Coverflex — fintech portuguesa líder em benefícios flexíveis, fundada em 2021, com presença em Portugal, Espanha e Itália.

Respondes SEMPRE em Português de Portugal. Tom profissional, claro e direto — como um colega sénior bem informado.

Regras:
1. Usa a informação da knowledge base
2. Se não tiveres informação, indica qual equipa contactar (RH: rh@coverflex.com, Suporte: help@coverflex.com)
3. Sê concreto e específico
4. Varia as aberturas — não comeces sempre com "Olá!"
5. Usa formatação clara quando útil"""
    else:
        system = """You are the internal knowledge assistant for Coverflex — a leading Portuguese fintech in flexible benefits management, founded in 2021, present in Portugal, Spain and Italy.

You ALWAYS respond in English. Professional, clear and direct tone — like a well-informed senior colleague.

Rules:
1. Use the information from the knowledge base
2. If you don't have enough information, indicate which team to contact (HR: rh@coverflex.com, Support: help@coverflex.com)
3. Be concrete and specific
4. Vary your openings — don't always start with "Hello!"
5. Use clear formatting when useful (lists, bold)"""

    messages = [{"role": "system", "content": system + "\n\nKnowledge Base:\n" + KNOWLEDGE_BASE}]
    for h in history[-8:]:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": message})

    try:
        r = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1000,
            temperature=0.65
        )
        response = r.choices[0].message.content
        related = get_related(message)

        # Save conversation
        all_messages = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": response}
        ]
        title = message[:40] + "..." if len(message) > 40 else message
        save_conv(conv_id, all_messages, title)

        return jsonify({
            "response": response,
            "related": related,
            "conv_id": conv_id
        })
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
