# Submission draft (Indie track) — NOT submitted

## Name ideas
- Is This a Scam?
- Scam Check for Grandma
- Ask Before You Pay
- SafeCheck
- Second Look

## Short description (Chris, first person)
My name is Chris. I built a simple tool to help older people spot scams.
Older adults get a lot of scam texts and calls. They are a big target.
You paste a message, or add a screenshot. Then you press one big button.
The app says "Likely Scam," "Be Careful," or "Looks OK." It lists the warning signs in plain words.
It tells you one safe thing to do next, and gives the AARP Fraud Watch helpline number.
It can read the answer out loud. It can also send the message to your family with one tap.
It uses Meta's Muse Spark model to read the message and screenshots. It also uses simple rules,
like "asks for gift cards" or "says keep it secret." The app combines both and picks the safer answer.
If the AI is not available, the rules still work.

## How I used Meta AI
- Muse Spark (muse-spark-1.3) through the Meta Model API, Chat Completions endpoint.
- Image input: it reads screenshots of texts and emails.
- Structured JSON output, guided by the rule-based findings.

## Honest note
I am a beginner. I used AI coding help to write a lot of this code. I tested it and I understand how it works.
