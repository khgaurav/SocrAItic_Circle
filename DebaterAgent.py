from llm_helper import call_llm_api
class DebaterAgent:
    """Represents an AI agent participating in the debate."""

    def __init__(self, name: str, model_name: str, stance: str, system_prompt: str):
        """
        Initializes the Debater Agent.

        Args:
            name (str): The name of the agent (e.g., "Debater A").
            model_name (str): The LLM model this agent uses.
            stance (str): The initial stance or side the agent takes in the debate.
            system_prompt (str): A base instruction defining the agent's role and persona.
        """
        self.name = name
        self.model_name = model_name
        self.stance = stance
        self.system_prompt = system_prompt
        self.context = [{"role": "system", "content": system_prompt + f" You are arguing for the '{stance}' stance."}]
        print(f"Initialized Debater: {self.name} (Model: {self.model_name}, Stance: {self.stance})")

    def generate_argument(self, topic: str, opponent_argument: str = None, feedback: str = None) -> str:
        """
        Generates the next argument based on the topic, opponent's last point, and judge feedback.

        Args:
            topic (str): The main topic of the debate.
            opponent_argument (str, optional): The previous argument from the opponent. Defaults to None.
            feedback (str, optional): Feedback received from the judge on the last argument. Defaults to None.

        Returns:
            str: The newly generated argument.
        """
        prompt = f"Debate Topic: {topic}\nYour Stance: {self.stance}\n"
        prompt += f"Your role: {self.system_prompt}\n"

        if opponent_argument:
            prompt += f"Your opponent ({'Other Debater'}) just argued:\n'''{opponent_argument}'''\n"
            prompt += "Please formulate your counter-argument or rebuttal.\n"
        else:
            prompt += "Please present your opening argument.\n"

        if feedback:
            prompt += f"\nFeedback on your previous argument:\n'''{feedback}'''\nPlease incorporate this feedback into your response.\n"
        prompt += "\nVery important: Your argument must be 520 words or less (approximately 4 minutes of speaking time at 130 words per minute). You will be penalised if you go over this limit."
        prompt += "\nGenerate your argument:"

        # Add current prompt to context before calling LLM
        self.context.append({"role": "user", "content": prompt})

        # Call the LLM API
        argument = call_llm_api(prompt, self.model_name, self.context[:-1]) # Pass context *before* this turn's prompt

        # Add LLM response to context
        self.context.append({"role": "assistant", "content": argument})

        # Optional: Context window management (e.g., limit history size)
        if len(self.context) > 10: self.context = self.context[-10:]

        print(f"{self.name} generated argument.")
        return argument

    def receive_feedback(self, feedback: str):
        """Stores feedback for the next turn."""
        # Feedback can be added to context or handled separately
        print(f"{self.name} received feedback.")
        # Example: Add feedback explicitly to context for the next turn's prompt
        self.context.append({"role": "system", "content": f"Feedback received: {feedback}"})
