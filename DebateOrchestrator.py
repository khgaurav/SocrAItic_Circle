from DebaterAgent import DebaterAgent
from JudgeAgent import JudgeAgent
class DebateOrchestrator:
    """Manages the flow of the debate between agents."""

    def __init__(self, debater_a: DebaterAgent, debater_b: DebaterAgent, judge: JudgeAgent, topic: str):
        """
        Initializes the orchestrator.

        Args:
            debater_a (DebaterAgent): The first debater.
            debater_b (DebaterAgent): The second debater.
            judge (JudgeAgent): The judge.
            topic (str): The topic of the debate.
        """
        self.debater_a = debater_a
        self.debater_b = debater_b
        self.judge = judge
        self.topic = topic
        self.debate_history = [] # Stores tuples of (round, debater_name, argument, feedback)
        print(f"\n--- Starting Debate on Topic: {self.topic} ---")
        print(f"Debater A: {self.debater_a.name} ({self.debater_a.stance})")
        print(f"Debater B: {self.debater_b.name} ({self.debater_b.stance})")
        print(f"Judge: {self.judge.name}")

    def run_debate(self, num_rounds: int = 3):
        """
        Executes the debate for a specified number of rounds.

        Args:
            num_rounds (int): The number of rounds for the debate.
        """
        argument_a = None
        argument_b = None
        feedback_a = None
        feedback_b = None

        for i in range(1, num_rounds + 1):
            print(f"\n--- Round {i} ---")

            # Debater A's turn
            print(f"\n{self.debater_a.name}'s Turn:")
            argument_a = self.debater_a.generate_argument(self.topic, argument_b, feedback_a)
            print(f"Argument: {argument_a}")
            feedback_a = self.judge.evaluate_argument(argument_a, self.debater_a.name, self.topic, i)
            print(f"Feedback from {self.judge.name}: {feedback_a}")
            self.debate_history.append({"round": i, "debater": self.debater_a.name, "argument": argument_a, "feedback": feedback_a})
            # self.debater_a.receive_feedback(feedback_a) # Let agent process feedback

            # Debater B's turn
            print(f"\n{self.debater_b.name}'s Turn:")
            argument_b = self.debater_b.generate_argument(self.topic, argument_a, feedback_b)
            print(f"Argument: {argument_b}")
            feedback_b = self.judge.evaluate_argument(argument_b, self.debater_b.name, self.topic, i)
            print(f"Feedback from {self.judge.name}: {feedback_b}")
            self.debate_history.append({"round": i, "debater": self.debater_b.name, "argument": argument_b, "feedback": feedback_b})
            # self.debater_b.receive_feedback(feedback_b) # Let agent process feedback


        # --- End of Debate ---
        print(f"\n--- Debate Concluded after {num_rounds} Rounds ---")

        # Final Judgement
        final_judgement = self.judge.declare_winner(self.debate_history, self.topic)
        print("\n--- Final Judgement ---")
        print(final_judgement)

        # You could add more complex scoring, analysis, or visualization here.
