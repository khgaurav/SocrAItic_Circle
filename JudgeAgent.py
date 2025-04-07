from typing import Any, Dict, List
from llm_helper import call_llm_api
ANALYSIS_LAYERS = [
    {
        "focus": "Evidence Analysis",
        "prompt_template": "Analyze the following argument for claims made without sufficient evidence: '{argument}'. For each unsubstantiated claim, explain what type of evidence would strengthen it."
    },
    {
        "focus": "Logical Flow",
        "prompt_template": "Trace the logical steps in this argument: '{argument}'. Identify any gaps, logical fallacies, or jumps in reasoning."
    },
    {
        "focus": "Assumption Check",
        "prompt_template": "What unstated assumptions must be true for this argument to work: '{argument}'? Which of these assumptions might be questionable?"
    },
    {
        "focus": "Rhetorical Strength",
        "prompt_template": "Evaluate the rhetorical strength and persuasiveness of this argument: '{argument}'. Are there any weaknesses in its delivery or structure?"
    },
]
class JudgeAgent:
    """Represents an AI agent (or interface for a human) evaluating the debate."""

    def __init__(self, name: str = "AI Judge", model_name: str = "gpt-4-turbo", use_strategic_layers: bool = True):
        """
        Initializes the Judge Agent.

        Args:
            name (str): Name of the judge.
            model_name (str): LLM model used by the judge.
            use_strategic_layers (bool): Whether to use the defined ANALYSIS_LAYERS for evaluation.
        """
        self.name = name
        self.model_name = model_name
        self.use_strategic_layers = use_strategic_layers
        self.system_prompt = (
            "You are an impartial judge evaluating a debate. "
            "Focus on logical consistency, evidence, rhetorical strength, and factual accuracy. "
            "Provide constructive feedback to help the debaters improve."
        )
        self.context = [{"role": "system", "content": self.system_prompt}]
        print(f"Initialized Judge: {self.name} (Model: {self.model_name})")

    def evaluate_argument(self, argument: str, debater_name: str, topic: str, round_num: int) -> str:
        """
        Evaluates a single argument using the LLM or predefined rules.

        Args:
            argument (str): The argument text to evaluate.
            debater_name (str): The name of the debater who made the argument.
            topic (str): The debate topic.
            round_num (int): The current round number.

        Returns:
            str: Constructive feedback for the debater.
        """
        print(f"{self.name} evaluating argument from {debater_name}...")

        if self.use_strategic_layers:
            # Use multiple prompts for focused analysis
            full_feedback = f"Feedback for {debater_name} on Round {round_num} (Topic: {topic}):\nArgument:\n'''{argument}'''\n\nAnalysis:\n"
            for layer in ANALYSIS_LAYERS:
                layer_prompt = layer["prompt_template"].format(argument=argument)
                # Add context about the debate topic and round if needed
                full_layer_prompt = f"{self.system_prompt}\nDebate Topic: {topic}\nRound: {round_num}\nDebater: {debater_name}\n{layer_prompt}"

                # Call LLM for each layer's analysis
                layer_analysis = call_llm_api(full_layer_prompt, self.model_name) # Context management might be needed here too
                full_feedback += f"\n--- {layer['focus']} ---\n{layer_analysis}\n"
            feedback = full_feedback

        else:
            # Simpler, single-prompt evaluation
            prompt = (
                f"{self.system_prompt}\n"
                f"Debate Topic: {topic}\nRound: {round_num}\n"
                f"Evaluate the following argument from {debater_name}:\n"
                f"'''{argument}'''\n"
                f"Provide specific, constructive feedback focusing on logic, evidence, and rhetoric."
            )
            feedback = call_llm_api(prompt, self.model_name) # Context management might be needed

        print(f"{self.name} generated feedback for {debater_name}.")
        # In a real system, you might parse this feedback, calculate scores, etc.
        return feedback

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
            f"better addressed counter-arguments, used evidence more effectively, and showed improvement based on feedback (if applicable). "
            f"You can declare a winner or provide a nuanced summary of performance."
        )

        # Call LLM for final judgement
        final_judgement = call_llm_api(prompt, self.model_name)
        print(f"{self.name} provided final judgement.")
        return final_judgement
