# Fetched content from Project/JudgeAgent.py [cite: 3]
import concurrent.futures
from typing import Any, Dict, List
from llm_helper import call_llm_api # Assuming llm_helper is in the same directory or accessible
import re

# --- Keep your existing ANALYSIS_LAYERS definition ---
ANALYSIS_LAYERS = [
    {
        "focus": "Logical Consistency",
        "prompt_template": """You are an advanced debate judge AI whose exclusive focus is to assess the logical structure and consistency of a debater's arguments. Your role is not to evaluate factual correctness or persuasive style, but to determine whether the debater's reasoning is coherent and free from logical fallacies.

      The debate under review concerns:
      "{topic}"

      The debater has adopted the following stance:
      "{stance}"

      Below are all their arguments across the debate rounds:
      {argument}

      As you read and analyze these arguments, follow this in-depth approach:

      1) Identify and Classify Logical Fallacies:
         - Determine if any arguments contain classical errors in reasoning (e.g., ad hominem attacks, straw man distortions, false dichotomies, hasty generalizations). 
         - Pinpoint where these fallacies occur, and assess how severely they undermine the overall coherence.

      2) Check for Internal Contradictions and Self-Consistency:
         - Examine whether the debater's claims in earlier rounds conflict with later statements.
         - Note any shifts in stance or logic that go unaddressed or unexplained, thus creating contradictions within the overall position.

      3) Evaluate the Validity of the Debater's Reasoning Structures:
         - Look at how premises connect to conclusions—are these connections logically sound, or do they rely on assumptions not sufficiently supported?
         - Consider whether the reasoning has discernible weak links or ambiguities that cast doubt on the conclusions.

      4) Assess the Strength of Logical Progression:
         - Judge whether the debater's arguments build upon each other in a way that is consistent and cohesive across rounds.
         - Check for clarity in how each new point follows from (or enhances) preceding points, and whether transitions are well-supported.

      After completing your detailed internal analysis, present your user-facing evaluation in the format below:

      LOGICAL CONSISTENCY SCORE: [score from 0-10]
      (Where 0 indicates multiple severe logical breakdowns, 5 indicates mostly sound logic with a few minor flaws, and 10 indicates impeccable logical structure throughout.)
      For example:
      LOGICAL CONSISTENCY SCORE: 8
      
      CRITIQUE (200 words):
      [Write precisely 200 words that summarize the key issues related to logical structure, including notable fallacies, any contradictions, and major areas for improvement. You may highlight particular arguments or rhetorical devices that either strengthen or weaken coherence. This critique should remain focused on the logical dimension of the debate, without venturing into factual correctness or persuasive style.]"""
    },
    {
        "focus": "Rhetorical Effectiveness",
        "prompt_template": """You are an advanced debate judge AI whose sole responsibility is evaluating the persuasive and stylistic elements of a debater's performance. You are not concerned with factual correctness or pure logical consistency; instead, you focus on how effectively the debater conveys their message, engages the audience, and sustains rhetorical impact across all rounds.

      The debate you are judging is centered on:
      "{topic}"

      The debater has taken the following stance:
      "{stance}"

      Their consolidated arguments across the debate are as follows:
      {argument}

      To arrive at a nuanced assessment, apply this comprehensive methodology:

      1) Clarity and Focus of the Central Thesis:
         - Examine whether the debater maintains a clear, coherent thesis throughout. 
         - Note if any sections become muddled, repetitive, or lose track of the central claim.

      2) Emotional Appeal and Audience Engagement:
         - Assess the use of emotive language, storytelling, anecdotes, and other techniques meant to resonate with listeners. 
         - Gauge whether the emotional components align with the debate context or come across as manipulative, off-topic, or extraneous.

      3) Language, Style, and Delivery:
         - Observe how the debater's word choices, metaphors, tone, and overall narrative style contribute to or detract from persuasiveness.
         - Consider whether the speaker uses jargon or technical terms effectively or if it confuses the audience.

      4) Anticipating Counterarguments and Rebuttals:
         - Determine how effectively the speaker pre-empts opposing views or responds to challenging questions.
         - Look for missed opportunities where a decisive rebuttal could have strengthened the presentation.

      5) Flow and Overall Convincingness:
         - Consider how smoothly the argument transitions from one point to the next, forming a cohesive arc. 
         - Evaluate whether the debater's style and progression sustain a compelling momentum from opening to closing statements.

      Once you have completed this detailed internal analysis, provide your final user-facing output as follows:

      PERSUASIVE QUALITY SCORE: [score from 0-10]
      (Where 0 indicates thoroughly unconvincing rhetoric, 5 indicates a moderately effective presentation, and 10 indicates masterful rhetorical skill throughout.)
      For example:
      PERSUASIVE QUALITY SCORE: 8
      
      CRITIQUE (200 words):
      [Compose exactly 200 words that highlight the strongest rhetorical devices, the areas needing better structure or clarity, and how well the debater connected with their audience. Focus on the speaker's style, emotional appeal, use of language, and skill in countering opposition. Avoid commenting on factual correctness or logical consistency unless it directly impacts rhetorical effect.]"""
    },
    {
        "focus": "Factual Accuracy",
        "prompt_template": """You are an advanced debate judge AI whose sole focus is evaluating the factual accuracy of arguments across multiple debate rounds. Your analysis must be methodical, rigorous, and based on established principles of factual verification.
      
      You will evaluate the following argument from a debater who took the {stance} position on the topic: "{topic}".
      
      {argument}
      
      Your task is to evaluate the OVERALL factual accuracy of this debater's position, following these specific criteria:
      
      1. CLAIM VALIDITY:
         - Compare each stated fact against established knowledge or robust data
         - Verify quantifiable details (numbers, dates, names, places) for accuracy
         - When facts are ambiguous or contested in the field, note the level of uncertainty
         - Identify if claims contradict each other within the debater's own arguments
      
      2. SOURCE QUALITY:
         - Evaluate whether cited sources (if present) are credible, reputable, and relevant
         - Distinguish between high-quality references (academic journals, expert analyses) and lower-quality sources (anecdotes, potentially biased outlets)
         - Consider whether specialized claims are backed by appropriate specialized evidence
         - Assess if the debater misrepresents the reliability or consensus status of their sources
      
      3. EVIDENCE COMPLETENESS:
         - Determine if the debater has provided sufficient evidence for their major claims
         - Identify significant omissions of relevant evidence that would be standard to include
         - Assess whether the debater acknowledges limitations in the available evidence
         - Consider if sweeping conclusions are drawn from limited factual foundations
      
      4. CONTEXTUAL INTEGRITY:
         - Examine whether facts are presented with appropriate context or misleadingly framed
         - Detect cherry-picking of data, straw man representations, or overgeneralizations
         - Assess whether quoted materials maintain their original meaning and intent
         - Identify if causal relationships are improperly inferred from correlational data
      
      Rate the overall argument on a scale of 0-10 for factual accuracy, where:
      0 = Pervasive factual inaccuracies and irreconcilable errors that discredit the position
      5 = Generally correct information but with notable errors, omissions, or unclear sourcing
      10 = Meticulous factual correctness with thorough, credible, and comprehensive supporting evidence
      
      Provide your evaluation in this format:
      
      FACTUAL ACCURACY SCORE: [score]
      For example:
      FACTUAL ACCURACY SCORE: 8
      
      CRITIQUE (200 words):
      [Provide a precisely 200-word critique that highlights the most crucial factual strengths and weaknesses. Mention any significant errors, the reliability of cited sources, and the sufficiency of evidence. Offer clear direction on where factual substantiation could be improved.]"""
    },
    {
        "focus": "Belief Impact",
        "prompt_template": """You are an advanced debate judge AI focused exclusively on determining how effectively a debater's arguments could shift the beliefs of various audiences. Your primary measure is the likelihood of changing minds, not merely how logical or factual the arguments are in isolation.

      The topic of the debate is:
      "{topic}"

      The debater's stance:
      "{stance}"

      The argument made by this debater is provided here:
      {argument}

      Your approach should be multi-perspectival and encompass the following elements:

      1) Impact on Opposing Audiences:
         - Estimate how convincing these arguments would be to individuals who began firmly against this stance. 
         - Note any concessions, empathetic language, or compelling evidence aimed specifically at persuading skeptics.

      2) Impact on Neutral or Undecided Audiences:
         - Analyze whether the speaker's logic, evidence, or rhetorical style provides enough clarity and momentum to guide someone with no prior opinion toward a supportive or more favorable viewpoint.
         - Consider if the arguments address common concerns or misconceptions that neutral listeners might have.

      3) Impact on Already Supportive Audiences:
         - Determine whether these arguments reinforce existing support or deepen understanding among those who initially agree. 
         - See if the debater's points offer novel perspectives or stronger justifications that further solidify agreement.

      4) Overall Persuasion Across Diverse Viewpoints:
         - Look for broad appeal or universal values embedded in the presentation that might span ideological or experiential differences.
         - Identify any alienating phrases, aggressive posturing, or assumptions that might inadvertently reduce the arguments' appeal to certain segments.

      After thoroughly analyzing belief-shifting elements, present your findings in this format:

      BELIEF-SHIFT SCORE: [score from 0-10]
      (Where 0 signals virtually no chance of changing anyone's mind and possibly entrenching opposition, 5 signals moderate impact mostly on neutral listeners, and 10 signals a high likelihood of swaying even those initially opposed.)
      
      For example:
      BELIEF-SHIFT SCORE: 8

      CRITIQUE (200 words):
      [In exactly 200 words, detail how well the arguments are likely to alter viewpoints, noting strengths and weaknesses in targeting different audiences. Highlight any key points that could convert skeptics, refine or reinforce believers' convictions, and address those on the fence. Emphasize major opportunities for improving reach and reducing pushback.]"""
    }
]
# --- End of ANALYSIS_LAYERS ---

class JudgeAgent:
    """Represents an AI agent (or interface for a human) evaluating the debate."""

    def __init__(self, name: str = "AI Judge", model_name: str = "gpt-4-turbo", use_strategic_layers: bool = True, max_workers: int = 4):
        """
        Initializes the Judge Agent.

        Args:
            name (str): Name of the judge.
            model_name (str): LLM model used by the judge.
            use_strategic_layers (bool): Whether to use the defined ANALYSIS_LAYERS for evaluation.
            max_workers (int): Max number of threads for parallel feedback generation.
        """
        self.name = name
        self.model_name = model_name
        self.use_strategic_layers = use_strategic_layers
        self.max_workers = min(max_workers, len(ANALYSIS_LAYERS))
        self.system_prompt = "You are an impartial debate judge."
        self.context = [{"role": "system", "content": self.system_prompt}]
        print(f"Initialized Judge: {self.name} (Model: {self.model_name}, Parallel Layers: {self.use_strategic_layers}, Max Workers: {self.max_workers if self.use_strategic_layers else 'N/A'})")

    # --- Keep your existing check_word_count function ---
    def check_word_count(self, argument: str, debater_name: str) -> bool:
        """
        Checks if a debater's argument meets the word count requirements.

        Args:
            argument (str): The debater's argument text
            debater_name (str): Name of the debater

        Returns:
            dict: Result containing word count, compliance status, and feedback
        """
        words = argument.split()
        word_count = len(words)
        target = 520 # Example target word count

        print(f"\n[JUDGE] Word Count Check - {debater_name}: {word_count} words")

        # Determine compliance (True if over limit in original code, let's make it True if compliant)
        if word_count <= target:
             print(f"[JUDGE] Word count is compliant for {debater_name}.")
             return True # Compliant
        else:
             print(f"[JUDGE] Word count EXCEEDED for {debater_name}.")
             return False # Not compliant


    def _run_layer_analysis(self, layer: Dict[str, str], argument: str, debater_name: str, topic: str, round_num: int) -> Dict[str, str]:
        """Helper function to run analysis for a single layer."""
        try:
            layer_prompt = layer["prompt_template"].format(argument=argument, stance=debater_name, topic=topic)
            full_layer_prompt = f"{self.system_prompt}\nDebate Topic: {topic}\nRound: {round_num}\nAnalyze based on '{layer['focus']}':\n{layer_prompt}"
            # print(f"DEBUG: Calling LLM for layer '{layer['focus']}'") # Optional debug print
            layer_analysis = call_llm_api(full_layer_prompt, self.model_name) # Context management might be simplified here for parallel calls
            # print(f"DEBUG: Received LLM response for layer '{layer['focus']}'") # Optional debug print
            return {"focus": layer['focus'], "analysis": layer_analysis}
        except Exception as e:
            print(f"Error during analysis layer '{layer['focus']}': {e}")
            return {"focus": layer['focus'], "analysis": f"Error generating analysis: {e}"}


    def evaluate_argument(self, argument: str, debater_name: str, topic: str, round_num: int) -> str:
        """
        Evaluates a single argument using the LLM or predefined rules.
        Uses parallel execution if use_strategic_layers is True.

        Args:
            argument (str): The argument text to evaluate.
            debater_name (str): The name of the debater who made the argument.
            topic (str): The debate topic.
            round_num (int): The current round number.

        Returns:
            str: Constructive feedback for the debater.
        """
        print(f"{self.name} evaluating argument from {debater_name}...")

        # --- Check word count BEFORE expensive LLM calls ---
        is_compliant = self.check_word_count(argument, debater_name)
        word_count_feedback = ""
        if not is_compliant:
            # Decide if you want to stop evaluation or just add feedback
            # Option 1: Stop evaluation (example)
            # return f"Feedback for {debater_name}: Argument exceeded word limit ({len(argument.split())} words). Please adhere to the 520-word limit."
            # Option 2: Add feedback and continue (used below)
             word_count_feedback = f"\nWarning: The argument exceeded the 520-word requirement ({len(argument.split())} words).\n"
        # --- End word count check ---


        feedback = ""
        if self.use_strategic_layers:
            print(f"Running strategic layer analysis in parallel (max_workers={self.max_workers})...")
            full_feedback = f"Feedback for {debater_name} on Round {round_num} (Topic: {topic}):\nArgument:\n'''{argument}'''\n\nAnalysis:\n"
            layer_results = []

            # Use ThreadPoolExecutor for parallel API calls
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Prepare future tasks
                future_to_layer = {
                    executor.submit(self._run_layer_analysis, layer, argument, debater_name, topic, round_num): layer
                    for layer in ANALYSIS_LAYERS
                }

                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_layer):
                    layer_name = future_to_layer[future]['focus']
                    try:
                        result = future.result()
                        layer_results.append(result)
                        print(f"Completed analysis layer: {result['focus']}") # Progress indicator
                    except Exception as exc:
                        print(f"Layer '{layer_name}' generated an exception: {exc}")
                        layer_results.append({"focus": layer_name, "analysis": f"Error during analysis: {exc}"})

            # Sort results back into original order (optional, but good for consistency)
            layer_results.sort(key=lambda x: [l['focus'] for l in ANALYSIS_LAYERS].index(x['focus']))

            # Assemble feedback
            for result in layer_results:
                full_feedback += f"\n--- {result['focus']} ---\n{result['analysis']}\n"

            feedback = full_feedback

        else:
            # Comprehensive single-prompt evaluation incorporating all analysis layers
            print("Running comprehensive single prompt evaluation...")
            prompt = (
                f"{self.system_prompt}\n"
                f"Debate Topic: {topic}\nRound: {round_num}\nDebater: {debater_name}\n"
                f"Evaluate the following argument:\n'''{argument}'''\n\n"
                f"Provide a comprehensive evaluation covering these key areas:\n\n"
                
                f"1) LOGICAL CONSISTENCY:\n"
                f"- Identify any logical fallacies (ad hominem, straw man, false dichotomies, hasty generalizations)\n"
                f"- Assess internal contradictions and self-consistency of claims\n"
                f"- Evaluate how premises connect to conclusions\n"
                f"- Analyze the strength of logical progression and cohesiveness\n\n"
                
                f"2) RHETORICAL EFFECTIVENESS:\n"
                f"- Assess clarity and focus of the central thesis\n"
                f"- Evaluate emotional appeal and audience engagement techniques\n"
                f"- Analyze language, style, and delivery effectiveness\n"
                f"- Examine how well counterarguments are anticipated and addressed\n"
                f"- Consider flow and overall persuasiveness\n\n"
                
                f"3) FACTUAL ACCURACY:\n"
                f"- Verify claim validity against established knowledge\n"
                f"- Evaluate quality and credibility of sources (if cited)\n"
                f"- Assess evidence completeness and sufficiency\n"
                f"- Check for contextual integrity and proper framing of facts\n\n"
                
                f"4) BELIEF IMPACT:\n"
                f"- Estimate persuasive impact on opposing audiences\n"
                f"- Analyze effectiveness for neutral/undecided audiences\n"
                f"- Consider reinforcement value for already supportive audiences\n"
                f"- Identify any elements that might reduce appeal to certain audiences\n\n"
                
                f"Provide specific, constructive feedback that will help the debater improve their argument. Be balanced and fair in your assessment.\n\n"
                f"IMPORTANT: After your analysis, provide quantitative scores on a scale of 1-10 for the following categories:\n"
                f"- LOGICAL CONSISTENCY SCORE: [score]\n"
                f"- PERSUASIVE QUALITY SCORE: [score]\n"
                f"- FACTUAL ACCURACY SCORE: [score]\n"
                f"- BELIEF-SHIFT SCORE: [score]\n"
                f"For example, your output should look like below with the only change be the score:\n"
                f"- LOGICAL CONSISTENCY SCORE: 9\n"
                f"- PERSUASIVE QUALITY SCORE: 7\n"
                f"- FACTUAL ACCURACY SCORE: 8\n"
                f"- BELIEF-SHIFT SCORE: 10\n"
            )
            feedback = call_llm_api(prompt, self.model_name) # Context management might be needed
        
        # Separate the textual feedback from the scores (e.g., using string splitting or regex)
        # For example (this is basic, regex might be more robust):
        try:
            feedback_text = feedback.split("IMPORTANT:")[0].strip() # Or split based on score markers
            scores = {}
            # Example parsing (needs refinement based on actual LLM output format)
            lines = feedback.splitlines()
            for line in reversed(lines): # Start from the end
                if "LOGICAL CONSISTENCY SCORE" in line:
                    scores['logic'] = float(re.search(r"[-+]?\d*\.?\d+", line).group())
                elif "PERSUASIVE QUALITY SCORE" in line:
                    scores['persuasive'] = float(re.search(r"[-+]?\d*\.?\d+", line).group())
                elif "FACTUAL ACCURACY SCORE" in line:
                    scores['factual'] = float(re.search(r"[-+]?\d*\.?\d+", line).group())
                elif "BELIEF-SHIFT SCORE" in line:
                    scores['belief'] = float(re.search(r"[-+]?\d*\.?\d+", line).group())
                if len(scores) == 4:
                    break # Stop once all scores found
            if len(scores) != 4: # Handle case where parsing failed
                print("[WARN] Failed to parse all scores from LLM response.")
                scores = {'logic': 0, 'persuasive': 0, 'factual': 0, 'belief': 0} # Default scores with new keys
        except Exception as e:
            print(f"[ERROR] Could not parse scores: {e}")
            feedback_text = feedback # Keep original response if parsing fails
            scores = {'logic': 0, 'persuasive': 0, 'factual': 0, 'belief': 0} # Default scores with new keys

        # Add word count feedback if needed
        feedback_text += word_count_feedback

        print(f"{self.name} generated feedback and scores for {debater_name}.")
        return feedback_text, scores 

    # --- Keep your existing declare_winner function ---
    def declare_winner(self, debate_history: List[Dict[str, Any]], topic: str) -> str:
        """
        Evaluates the entire debate and declares a winner (or assesses overall performance).

        Args:
            debate_history (List[Dict[str, Any]]): A log of the entire debate.
            topic (str): The debate topic.

        Returns:
            str: A summary of the debate outcome.
        """
        print(f"{self.name} evaluating the overall debate...")
        history_summary = "\n".join([f"Round {turn['round']} - {turn['debater']}: {turn['argument'][:100]}..." for turn in debate_history])

        prompt = (
            f"{self.system_prompt}\n"
            f"You have observed a debate on the topic: '{topic}'.\n"
            f"Here is a summary of the arguments:\n{history_summary}\n\n"
            f"Based on the entire debate, please provide an overall assessment. Consider which debater presented stronger arguments, "
            f"better addressed counter-arguments, used evidence more effectively, and showed improvement based on feedback. "
            f"Your answer should just contain the winner's name based on above details. Do not include anything else."
        )

        # Call LLM for final judgement
        final_judgement = call_llm_api(prompt, self.model_name)
        print(f"{self.name} provided final judgement.")
        return final_judgement
