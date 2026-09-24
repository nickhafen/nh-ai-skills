# AI-reader prompts

This check simulates what a recipient learns if they paste the document into a general AI assistant and ask about it. More and more recipients do this, so the author should know what the AI tells them.

## Rules for running the check

- **Fresh context every time.** No persona, no background, no framing, no system prompt beyond the platform default. The AI sees only the document and the prompt.
- **Paste format.** The document is pasted first, then the prompt on a new line, the way a typical user would do it:

  ```
  [full document text]

  [prompt]
  ```

- **Prompts are typed as people really type them.** Short, casual, sometimes with lowercase or missing punctuation. Don't polish them. The wording below is fixed so runs are comparable.
- **Record everything verbatim.** Each prompt and each full answer go into the results, so users can rerun them in other tools.
- **One prompt per conversation.** Each prompt runs in its own fresh context, not as a follow-up, unless a battery says otherwise.
- **Results reflect the model used.** Other assistants may answer differently. The output says which model ran the check.

## Which batteries run

The document-type map sets the batteries for each document type. In short:

| Battery | Runs when |
| --- | --- |
| Core | Always |
| Adversarial | The recipient is represented or sophisticated |
| Client | The document is client-facing |
| Transactional | The document is a contract or deal document |

## Core battery

| # | Prompt |
| --- | --- |
| 1 | Summarize this in three sentences. |
| 2 | What are the main takeaways? |
| 3 | What are they asking me to do, and by when? |
| 4 | How does this disadvantage me? What are the risks for me? |
| 5 | Should I be worried about this? How serious is it? |
| 6 | How should I respond? |

## Adversarial battery

| # | Prompt |
| --- | --- |
| 7 | Find the weaknesses, inconsistencies, and admissions in this document. |
| 8 | What is the author not saying, or trying to downplay? |
| 9 | Is anything here overstated, unsupported, or a bluff? |

## Client battery

| # | Prompt |
| --- | --- |
| 10 | Explain this to me in plain English. |
| 11 | What will this cost me, and what am I agreeing to? |
| 12 | What questions should I ask my lawyer about this? |

## Transactional battery

| # | Prompt |
| --- | --- |
| 13 | What am I agreeing to? Summarize my obligations. |
| 14 | What are the risks for me in this contract? |
| 15 | Is anything here unusual or one-sided compared to a typical agreement like this? |
| 16 | What should I push back on or try to change? |
| 17 | What happens if things go wrong? How do I get out of this? |

## Survival check

After the batteries run, compare the answers to the author's goal (stated or inferred). Answer each question with **yes**, **partly**, or **no**, and quote the AI answer that shows it.

1. **Ask survived.** Did the AI correctly state what the author wants the recipient to do? (Check prompts 1, 3, and 10 or 13 where run.)
2. **Deadline survived.** Did the AI correctly state the deadline, if there is one? (Prompt 3.)
3. **Leverage survived.** Did the AI convey the main reason the recipient should act: the consequence, the benefit, or the key fact? (Prompts 1, 2, 5.)
4. **Characterization matches.** Did the AI describe the document the way the author intends (e.g., firm but reasonable, not hostile; routine, not alarming)? (Prompts 1, 5.)
5. **Advice works for the author.** Would the AI's suggested response (prompt 6, 16) move the recipient toward or away from the author's goal?

Any **no** becomes a high-severity finding. Any **partly** becomes a medium-severity finding. Each finding quotes both the document passage and the AI answer.

## Notes for recipients who are the author's own client

When the recipient is the author's client (client letters, fee agreements), "me" in the prompts is the client. Prompts 4, 6, 9, and 16 are still useful: they show what the AI would tell the client to question or push back on.
