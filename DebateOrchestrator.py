import concurrent.futures
from DebaterAgent import DebaterAgent # Assuming DebaterAgent.py is accessible
from JudgeAgent import JudgeAgent # Assuming JudgeAgent.py is accessible

class DebateOrchestrator:
    """Manages the flow of the debate between agents. Allows parallel generation for Round 1."""

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
        self.debate_history = [] # Stores dicts: {"round": int, "debater": str, "argument": str, "feedback": str}
        self.max_workers_round1 = max_workers_round1 # Typically 2 for two debaters
        print(f"\n--- Starting Debate on Topic: {self.topic} ---")
        print(f"Debater A: {self.debater_a.name} ({self.debater_a.stance})")
        print(f"Debater B: {self.debater_b.name} ({self.debater_b.stance})")
        print(f"Judge: {self.judge.name}")
        print(f"Parallel Argument Generation for Round 1: Enabled (Max Workers: {self.max_workers_round1})")

    def _generate_argument_task(self, debater: DebaterAgent, opponent_argument: str = None, feedback: str = None) -> tuple[str, str]:
        """Helper function to wrap argument generation for parallel execution."""
        try:
            argument = debater.generate_argument(self.topic, opponent_argument, feedback)
            return debater.name, argument
        except Exception as e:
            print(f"Error generating argument for {debater.name}: {e}")
            return debater.name, f"Error generating argument: {e}"

    def run_debate(self, num_rounds: int = 3):
        """
        Executes the debate for a specified number of rounds.
        Round 1 arguments are generated in parallel. Subsequent rounds are sequential.

        Args:
            num_rounds (int): The number of rounds for the debate.
        """
        argument_a = None
        argument_b = None
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

                print(f"\n{self.debater_a.name}'s Opening Argument:\n{argument_a}")
                feedback_a_text, scores_a = self.judge.evaluate_argument(argument_a, self.debater_a.name, self.topic, i)
                print(f"Feedback from {self.judge.name} for {self.debater_a.name}:\n{feedback_a_text}")
                print(f"Scores for {self.debater_a.name}: {scores_a}")
                self.debate_history.append({
                    "round": i,
                    "debater": self.debater_a.name,
                    "argument": argument_a,
                    "feedback": feedback_a_text, # Store text feedback
                    "scores": scores_a # Store scores dictionary
                })
                feedback_a = feedback_a_text

                print(f"\n{self.debater_b.name}'s Opening Argument:\n{argument_b}")
                feedback_b_text, scores_b = self.judge.evaluate_argument(argument_b, self.debater_b.name, self.topic, i)
                print(f"Feedback from {self.judge.name} for {self.debater_b.name}:\n{feedback_b_text}")
                print(f"Scores for {self.debater_b.name}: {scores_b}")
                self.debate_history.append({
                    "round": i,
                    "debater": self.debater_b.name,
                    "argument": argument_b,
                    "feedback": feedback_b_text, # Store text feedback
                    "scores": scores_b # Store scores dictionary
                })
                feedback_b = feedback_b_text

            # --- Rounds 2+: Sequential Argument Generation ---
            else:
                # Debater A's turn
                print(f"\n{self.debater_a.name}'s Turn:")
                # Debater A uses Debater B's *previous* argument and its *own* previous feedback
                argument_a = self.debater_a.generate_argument(self.topic, argument_b, feedback_a)
                print(f"Argument: {argument_a}")
                feedback_a_text, scores_a = self.judge.evaluate_argument(argument_a, self.debater_a.name, self.topic, i)
                print(f"Feedback from {self.judge.name} for {self.debater_a.name}:\n{feedback_a_text}")
                print(f"Scores for {self.debater_a.name}: {scores_a}")
                self.debate_history.append({
                    "round": i,
                    "debater": self.debater_a.name,
                    "argument": argument_a,
                    "feedback": feedback_a_text, # Store text feedback
                    "scores": scores_a # Store scores dictionary
                })
                feedback_a = feedback_a_text
                # Optional: self.debater_a.receive_feedback(feedback_a)

                # Debater B's turn
                print(f"\n{self.debater_b.name}'s Turn:")
                 # Debater B uses Debater A's *current* argument and its *own* previous feedback
                argument_b = self.debater_b.generate_argument(self.topic, argument_a, feedback_b)
                print(f"Argument: {argument_b}")
                feedback_b_text, scores_b = self.judge.evaluate_argument(argument_b, self.debater_b.name, self.topic, i)
                print(f"Feedback from {self.judge.name} for {self.debater_b.name}:\n{feedback_b_text}")
                print(f"Scores for {self.debater_b.name}: {scores_b}")
                self.debate_history.append({
                    "round": i,
                    "debater": self.debater_b.name,
                    "argument": argument_b,
                    "feedback": feedback_b_text, # Store text feedback
                    "scores": scores_b # Store scores dictionary
                })
                feedback_b = feedback_b_text
                # Optional: self.debater_b.receive_feedback(feedback_b)


        # --- End of Debate ---
        print(f"\n--- Debate Concluded after {num_rounds} Rounds ---")

        # Final Judgement
        # final_judgement = self.judge.declare_winner(self.debate_history, self.topic)
        # print("\n--- Final Judgement ---")
        # print(final_judgement)
