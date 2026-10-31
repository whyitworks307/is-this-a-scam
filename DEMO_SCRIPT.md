# 2-minute demo: screen recording + voiceover (no face on camera)

**Setup:** Chrome at 1280x800, zoom 125%. Server running with META_API_KEY set (no DEMO MODE banner).
Record system audio for the Read Out Loud part. Have `sample_scam_screenshot.png` on the desktop.
Speak slowly. Each line is short on purpose. About 260 spoken words total.

| Time | Screen | Chris says (exact words) |
|---|---|---|
| 0:00–0:20 | Title card: "Is This a Scam?" with the stat and source line under it. | "Hi, I'm Chris. I'm a dad of three from Missouri. Older people get a lot of scam texts and calls. In 2024, people over 60 reported almost 4.9 billion dollars in losses to the FBI. So I built a simple way to check a message before you pay or reply." |
| 0:20–0:30 | Open the app. Slowly move the mouse over the big text box and the one blue button. | "It's one page. Big text. One button. No account and no menus." |
| 0:30–0:55 | Click the "Grandchild in trouble" sample. Click **Check It**. Red "Likely Scam" appears. Hover over each reason. | "Here's a message that says a grandchild is in jail and needs money. I paste it in and press Check It. It says Likely Scam. It tells you why in plain words. It says a loved one is in jail, it wants money fast, and it says keep it secret. Then it gives one safe step. Call your grandchild yourself first." |
| 0:55–1:15 | Clear the box. Click **Choose File**, pick `sample_scam_screenshot.png`. Click **Check It**. Verdict appears. | "A lot of people can't copy text off their phone. So you can just add a screenshot. The app reads the picture and checks it the same way." |
| 1:15–1:25 | Click **Read Out Loud**. Let it speak for a few seconds. | "If small print is hard to read, it reads the answer out loud." |
| 1:25–1:35 | Click **Send to My Family**. Show the prefilled message. Don't send it. | "And one tap starts a message to family. That way nobody has to decide alone." |
| 1:35–1:50 | Show the architecture diagram from README, or the "Checked by: Meta muse-spark-1.3 + rules" line. | "Here's how it works. Simple rules look for big warning signs, like gift cards or keep it secret. Meta's Muse Spark model reads the message or the picture and explains it. If they disagree, the app picks the safer answer. If the AI is down, the rules still work." |
| 1:50–2:00 | Back to the app with the red verdict. Fade out. | "I built this for my family and yours. Before you pay, check it. Thanks for watching." |

## Stat source
- "$4.885 billion in losses from 147,127 complaints" by people 60+ in 2024 (FBI IC3).
  - FBI press release: https://www.fbi.gov/news/press-releases/fbi-recognizes-world-elder-abuse-day-and-reminds-americans-of-elder-fraud
  - IC3 2024 Elder Fraud Report: https://www.ic3.gov/AnnualReport/Reports/2024_Elder_Fraud_Report.pdf
  - Spoken as "almost 4.9 billion dollars". These are reported losses only. Don't call them total losses.
- Any other number you add: mark it [Chris to verify].

## Before recording
- Run `python test_samples.py` once to make sure everything passes.
- Check the screenshot demo in live mode. Demo mode can't read pictures.
- Keep the key out of the video. Don't show the terminal or `.env`.
