# Submission draft (Indie track) - NOT SUBMITTED

Due: Wed Nov 4, 2026, 9:00 PM ET (8:00 PM Central). Portal: https://cerebralvalley.ai/e/meta-ai-developer-hackathon/hackathon/submit

## What I could confirm (checked Nov 2, 2026, without logging in)
- The submit page needs a login. I could not see its form fields, the video length limit, or whether a public repo is required.
- The public event page says:
  - Submit through the Cerebral Valley portal link above.
  - Indie track: individuals and students, "judged on creativity, technical ambition, and whether it works."
  - A team's Representative submits and must list all team members in the submission.
  - Judging: Impact 30%, Use of Meta AI Tooling 25%, Technical Depth & Execution 20%, Demo 25%. The Demo score covers "the quality of the demo video", so a demo video is expected.
  - The Submission must be your own original work. You can get technical help from a third party if you still own the work. Open source is allowed if you follow its license.
  - The event waiver and Official Rules must be signed before any prize is paid.
- **Chris: log in and check the real fields.** Look for the video length limit, the video host (YouTube or Loom), and whether a public repo is required. Then copy in the answers below.

## Answers (paste these into the matching fields)

**Project name:** Is This a Scam?

**Track:** Indie developer

**Theme:** Build for Your World

**Team members:** Christopher Wright (solo)

**Tagline (one line):** Paste a text or add a screenshot, press one big button, and find out in plain words if it's a scam.

**Description:**
My name is Chris. I'm a dad of three from Huntsville, Missouri. I've spent twenty years training restaurant crews, so I know how to keep things simple. I want older folks protected from scams.
In 2024, people over 60 lost $4.885 billion across 147,127 complaints, per the FBI IC3 2024 Elder Fraud Report.
Is This a Scam? is one web page with big text and one button. You paste a message or add a screenshot. The app says "Likely Scam," "Be Careful," or "Looks OK." It lists the warning signs in plain words and gives one safe next step, plus the AARP Fraud Watch helpline number. It can read the answer out loud, and one tap starts a message to your family.

**How it uses Meta AI:**
- Muse Spark (muse-spark-1.3) through the Meta Model API's Chat Completions endpoint.
- Image input: the model reads screenshots of texts and emails and pulls out the words.
- Rules check first, and the model gets those findings. It answers in JSON with a verdict, reasons, and a next step.
- Safety first: the app combines the model and the rules and keeps the more careful answer. A strong rule hit, like gift cards or "keep it secret," can't be turned into "Looks OK."
- If the AI is down, the rules still answer. If a screenshot can't be read, the app says "Be Careful."

**Tech stack:** Python, FastAPI, plain HTML/JS, Web Speech API (read aloud), Meta Model API (Muse Spark).

**Testing:** 12 sample messages (10 scam types plus 2 real messages) pass when run live against the model (test_samples.py).

**GitHub repo:** https://github.com/whyitworks307/is-this-a-scam (public)

**Demo video:** [Chris: upload the voiced video and paste the link here] (source file: demo_silent.mp4, 1:37, plus VOICEOVER.md)

**AI assistance disclosure:**
I am a beginner. AI coding assistants helped me write much of the code, the docs, and this write-up, and they helped make the demo video. I picked the problem, made the design choices, tested it, and I understand how it works. The app itself uses Meta's Muse Spark model.

## Name ideas (if you want a different one)
Scam Check for Grandma · Ask Before You Pay · Second Look
