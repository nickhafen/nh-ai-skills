# Build your own feedback skill

Your goal is to create a prompt or skill that gives peer feedback the way you
would. The steps below say what to do; the suggestions under each are options,
not requirements.

[peer-feedback-hafen](../peer-feedback-hafen/SKILL.md) is a simple example.

## Ground rules

- **Follow the syllabus policy on other students' work:**

  > "Students will be engaging in peer critiques and may have ideas about
  > their own work while critiquing another person's written work. Students
  > are welcome to think through ideas that came to them during the editing
  > process at a later time but should never retain another student's work in
  > any form for later reference. If a student has any questions about this
  > policy, they should ask the professors before engaging in any behavior that
  > could jeopardize the student's academic standing."

- **Don't use real client information.**
- **When you use the skill, follow each assignment's AI policy.**

## 1. Decide what your feedback is for

Pick the documents, the reader you're reviewing for, and what the feedback
should look like.

*Suggestions*

- Start with one document type, such as client letters, and add others once it
  works.
- Decide where it will live: a prompt you paste or keep in a Project or Gem, or
  a skill. A good prompt is a fine start; a skill lets you split examples and
  reference material into separate files.
- Sketch the output you want: a summary note, margin comments, or both.

## 2. Give the AI examples of your feedback

Examples teach your judgment and voice better than any description. Aim for
pairs of a draft and your feedback on it.

*Suggestions*

- Use feedback you've received on your own drafts this semester (fee agreement,
  demand letter, complaint, client letter).
- Mark up the [sample feedback worksheet](sample-feedback.docx).
- Ask the AI to write more sample drafts for you to mark up. This creates
  "training data" when you don't have much of your own.
  - Ask for a mix of problems, big-picture and line-level.
  - Include at least one strong draft, so the AI learns not to invent
    problems.
  - Add a one-line "why I flagged this" to some comments. Reasons teach
    judgment; phrasing alone teaches style.
  - Keep your comments as you'd naturally write them. Cleaned-up comments teach
    a voice that isn't yours.

## 3. Spell out your standards

Write down what you look for, what you let go, and how you sound.

*Suggestions*

- Put the course's five writing principles in your own words: organized, plain,
  precise, concise, clean.
- List your pet peeves and favorite fixes ("in the event that" > "if").
- Note what you deliberately don't comment on.
- Describe your voice: blunt or gentle, questions or directives, how much
  praise.
- Give the AI your examples and ask what patterns it sees, or ask it to
  interview you. Then correct what it gets wrong.

## 4. Give it the context for each document type

Good feedback depends on what the document is for. For each type you cover, tell
the AI five things: the audience, the purpose, the components, the strategic
considerations, and the ethical considerations.

*Suggestions*

- Draw on the readings (*Writing for Litigation*) and each assignment's editing
  criteria.
- Ask the AI to draft the five points for a document type, then check them
  against what you've learned. Verify any rule it cites.
- Tell it to raise strategic and ethical points as questions for the writer,
  not as rulings.
- Include a fallback for document types you didn't cover.

## 5. Tell it how to give feedback

Your examples show your voice; this step tells the AI how to run a review.

*Suggestions*

- Build in the course's five feedback principles: focus on the writing, not the
  author; meet the paper where it is (global to granular); be specific; be
  constructive; be positive.
- Give it an order of work: read the whole draft, find what works, then
  diagnose from big picture to line level.
- Set the output format, such as a short overall note, then big-picture
  comments, then line comments.
- Set limits: feedback only, no rewriting; a cap on line comments; one mention
  per recurring pattern.
- End with a self-check, such as "Does every comment quote the words it's about
  and offer a fix?"

## 6. Assemble it

Put the pieces together in the form you chose in step 1.

*Suggestions*

- **As a prompt:** one document with sections for your standards, context,
  process, output format, and examples. Paste it into a chat or save it as a
  Project's or Gem's instructions.
- **As a skill:** a short main file (what it does, when to use it, the steps,
  the output format) that points to separate files for examples, standards, and
  document context. [Professor Hafen's example skill](../peer-feedback-hafen/SKILL.md)
  uses this structure.
- Ask the AI to assemble it from your materials, or use the Skill Creator at
  [nickhafen.github.io/nh-ai-utilities](https://nickhafen.github.io/nh-ai-utilities).
- Upload a skill as a zipped folder so the supporting files come with it.
- Write the skill's description to say when to use it ("Use when asked for peer
  feedback on a legal draft"). That's how the AI decides to load it.

## 7. Test it against yourself, then revise

The only way to know it sounds like you is to compare it with you.

*Suggestions*

- Hold back one draft you've marked up. Run the skill on it in a fresh chat and
  compare its feedback with yours.
- Ask: What did it miss? What did it add that you wouldn't say? Does it sound
  like you? Did it get the priorities right?
- Run it on a strong draft and check that it doesn't invent problems.
- Run the same draft without your skill and compare. If the feedback is no
  better, your examples or standards need work.
- To make that comparison more systematic, ask Claude to use its skill-creator
  skill to run an eval of your skill against plain Claude with no skill. It runs
  both on the same drafts and shows the results side by side.
- Fix the gap you see, then test again. Usually the fix is a better example,
  not more rules.

## 8. Keep improving it

Your skill gets better as you add examples and as your judgment as a writer
grows. Refine it every time you use it.

*Suggestions*

- Mark up more sample drafts. Ask the AI for new flawed drafts of the document
  types your skill handles least well, mark them up, and add the best pairs to
  your examples.
- Add your own drafts and the feedback you get on them as the semester goes on,
  following the ground rules above.
- When the skill's feedback misses or overreaches on a real review, capture it:
  add that draft with the feedback you'd actually give.
- Add context for each new document type you learn (letters to opposing
  counsel, motions, responses).
- Update your standards as they change. If you've stopped caring about
  something or started caring about something new, say so.
- Prune as you go. Replace weak or outdated examples rather than piling on
  more; a handful of good ones beats dozens of mediocre ones.
- Rerun your step 7 test after big changes to make sure it still sounds like
  you.
