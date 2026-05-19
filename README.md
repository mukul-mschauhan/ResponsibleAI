# Responsible AI Banking Control Tower

A Streamlit-based banking demo that shows how Responsible AI can be operationalized around a credit-card fraud detection use case.

The purpose of this demo is not to prove that a fraud model is production-ready. The purpose is to demonstrate the governance layer a bank should put around AI decisions: explainability, fairness monitoring, privacy controls, human oversight, audit logging, and post-deployment monitoring.

## Demo positioning

**Business title:** Responsible AI in Credit Card Fraud Detection  
**Client context:** Banking, compliance, data privacy, AI governance, fraud risk, model risk management  
**Suggested workshop name:** Responsible AI Banking Control Tower

## What this app demonstrates

1. Transaction simulation using synthetic banking data
2. Fraud score generation using a transparent demo model
3. Risk classification and suggested action
4. Explainability through operational reason codes
5. Responsible AI control checks
6. Bias and fairness monitoring across approved business segments
7. Human-in-the-loop review and override
8. Audit trail generation
9. Model performance and drift-style monitoring dashboard
10. Responsible AI scorecard

## Responsible AI concepts covered

- Fairness
- Explainability
- Accountability
- Privacy and confidentiality
- Human oversight
- Auditability
- Model monitoring
- Customer protection
- Misuse prevention
- Safe GenAI usage, where Claude is used only for explanation and not decisioning

## Important disclaimer

This app uses **synthetic data only**. It is meant for education, executive demos, and Responsible AI workshops. It is not a production fraud detection system, legal advice, regulatory certification, or model validation report.

## Project structure

```text
rai_banking_control_tower/
├── streamlit_app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── .streamlit/
│   └── config.toml
├── data/
│   └── audit_log.csv              # Generated when decisions are logged
└── src/
    ├── audit_logger.py
    ├── config.py
    ├── data_generator.py
    ├── explainability.py
    ├── llm_explainer.py
    ├── model.py
    ├── rai_engine.py
    └── ui_components.py
```

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\Scripts\activate        # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run streamlit_app.py
```

## Optional Claude integration

The app works without an LLM. If you want Claude to generate polished business explanations, create a `.env` file:

```bash
cp .env.example .env
```

Then add your API key:

```text
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-latest
```

Claude is used only to explain model outputs. It does not make the fraud decision.

### Opening message

Banks should not deploy AI by asking only, "Is the model accurate?" A responsible bank asks whether the AI decision is fair, explainable, privacy-safe, monitored, auditable, and controlled by humans where customer harm is possible.

### Demo scenario 1: High-risk fraud

Use: `High-risk cross-border electronics purchase`

Message: The model catches suspicious behavior, but the bank still applies explainability, human oversight, privacy masking, and audit logging.

### Demo scenario 2: Genuine customer travelling abroad

Use: `Genuine customer travelling abroad`

Message: Responsible AI reduces unnecessary customer harm. The system should verify rather than blindly block.

### Demo scenario 3: Bias monitoring

Open the Fairness tab and monitor by travel profile, income band, tenure band, country, or channel.

Message: Responsible AI checks whether a model is over-flagging certain customer segments.

### Demo scenario 4: Human review and audit

Open Human Review, write a decision to audit log, then open the Audit Log tab.

Message: A bank must be able to reconstruct why a decision was made, which model version was used, who reviewed it, and what action was taken.

## Recommended talking points

- AI detects risk; Responsible AI governs the decision.
- Fraud detection must balance bank protection and customer protection.
- False positives are not just model errors; they are customer harm.
- Explainability is required for analysts, auditors, customer support, and regulators.
- Human oversight should be placed at high-impact decision points, not everywhere.
- Privacy and confidentiality must be designed into the workflow.
- Responsible AI is not a blocker to adoption; it is the control framework that enables safe adoption.

## GitHub push instructions

```bash
git init
git add .
git commit -m "Initial Responsible AI banking control tower demo"
git branch -M main
git remote add origin https://github.com/<your-username>/rai-banking-control-tower.git
git push -u origin main
```

## Deployment on Streamlit Community Cloud

1. Push this folder to GitHub.
2. Go to Streamlit Community Cloud.
3. Create a new app.
4. Select your repository.
5. Set main file path as `streamlit_app.py`.
6. Add `ANTHROPIC_API_KEY` in Streamlit secrets only if you want optional Claude explanations.

## Production hardening ideas

For a real bank, this demo would need significant hardening:

- Real model validation process
- Regulatory mapping by jurisdiction
- Data privacy impact assessment
- Access control and authentication
- Secure audit storage
- Model registry
- CI/CD approval workflow
- Formal bias testing framework
- Adversarial fraud testing
- Customer dispute integration
- Incident response playbook
- Third-party risk controls
- Legal and compliance approval

## License

MIT-style usage for educational and demo purposes. Review before commercial use.
