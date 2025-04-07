from DebaterAgent import DebaterAgent
from DebateOrchestrator import DebateOrchestrator
from JudgeAgent import JudgeAgent
if __name__ == "__main__":
    # Configure your agents (replace with desired models and prompts)
    # NOTE: Ensure you have API keys set up in your environment if using real LLMs
    agent1 = DebaterAgent(
        name="Pro-AI Debater",
        model_name="gemini-1.5-flash-8b", # Changed to Gemini model
        stance="Artificial Intelligence is beneficial for society",
        system_prompt="You are an optimistic AI assistant arguing for the benefits of AI."
    )

    agent2 = DebaterAgent(
        name="Cautious Debater",
        model_name="sonar", # Changed to Perplexity model
        stance="Artificial Intelligence poses significant risks to society",
        system_prompt="You are a cautious analyst arguing about the potential risks and downsides of AI."
    )

    judge_agent = JudgeAgent(
        name="Fair AI Judge",
        model_name="gemini-2.0-flash-thinking-exp-01-21", # Changed to Gemini model
        use_strategic_layers=False
    )


    # Define the debate topic
    debate_topic = "The societal impact of widespread Artificial Intelligence adoption."

    # Create and run the orchestrator
    orchestrator = DebateOrchestrator(agent1, agent2, judge_agent, debate_topic)
    orchestrator.run_debate(num_rounds=2) # Run for 2 rounds for a shorter example

    # You can access the history for further analysis
    # print("\nFull Debate History:")
    # for turn in orchestrator.debate_history:
    #     print(f"Round {turn['round']} - {turn['debater']}:\n Argument: {turn['argument']}\n Feedback: {turn['feedback']}\n---")
