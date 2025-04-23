import concurrent.futures
from DebaterAgent import DebaterAgent
from JudgeAgent import JudgeAgent
from llm_helper import call_llm_api

class SelfImprovingDebateOrchestrator:
    """
    Manages the flow of debate between agents with a self-improvement cycle.
    Each debater gets feedback on their argument and a chance to improve it before the next round.
    """

    def __init__(self, debater_a: DebaterAgent, debater_b: DebaterAgent, judge: JudgeAgent, topic: str, max_workers_round1: int = 2):
        """
        Initializes the orchestrator.

        Args:
            debater_a (DebaterAgent): The first debater.
            debater_b (DebaterAgent): The second debater.
            judge (JudgeAgent): The judge.
            topic (str): The topic of the debate.
            max_workers_round1 (int): Max workers for parallel argument generation in round 1.
        """
        self.debater_a = debater_a
        self.debater_b = debater_b
        self.judge = judge
        self.topic = topic
        self.debate_history = [] # Stores dicts: {"round": int, "debater": str, "argument": str, "feedback": str, "improved_argument": str}
        self.max_workers_round1 = max_workers_round1 # Typically 2 for two debaters
        print(f"\n--- Starting Self-Improving Debate on Topic: {self.topic} ---")
        print(f"Debater A: {self.debater_a.name} ({self.debater_a.stance})")
        print(f"Debater B: {self.debater_b.name} ({self.debater_b.stance})")
        print(f"Judge: {self.judge.name}")
        print(f"Process: Generate argument → Receive feedback → Improve argument → Evaluate improvement → Proceed to next round")

    def _generate_argument_task(self, debater: DebaterAgent, opponent_argument: str = None, feedback: str = None) -> tuple[str, str]:
        """Helper function to wrap argument generation for parallel execution."""
        try:
            argument = debater.generate_argument(self.topic, opponent_argument, feedback)
            return debater.name, argument
        except Exception as e:
            print(f"Error generating argument for {debater.name}: {e}")
            return debater.name, f"Error generating argument: {e}"

    def _improve_argument(self, debater: DebaterAgent, original_argument: str, feedback: str) -> str:
        """
        Ask the debater to improve their argument based on feedback.
        
        Args:
            debater (DebaterAgent): The debater to improve the argument
            original_argument (str): The original argument
            feedback (str): The feedback from the judge
            
        Returns:
            str: The improved argument
        """
        prompt = f"""
You previously made the following argument:
'''{original_argument}'''

You received this feedback:
'''{feedback}'''

Please improve your argument based on the feedback. Focus on strengthening your reasoning, 
addressing weaknesses identified in the feedback, and maintaining a clear structure.
Your improved argument must still be 520 words or less.

Provide only the improved argument.
"""
        # Call the LLM to improve the argument
        improved_argument = call_llm_api(prompt, debater.model_name, 
                                       [{"role": "system", "content": debater.system_prompt}])
        
        print(f"{debater.name} improved their argument based on feedback.")
        return improved_argument

    def run_debate(self, num_rounds: int = 3):
        """
        Executes the debate for a specified number of rounds with self-improvement.
        
        Args:
            num_rounds (int): The number of rounds for the debate.
        """
        argument_a = None
        argument_b = None
        improved_argument_a = None
        improved_argument_b = None
        feedback_a = None
        feedback_b = None

        for i in range(1, num_rounds + 1):
            print(f"\n--- Round {i} ---")

            # --- Round 1: Parallel Argument Generation ---
            if i == 1:
                print("\nGenerating opening arguments in parallel...")
                round1_args = {}
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers_round1) as executor:
                    # Submit tasks for both debaters
                    future_a = executor.submit(self._generate_argument_task, self.debater_a)
                    future_b = executor.submit(self._generate_argument_task, self.debater_b)

                    # Collect results as they complete
                    for future in concurrent.futures.as_completed([future_a, future_b]):
                        debater_name, argument = future.result()
                        round1_args[debater_name] = argument
                        print(f"Opening argument generated for: {debater_name}")

                argument_a = round1_args.get(self.debater_a.name, "Error: Failed to generate argument A")
                argument_b = round1_args.get(self.debater_b.name, "Error: Failed to generate argument B")

                # --- Debater A Cycle: Generate → Feedback → Improve → Evaluate Improvement ---
                print(f"\n{self.debater_a.name}'s Opening Argument:\n{argument_a}")
                feedback_a_text, scores_a = self.judge.evaluate_argument(argument_a, self.debater_a.name, self.topic, i)
                print(f"Feedback from {self.judge.name} for {self.debater_a.name}:\n{feedback_a_text}")
                print(f"Scores for {self.debater_a.name}'s original argument: {scores_a}")
                
                print(f"\n{self.debater_a.name} is improving their argument based on feedback...")
                improved_argument_a = self._improve_argument(self.debater_a, argument_a, feedback_a_text)
                print(f"{self.debater_a.name}'s Improved Argument:\n{improved_argument_a}")
                
                # Evaluate the improved argument
                print(f"\nEvaluating {self.debater_a.name}'s improved argument...")
                improved_feedback_a, improved_scores_a = self.judge.evaluate_argument(
                    improved_argument_a, self.debater_a.name, self.topic, i
                )
                print(f"Scores for {self.debater_a.name}'s improved argument: {improved_scores_a}")
                
                # Record the cycle in history with improved scores
                self.debate_history.append({
                    "round": i,
                    "debater": self.debater_a.name,
                    "original_argument": argument_a,
                    "feedback": feedback_a_text,
                    "scores": scores_a,
                    "improved_argument": improved_argument_a,
                    "improved_scores": improved_scores_a
                })
                feedback_a = feedback_a_text
                
                # --- Debater B Cycle: Generate → Feedback → Improve → Evaluate Improvement ---
                print(f"\n{self.debater_b.name}'s Opening Argument:\n{argument_b}")
                feedback_b_text, scores_b = self.judge.evaluate_argument(argument_b, self.debater_b.name, self.topic, i)
                print(f"Feedback from {self.judge.name} for {self.debater_b.name}:\n{feedback_b_text}")
                print(f"Scores for {self.debater_b.name}'s original argument: {scores_b}")
                
                print(f"\n{self.debater_b.name} is improving their argument based on feedback...")
                improved_argument_b = self._improve_argument(self.debater_b, argument_b, feedback_b_text)
                print(f"{self.debater_b.name}'s Improved Argument:\n{improved_argument_b}")
                
                # Evaluate the improved argument
                print(f"\nEvaluating {self.debater_b.name}'s improved argument...")
                improved_feedback_b, improved_scores_b = self.judge.evaluate_argument(
                    improved_argument_b, self.debater_b.name, self.topic, i
                )
                print(f"Scores for {self.debater_b.name}'s improved argument: {improved_scores_b}")
                
                # Record the cycle in history with improved scores
                self.debate_history.append({
                    "round": i,
                    "debater": self.debater_b.name,
                    "original_argument": argument_b,
                    "feedback": feedback_b_text,
                    "scores": scores_b,
                    "improved_argument": improved_argument_b,
                    "improved_scores": improved_scores_b
                })
                feedback_b = feedback_b_text

            # --- Rounds 2+: Sequential Argument Generation with Improvement ---
            else:
                # Debater A's turn - using B's previous improved argument as context
                print(f"\n{self.debater_a.name}'s Turn:")
                argument_a = self.debater_a.generate_argument(self.topic, improved_argument_b, feedback_a)
                print(f"Argument: {argument_a}")
                
                feedback_a_text, scores_a = self.judge.evaluate_argument(argument_a, self.debater_a.name, self.topic, i)
                print(f"Feedback from {self.judge.name} for {self.debater_a.name}:\n{feedback_a_text}")
                print(f"Scores for {self.debater_a.name}'s original argument: {scores_a}")
                
                print(f"\n{self.debater_a.name} is improving their argument based on feedback...")
                improved_argument_a = self._improve_argument(self.debater_a, argument_a, feedback_a_text)
                print(f"{self.debater_a.name}'s Improved Argument:\n{improved_argument_a}")
                
                # Evaluate the improved argument
                print(f"\nEvaluating {self.debater_a.name}'s improved argument...")
                improved_feedback_a, improved_scores_a = self.judge.evaluate_argument(
                    improved_argument_a, self.debater_a.name, self.topic, i
                )
                print(f"Scores for {self.debater_a.name}'s improved argument: {improved_scores_a}")
                
                # Record the cycle in history with improved scores
                self.debate_history.append({
                    "round": i,
                    "debater": self.debater_a.name,
                    "original_argument": argument_a,
                    "feedback": feedback_a_text,
                    "scores": scores_a,
                    "improved_argument": improved_argument_a,
                    "improved_scores": improved_scores_a
                })
                feedback_a = feedback_a_text

                # Debater B's turn - using A's current improved argument as context
                print(f"\n{self.debater_b.name}'s Turn:")
                argument_b = self.debater_b.generate_argument(self.topic, improved_argument_a, feedback_b)
                print(f"Argument: {argument_b}")
                
                feedback_b_text, scores_b = self.judge.evaluate_argument(argument_b, self.debater_b.name, self.topic, i)
                print(f"Feedback from {self.judge.name} for {self.debater_b.name}:\n{feedback_b_text}")
                print(f"Scores for {self.debater_b.name}'s original argument: {scores_b}")
                
                print(f"\n{self.debater_b.name} is improving their argument based on feedback...")
                improved_argument_b = self._improve_argument(self.debater_b, argument_b, feedback_b_text)
                print(f"{self.debater_b.name}'s Improved Argument:\n{improved_argument_b}")
                
                # Evaluate the improved argument
                print(f"\nEvaluating {self.debater_b.name}'s improved argument...")
                improved_feedback_b, improved_scores_b = self.judge.evaluate_argument(
                    improved_argument_b, self.debater_b.name, self.topic, i
                )
                print(f"Scores for {self.debater_b.name}'s improved argument: {improved_scores_b}")
                
                # Record the cycle in history with improved scores
                self.debate_history.append({
                    "round": i,
                    "debater": self.debater_b.name,
                    "original_argument": argument_b,
                    "feedback": feedback_b_text,
                    "scores": scores_b,
                    "improved_argument": improved_argument_b,
                    "improved_scores": improved_scores_b
                })
                feedback_b = feedback_b_text

        # --- End of Debate ---
        print(f"\n--- Self-Improving Debate Concluded after {num_rounds} Rounds ---")
        
        # Return debate history for analysis
        return self.debate_history
