# HealthEase – Smart Health Appointment & Assistant System (Phase 1)

An AI-assisted healthcare appointment platform. This is **Phase 1**, with three working features:

1. **Login and registration with roles** – patients and doctors get separate dashboards.
2. **Appointment booking** – a patient picks a doctor and books a slot; the doctor accepts, cancels or asks to reschedule, then marks it completed and adds remarks.
3. **AI health chatbot** – general health guidance that suggests which type of doctor to see. Replies in Hindi when the user writes in Hindi.

Planned for later phases: Hindi voice input, digital prescription PDFs, PIN-code hospital search, automated medical reports, appointment reminders and WhatsApp integration.

## Tech stack
Python (Flask), Flask-Login, SQLAlchemy (SQLite locally), Bootstrap, Gemini / OpenRouter for the chatbot.

## Run locally
```bash
pip install -r requirements.txt
cp .env.example .env      # then edit .env and add a chatbot API key
python app.py
```
Open http://localhost:5000. With `SEED_DEMO=1` in `.env`, these demo accounts are created (password `Demo@1234`):

| Role | Email |
|---|---|
| Patient | patient@demo.com |
| Doctor | aarav.mehta@demo.com |

## Deploy on Vercel
1. Push this repo to GitHub.
2. In Vercel choose **Add New → Project**, import the repo and keep the default settings.
3. Add environment variables: `SECRET_KEY`, and `GEMINI_API_KEY` (or `OPENROUTER_API_KEY`) for the chatbot.
4. Deploy.

Note: on Vercel the default database is temporary and resets when the app restarts. For permanent data, set `DATABASE_URL` to a Postgres connection string (for example from Neon).

## Disclaimer
The chatbot gives general information only. It is not medical advice. Please consult a doctor.
