import os
import json

def find_distinct_m_behaviors(root_dir):
    """
    Searches a directory and its subdirectories for JSON files,
    opens them, and extracts distinct values for the 'm_behaviors' parameter.

    Args:
        root_dir (str): The root directory to start the search from.

    Returns:
        tuple: A tuple containing:
            - set: A set containing all distinct 'm_behaviors' values found.
            - int: The total number of JSON files processed.
    """
    distinct_behaviors = set()
    processed_files_count = 0

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".json"):
                filepath = os.path.join(dirpath, filename)
                processed_files_count += 1
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "m_behaviors" in data:
                            # m_behaviors can be a single string or a list of strings
                            if isinstance(data["m_behaviors"], list):
                                for behavior in data["m_behaviors"]:
                                    distinct_behaviors.add(behavior)
                            else:
                                distinct_behaviors.add(data["m_behaviors"])
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON from {filepath}")
                except Exception as e:
                    print(f"An error occurred while processing {filepath}: {e}")
    return distinct_behaviors, processed_files_count

if __name__ == "__main__":
    target_directory = r"C:\Wizwad\Deserialized\Deck_Root\Spells"

    if not os.path.isdir(target_directory):
        print(f"Error: The directory '{target_directory}' does not exist.")
    else:
        found_behaviors, num_processed_files = find_distinct_m_behaviors(target_directory)

        print(f"Processed {num_processed_files} JSON files.")

        if found_behaviors:
            print("Distinct 'm_behaviors' found:")
            for behavior in sorted(list(found_behaviors)):
                print(f"- {behavior}")
        else:
            print(f"No 'm_behaviors' found in any JSON file within '{target_directory}'.")