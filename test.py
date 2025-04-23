from DebaterAgent import DebaterAgent
from DebateOrchestrator import DebateOrchestrator
from SelfImprovingDebateOrchestrator import SelfImprovingDebateOrchestrator
from JudgeAgent import JudgeAgent
import csv
import os
from datetime import datetime

def write_debate_to_csv(history, topic, debater_a_name, debater_b_name, final_judgement, final_scores, filename="debate_log.csv"):
    """Appends a completed debate run as a single row to a CSV file."""

    # --- Define CSV Headers ---
    # Adjust headers based on the number of rounds and desired scores
    max_rounds = max(turn['round'] for turn in history) if history else 0
    headers = ['timestamp', 'topic', 'debater_a', 'debater_b']
    for i in range(1, max_rounds + 1):
        headers.extend([
            f'round_{i}_A_arg', f'round_{i}_A_feedback',
            f'round_{i}_A_score_logic', f'round_{i}_A_score_evidence', f'round_{i}_A_score_rhetoric', f'round_{i}_A_score_belief', # Add more scores if needed
            f'round_{i}_B_arg', f'round_{i}_B_feedback',
            f'round_{i}_B_score_logic', f'round_{i}_B_score_evidence', f'round_{i}_B_score_rhetoric', f'round_{i}_B_score_belief', # Add more scores if needed
        ])
    headers.extend(['final_judgement', 'final_score_A', 'final_score_B']) # Adjust final score headers as needed

    # --- Prepare Data Row ---
    row_data = {'timestamp': datetime.now().isoformat(), 'topic': topic, 'debater_a': debater_a_name, 'debater_b': debater_b_name}

    for i in range(1, max_rounds + 1):
        # Find data for round i, debater A
        turn_a = next((t for t in history if t['round'] == i and t['debater'] == debater_a_name), None)
        if turn_a:
            row_data[f'round_{i}_A_arg'] = turn_a.get('argument', '')
            row_data[f'round_{i}_A_feedback'] = turn_a.get('feedback', '')
            row_data[f'round_{i}_A_score_logic'] = turn_a.get('scores', {}).get('logic', '')
            row_data[f'round_{i}_A_score_evidence'] = turn_a.get('scores', {}).get('factual', '')  # Updated to match JudgeAgent scores
            row_data[f'round_{i}_A_score_rhetoric'] = turn_a.get('scores', {}).get('persuasive', '') # Updated to match JudgeAgent scores
            row_data[f'round_{i}_A_score_belief'] = turn_a.get('scores', {}).get('belief', '') # Updated to match JudgeAgent scores
        else: # Fill blanks if turn data missing
             for key in ['arg', 'feedback', 'score_logic', 'score_evidence', 'score_rhetoric']:
                 row_data[f'round_{i}_A_{key}'] = ''


        # Find data for round i, debater B
        turn_b = next((t for t in history if t['round'] == i and t['debater'] == debater_b_name), None)
        if turn_b:
            row_data[f'round_{i}_B_arg'] = turn_b.get('argument', '')
            row_data[f'round_{i}_B_feedback'] = turn_b.get('feedback', '')
            row_data[f'round_{i}_B_score_logic'] = turn_b.get('scores', {}).get('logic', '')
            row_data[f'round_{i}_B_score_evidence'] = turn_b.get('scores', {}).get('factual', '')  # Updated to match JudgeAgent scores
            row_data[f'round_{i}_B_score_rhetoric'] = turn_b.get('scores', {}).get('persuasive', '') # Updated to match JudgeAgent scores
            row_data[f'round_{i}_B_score_belief'] = turn_a.get('scores', {}).get('belief', '') # Updated to match JudgeAgent scores
        else: # Fill blanks if turn data missing
             for key in ['arg', 'feedback', 'score_logic', 'score_evidence', 'score_rhetoric']:
                 row_data[f'round_{i}_B_{key}'] = ''

    # # Add final judgement and scores
    # row_data['final_judgement'] = final_judgement
    # # Adapt how final scores are stored based on how declare_winner returns them
    # row_data['final_score_A'] = final_scores.get(debater_a_name, '') if isinstance(final_scores, dict) else ''
    # row_data['final_score_B'] = final_scores.get(debater_b_name, '') if isinstance(final_scores, dict) else ''

    # --- Write to CSV ---
    file_exists = os.path.isfile(filename)
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            if not file_exists:
                writer.writeheader() # Write header only if file is new
            # Ensure all header fields exist in row_data, filling missing ones with empty strings
            row_to_write = {header: row_data.get(header, '') for header in headers}
            writer.writerow(row_to_write)
        print(f"Debate results appended to {filename}")
    except IOError as e:
        print(f"Error writing to CSV file {filename}: {e}")
    except Exception as e:
         print(f"An unexpected error occurred during CSV writing: {e}")

if __name__ == "__main__":
    # Configure your agents (replace with desired models and prompts)
    # NOTE: Ensure you have API keys set up in your environment if using real LLMs
    agent1 = DebaterAgent(
        name="STEM Funding Advocate",
        model_name="gemini-2.0-flash-lite",
        stance="Increased funding for STEM (Science, Technology, Engineering, Mathematics) education and research is crucial for societal progress and economic growth.",
        system_prompt="You are a passionate advocate arguing for the critical importance of prioritizing funding for STEM fields."
    )

    agent2 = DebaterAgent(
        name="Arts & Psychology Funding Advocate",
        model_name="gemini-2.0-flash-lite",
        stance="Funding for the Arts and Psychology is essential for a well-rounded society, fostering creativity, critical thinking, and mental well-being, and should not be overshadowed by STEM.",
        system_prompt="You are a thoughtful proponent arguing for the vital role and necessary funding of Arts and Psychology disciplines."
    )

    judge_agent = JudgeAgent(
        name="Balanced Funding Judge",
        model_name="sonar",
        use_strategic_layers=False,
        max_workers=4
    )

    # Define the debate topic
    debate_topic = "Prioritizing government funding: Should STEM fields receive significantly more resources than Arts and Psychology?"

    # Create and run the orchestrator
    orchestrator = DebateOrchestrator(agent1, agent2, judge_agent, debate_topic)
    debate_history = orchestrator.run_debate(num_rounds=4)

    # Get the final judgment after the debate
    # print("\n--- Getting Final Judgment ---")
    # final_judgment_text = judge_agent.declare_winner(orchestrator.debate_history, orchestrator.topic)
    # print(f"\n--- Final Judgment ---\n{final_judgment_text}")
    
    # Calculate final scores based on average scores from each round
    final_scores = {}
    debater_a_scores = []
    debater_b_scores = []
    
    for turn in orchestrator.debate_history:
        if turn['debater'] == orchestrator.debater_a.name:
            if 'scores' in turn and turn['scores']:
                # Calculate average of all score metrics
                avg_score = sum(turn['scores'].values()) / len(turn['scores']) if turn['scores'] else 0
                debater_a_scores.append(avg_score)
        elif turn['debater'] == orchestrator.debater_b.name:
            if 'scores' in turn and turn['scores']:
                # Calculate average of all score metrics
                avg_score = sum(turn['scores'].values()) / len(turn['scores']) if turn['scores'] else 0
                debater_b_scores.append(avg_score)
    
    # Calculate average score across all rounds
    # final_scores[orchestrator.debater_a.name] = sum(debater_a_scores) / len(debater_a_scores) if debater_a_scores else 0
    # final_scores[orchestrator.debater_b.name] = sum(debater_b_scores) / len(debater_b_scores) if debater_b_scores else 0
    
    # print(f"\n--- Final Scores ---")
    # print(f"{orchestrator.debater_a.name}: {final_scores[orchestrator.debater_a.name]:.2f}")
    # print(f"{orchestrator.debater_b.name}: {final_scores[orchestrator.debater_b.name]:.2f}")

    # Write debate results to CSV
    write_debate_to_csv(
        history=orchestrator.debate_history,
        topic=orchestrator.topic,
        debater_a_name=orchestrator.debater_a.name,
        debater_b_name=orchestrator.debater_b.name,
        final_judgement="",
        final_scores=final_scores,
        filename="debate_results_log.csv"
    )

    print("\nDebate results have been saved to debate_results_log.csv")
