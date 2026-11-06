# NeuroVision Therapy MVP

Android-friendly Streamlit prototype.

## Included
- Clinician portal: pseudonymous patient records, assessment data entry, clinician-authored therapy plans, session logging and outcome plots.
- Patient/parent portal: view assigned activities and a simple visual-search engagement demo.
- Evidence library with randomized clinical trial references and DOI links.
- SQLite database.

## Deploy from Android
1. Create a GitHub repository.
2. Upload `app.py` and `requirements.txt` to the repository root.
3. Open https://share.streamlit.io/ and sign in with GitHub.
4. Create an app using your repository, branch `main`, main file `app.py`.
5. Open the deployed URL in Android Chrome.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Critical safety, privacy and clinical limitations
- No authentication, role-based access control, encryption, audit trail, backup or production-grade security.
- Patient/parent and clinician workspaces are NOT securely separated in this prototype.
- Do not enter real patient identifiers, contact details, images or clinical records into a public/unapproved cloud deployment. Use fictional demo data only.
- This is not a medical device. It does not diagnose, prescribe, measure eye movements, assess visual acuity, deliver calibrated vergence/accommodation stimuli or replace examination.
- The visual-search game is for interface engagement only, not validated vision therapy or an outcome measure.
- Physical procedures (Brock string, vectograms, Hart chart, flippers) require clinician demonstration and suitable equipment; the app only records instructions.
- Review consent, data protection, security, hosting and applicable Indian legal/regulatory requirements before real-world use.
- Do not use this app to manage sudden vision loss, acute/new diplopia, new neurological symptoms or other urgent presentations.

## Evidence interpretation
CITT supports office-based vergence/accommodative therapy with home reinforcement for selected children with symptomatic convergence insufficiency. CITT-ART found improvements in NPC/PFV but no significant advantage in standardized reading outcomes. Do not generalize these results to all binocular vision anomalies, amblyopia, strabismus, dyslexia, learning disability or cerebral visual impairment.
