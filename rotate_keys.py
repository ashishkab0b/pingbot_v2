import os
from dotenv import dotenv_values, set_key, load_dotenv
from secrets import token_hex

load_dotenv(dotenv_path=".env")

KEY_LENGTH = 32

def rotate_key(root_dirs, fname, key_name, key_length, match_keys):
    """
    Rotate a key in .env files within the specified root directories.

    Parameters:
    - root_dirs: List of root directory paths to search for .env files.
    - key_name: Name of the key to replace in .env files.
    - key_length: Length of the new secret key.
    - match_keys: If true, use the same key in all file. If false, generate a new key for each file.
    """
    if match_keys:
        new_key = token_hex(key_length)
    for root_dir in root_dirs:
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename == fname:
                    env_file_path = os.path.join(dirpath, filename)
                    if not match_keys:
                        new_key = token_hex(key_length)
                    try:
                        # Load the existing .env file
                        env_vars = dotenv_values(env_file_path)

                        if key_name in env_vars:
                            # Update the key in the file
                            set_key(env_file_path, key_name, new_key)
                            print(f"Updated {key_name} in: {env_file_path}. Match keys: {match_keys}")
                        else:
                            print(f"{key_name} not found in: {env_file_path}")
                    except Exception as e:
                        print(f"Error processing {env_file_path}: {e}")


if __name__ == "__main__":
    
    directories_to_search = ["./bot", "./flask_app"]

    rotate_key_names_str = os.getenv("ROTATE_KEY_NAMES")
    rotate_key_names = rotate_key_names_str.split(",") if rotate_key_names_str else []
    
    if not rotate_key_names:
        print("No keys to rotate.")
    
    for key in rotate_key_names:
        rotate_key(root_dirs=directories_to_search, 
                   fname=".env",
                   key_name=key, 
                   key_length=KEY_LENGTH, 
                   match_keys=True)