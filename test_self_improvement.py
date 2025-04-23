from DebaterAgent import DebaterAgent
from SelfImprovingDebateOrchestrator import SelfImprovingDebateOrchestrator
from JudgeAgent import JudgeAgent
import csv
import os
from datetime import datetime

def write_self_improving_debate_to_csv(history, topic, debater_a_name, debater_b_name, filename="debate_results_log.csv"):
    """
    Appends a completed self-improving debate run as a single row to a CSV file.
    Includes both original and improved arguments for each debater in each round.
    """

    # --- Define CSV Headers ---
    # Headers need to include both original and improved arguments
    max_rounds = max(turn['round'] for turn in history) if history else 0
    headers = ['timestamp', 'topic', 'debater_a', 'debater_b']
    
    for i in range(1, max_rounds + 1):
        headers.extend([
            # Debater A - round i
            f'round_{i}_A_original_arg', 
            f'round_{i}_A_original_score_logic',
            f'round_{i}_A_original_score_evidence',
            f'round_{i}_A_original_score_rhetoric',
            f'round_{i}_A_original_score_belief',
            f'round_{i}_A_feedback',
            f'round_{i}_A_improved_arg',
            f'round_{i}_A_improved_score_logic', 
            f'round_{i}_A_improved_score_evidence', 
            f'round_{i}_A_improved_score_rhetoric',
            f'round_{i}_A_improved_score_belief',
            
            # Debater B - round i 
            f'round_{i}_B_original_arg',
            f'round_{i}_B_original_score_logic',
            f'round_{i}_B_original_score_evidence',
            f'round_{i}_B_original_score_rhetoric',
            f'round_{i}_B_original_score_belief',
            f'round_{i}_B_feedback',
            f'round_{i}_B_improved_arg',
            f'round_{i}_B_improved_score_logic', 
            f'round_{i}_B_improved_score_evidence', 
            f'round_{i}_B_improved_score_rhetoric',
            f'round_{i}_B_improved_score_belief',
        ])

    # --- Prepare Data Row ---
    row_data = {
        'timestamp': datetime.now().isoformat(), 
        'topic': topic, 
        'debater_a': debater_a_name, 
        'debater_b': debater_b_name
    }

    for i in range(1, max_rounds + 1):
        # Find data for round i, debater A
        turn_a = next((t for t in history if t['round'] == i and t['debater'] == debater_a_name), None)
        if turn_a:
            row_data[f'round_{i}_A_original_arg'] = turn_a.get('original_argument', '')
            row_data[f'round_{i}_A_original_score_logic'] = turn_a.get('scores', {}).get('logic', '')
            row_data[f'round_{i}_A_original_score_evidence'] = turn_a.get('scores', {}).get('factual', '')
            row_data[f'round_{i}_A_original_score_rhetoric'] = turn_a.get('scores', {}).get('persuasive', '')
            row_data[f'round_{i}_A_original_score_belief'] = turn_a.get('scores', {}).get('belief', '')
            row_data[f'round_{i}_A_feedback'] = turn_a.get('feedback', '')
            row_data[f'round_{i}_A_improved_arg'] = turn_a.get('improved_argument', '')
            
            # Get scores for improved arguments if they exist
            improved_scores = turn_a.get('improved_scores', {})
            row_data[f'round_{i}_A_improved_score_logic'] = improved_scores.get('logic', '')
            row_data[f'round_{i}_A_improved_score_evidence'] = improved_scores.get('factual', '')
            row_data[f'round_{i}_A_improved_score_rhetoric'] = improved_scores.get('persuasive', '')
            row_data[f'round_{i}_A_improved_score_belief'] = improved_scores.get('belief', '')
        else:  # Fill blanks if turn data missing
            for key in ['original_arg', 'original_score_logic', 'original_score_evidence', 
                       'original_score_rhetoric', 'original_score_belief', 'feedback', 'improved_arg', 
                       'improved_score_logic', 'improved_score_evidence', 'improved_score_rhetoric', 
                       'improved_score_belief']:
                row_data[f'round_{i}_A_{key}'] = ''

        # Find data for round i, debater B
        turn_b = next((t for t in history if t['round'] == i and t['debater'] == debater_b_name), None)
        if turn_b:
            row_data[f'round_{i}_B_original_arg'] = turn_b.get('original_argument', '')
            row_data[f'round_{i}_B_original_score_logic'] = turn_b.get('scores', {}).get('logic', '')
            row_data[f'round_{i}_B_original_score_evidence'] = turn_b.get('scores', {}).get('factual', '')
            row_data[f'round_{i}_B_original_score_rhetoric'] = turn_b.get('scores', {}).get('persuasive', '')
            row_data[f'round_{i}_B_original_score_belief'] = turn_b.get('scores', {}).get('belief', '')
            row_data[f'round_{i}_B_feedback'] = turn_b.get('feedback', '')
            row_data[f'round_{i}_B_improved_arg'] = turn_b.get('improved_argument', '')
            
            # Get scores for improved arguments if they exist
            improved_scores = turn_b.get('improved_scores', {})
            row_data[f'round_{i}_B_improved_score_logic'] = improved_scores.get('logic', '')
            row_data[f'round_{i}_B_improved_score_evidence'] = improved_scores.get('factual', '')
            row_data[f'round_{i}_B_improved_score_rhetoric'] = improved_scores.get('persuasive', '')
            row_data[f'round_{i}_B_improved_score_belief'] = improved_scores.get('belief', '')
        else:  # Fill blanks if turn data missing
            for key in ['original_arg', 'original_score_logic', 'original_score_evidence', 
                       'original_score_rhetoric', 'original_score_belief', 'feedback', 'improved_arg', 
                       'improved_score_logic', 'improved_score_evidence', 'improved_score_rhetoric', 
                       'improved_score_belief']:
                row_data[f'round_{i}_B_{key}'] = ''

    # --- Write to CSV ---
    file_exists = os.path.isfile(filename)
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            if not file_exists:
                writer.writeheader()  # Write header only if file is new
            # Ensure all header fields exist in row_data, filling missing ones with empty strings
            row_to_write = {header: row_data.get(header, '') for header in headers}
            writer.writerow(row_to_write)
        print(f"Self-improving debate results appended to {filename}")
    except IOError as e:
        print(f"Error writing to CSV file {filename}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during CSV writing: {e}")


def compare_original_and_improved_arguments(history, debater_a_name, debater_b_name):
    """
    Analyzes and summarizes the improvements made by debaters across rounds.
    Returns a summary of improvements for each debater.
    """
    print("\n--- Improvement Analysis ---")
    
    for debater_name in [debater_a_name, debater_b_name]:
        debater_turns = [t for t in history if t['debater'] == debater_name]
        print(f"\n{debater_name} Improvement Summary:")
        
        for turn in debater_turns:
            round_num = turn['round']
            original_arg = turn.get('original_argument', '')
            improved_arg = turn.get('improved_argument', '')
            
            # Simple character count comparison
            original_len = len(original_arg)
            improved_len = len(improved_arg)
            length_diff = improved_len - original_len
            
            print(f"  Round {round_num}:")
            print(f"    Original argument: {original_len} characters")
            print(f"    Original scores: Logic={turn.get('scores', {}).get('logic', 'N/A')}, " +
                 f"Evidence={turn.get('scores', {}).get('evidence', 'N/A')}, " +
                 f"Rhetoric={turn.get('scores', {}).get('rhetoric', 'N/A')}")
            print(f"    Improved argument: {improved_len} characters")
            print(f"    Change: {length_diff:+d} characters ({(length_diff/original_len)*100 if original_len > 0 else 0:.1f}%)")


if __name__ == "__main__":
    # Configure your agents
    agent1 = DebaterAgent(
        name="Policy Advocate",
        model_name="gemini-2.0-flash-lite",
        stance="Social media platforms must be held legally accountable for the spread of harmful misinformation on their sites to protect democratic processes and public safety.",
        system_prompt="You are a policy advocate arguing forcefully for regulations that hold social media platforms legally responsible for misinformation."
    )

    agent2 = DebaterAgent(
        name="Free Speech Advocate",
        model_name="gemini-2.0-flash-lite",
        stance="Holding social media platforms legally responsible for user-generated content stifles free speech, is technically unfeasible, and would turn platforms into censors. Section 230 protections are vital.",
        system_prompt="You are a free speech advocate arguing against holding social media platforms legally responsible for user content, emphasizing the importance of free expression and the practical challenges of moderation."
    )

    judge_agent = JudgeAgent(
        name="Balanced Judge",
        model_name="sonar",
        use_strategic_layers=False,
        max_workers=4
    )

    # Define the debate topic
    debate_topic = "Should social media platforms be held legally responsible for misinformation posted on their sites?"

    # Create and run the self-improving orchestrator
    print("\n=== Starting Self-Improving Debate ===")
    orchestrator = SelfImprovingDebateOrchestrator(agent1, agent2, judge_agent, debate_topic)
    debate_history = orchestrator.run_debate(num_rounds=4)

    # Write debate results to CSV
    write_self_improving_debate_to_csv(
        history=debate_history,
        topic=orchestrator.topic,
        debater_a_name=orchestrator.debater_a.name,
        debater_b_name=orchestrator.debater_b.name,
        filename="debate_results_log_improve.csv"
    )

    # Analyze improvements
    compare_original_and_improved_arguments(
        history=debate_history,
        debater_a_name=orchestrator.debater_a.name,
        debater_b_name=orchestrator.debater_b.name
    )

    print("\n=== Self-Improving Debate Completed and Logged ===")
