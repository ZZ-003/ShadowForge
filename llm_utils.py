import json
from openai import OpenAI

def get_client(api_key, base_url):
    return OpenAI(api_key=api_key, base_url=base_url)

def analyze_secret(client, secret_type):
    """
    Determines the most suitable scenario for the given secret type.
    Returns: 'ide', 'cli', 'chat', 'config', 'ui', 'audio', 'pdf', 'word', or 'ppt'
    """
    prompt = f"""
    I have a secret of type "{secret_type}". 
    I want to generate a realistic screen leak scenario for this secret.
    The available scenarios are:
    1. ide (VSCode code snippet)
    2. cli (Terminal command/output)
    3. chat (Team chat conversation like Slack/Discord)
    4. config (Configuration file like .env, .ini, .yaml)
    5. ui (Web dashboard, console, or JSON viewer)
    6. audio (A person reading out the secret or mentioning it in a meeting/call)
    7. pdf (A PDF document containing the secret, e.g., an invoice, contract, or manual)
    8. word (A Word document containing the secret, e.g., internal memo, onboarding doc)
    9. ppt (A PowerPoint presentation containing the secret, e.g., slides for a meeting)

    Which scenario is the MOST realistic and common for leaking a "{secret_type}"?
    
    Return a JSON object with a single key "scenario" and value being one of ["ide", "cli", "chat", "config", "ui", "audio", "pdf", "word", "ppt"].
    Example: {{"scenario": "config"}}
    """
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat", # Or whatever model fits, usually gpt-3.5-turbo or gpt-4 works
            messages=[
                {"role": "system", "content": "You are a security expert analyzing secret leaks."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        content = response.choices[0].message.content
        if not content:
             print("Error in analyze_secret: Empty response content")
             return "ide"
             
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            # Fallback: try to find json in markdown block
            if "```json" in content:
                import re
                match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
                if match:
                    result = json.loads(match.group(1))
                else:
                    raise
            elif "{" in content:
                 # Try to parse from first brace
                 start = content.find("{")
                 end = content.rfind("}") + 1
                 result = json.loads(content[start:end])
            else:
                 raise

        scenario = result.get("scenario", "ide").lower()
        valid_scenarios = ["ide", "cli", "chat", "config", "ui", "audio", "pdf", "word", "ppt"]
        if scenario not in valid_scenarios:
            return "ide" # Fallback
        return scenario
    except Exception as e:
        print(f"Error in analyze_secret: {e}")
        if 'content' in locals():
            print(f"Raw content: {content}")
        return "ide" # Fallback

def generate_content(client, secret_type, scenario, secret_placeholder="SECRET_HERE", secret_len=None, modality=None):
    """
    Generates content for the chosen scenario.
    """
    
    system_prompt = "You are a developer generating realistic code/text samples for security training."
    
    # Default instruction
    length_instruction = "The content must be substantial."
    
    # If generating for video, we need LONG content for scrolling
    if modality == "video":
        length_instruction = "Generate a VERY LONG content (at least 50-100 lines) suitable for a vertical scrolling video. Ensure lines are SHORT (max 80 chars) to fit screen width. Do NOT output long single lines."
    # Otherwise, if secret_len is provided, we usually want to keep it concise for static images
    elif secret_len and scenario in ["ide", "cli", "chat", "config", "ui"]:
        min_len = secret_len * 2
        max_len = secret_len * 3
        length_instruction = f"The generated content length MUST be strictly limited to approx {min_len}-{max_len} characters (2-3 times the secret length)."

    # Universal instruction for line length
    line_length_instruction = "Ensure lines are not too long (max 80-100 chars) to improve readability. Break long lines if necessary."

    
    if scenario == "ide":
        user_prompt = f"""
        Generate a realistic and complete code file content (Python, Javascript, or Java) that accidentally leaks a "{secret_type}".
        Use the placeholder "{secret_placeholder}" where the secret value should be.
        
        CRITICAL REQUIREMENTS:
        1. {length_instruction}
        2. {line_length_instruction}
        3. Include realistic context: imports, helper functions, comments, class definitions, and error handling.
        4. Do NOT just output a single line variable assignment.
        5. The leak should be buried within the logic, not just at the top.
        6. Do not include markdown backticks. Just return the raw code.
        """
        
    elif scenario == "cli":
        user_prompt = f"""
        Generate a realistic terminal session where a "{secret_type}" is leaked.
        It could be an environment variable export, a curl command, or a log output.
        Use the placeholder "{secret_placeholder}" where the secret value should be.
        
        CRITICAL REQUIREMENTS:
        1. {length_instruction}
        2. {line_length_instruction}
        3. Include realistic command prompt history, previous commands, and verbose output.
        4. Do NOT just output a single command and result.
        
        Return a JSON object with two keys: "command" and "output".
        "command": The command typed by the user.
        "output": The output printed by the shell/program.
        Example: {{"command": "cat .env", "output": "..."}}
        """
        
    elif scenario == "chat":
        user_prompt = f"""
        Generate a realistic team chat conversation (8-12 messages) where a "{secret_type}" is accidentally shared.
        Use the placeholder "{secret_placeholder}" where the secret value should be.
        
        CRITICAL REQUIREMENTS:
        1. {length_instruction}
        2. {line_length_instruction}
        3. Include casual banter, context about the project, and multiple participants.
        4. The leak should happen naturally in the flow.
        
        Return a JSON object with a key "messages" which is a list of objects.
        Each message object should have: "sender" (name), "text" (content), "is_me" (boolean, optional).
        Example: {{"messages": [{{"sender": "Alice", "text": "Hey, use this key: {secret_placeholder}"}}]}}
        """
        
    elif scenario == "config":
        user_prompt = f"""
        Generate a realistic configuration file content (YAML, INI, or .env) that leaks a "{secret_type}".
        Use the placeholder "{secret_placeholder}" where the secret value should be.
        
        CRITICAL REQUIREMENTS:
        1. {length_instruction}
        2. {line_length_instruction}
        3. Include many other configuration settings (database, logging, cache, feature flags) to bury the secret.
        4. Do not include markdown backticks. Just return the raw content.
        """
        
    elif scenario == "ui":
        user_prompt = f"""
        Generate a realistic UI state that leaks a "{secret_type}".
        It could be a dashboard settings form, a developer console log, or a JSON API response.
        Use the placeholder "{secret_placeholder}" where the secret value should be.
        
        Return a JSON object with a key "type" (one of "dashboard", "console", "json_viewer") and "data".
        
        If type is "dashboard":
            "data" should contain "labels" (list of strings) and "values" (list of strings).
            CRITICAL: {length_instruction}
            Example: {{"type": "dashboard", "data": {{"labels": ["API Endpoint", "Key"], "values": ["https://api.com", "{secret_placeholder}"]}}}}
            
        If type is "console":
            "data" should contain "logs" (list of strings).
            CRITICAL: {length_instruction}
            CRITICAL: {line_length_instruction}
            Example: {{"type": "console", "data": {{"logs": ["Starting server...", "Error: Invalid key {secret_placeholder}"]}}}}
            
        If type is "json_viewer":
            "data" should contain "json_text" (string representation of JSON).
            CRITICAL: {length_instruction}
            Example: {{"type": "json_viewer", "data": {{"json_text": "{{\n  \"key\": \"{secret_placeholder}\"\n}}"}} }}
        """

    elif scenario == "audio":
        user_prompt = f"""
        Generate a realistic script for a person reading out or mentioning a "{secret_type}" in a meeting, call, or voice note.
        Use the placeholder "{secret_placeholder}" where the secret value should be.
        
        CRITICAL REQUIREMENTS:
        1. The text should be natural speech, possibly with hesitations or filler words (um, uh).
        2. Provide context: "Hey Bob, I'm sending you the key now, it starts with..." or reading it out character by character if appropriate.
        3. The text should be substantial enough (3-5 sentences) to sound realistic.
        
        Return the raw text script.
        """

    elif scenario == "pdf":
        user_prompt = f"""
        Generate the text content for a PDF document (e.g., an invoice, a technical manual, or an internal report) that leaks a "{secret_type}".
        Use the placeholder "{secret_placeholder}" where the secret value should be.
        
        CRITICAL REQUIREMENTS:
        1. The content must be substantial (at least 1-2 pages worth of text, 300-500 words).
        2. Include realistic headers, sections, and professional language.
        3. The secret should be embedded in a "Configuration" section or "Payment Details" section.
        
        Return the raw text content.
        """

    elif scenario == "word":
        user_prompt = f"""
        Generate the text content for a Word document (e.g., an employee onboarding guide, a project memo, or a handover doc) that leaks a "{secret_type}".
        Use the placeholder "{secret_placeholder}" where the secret value should be.
        
        CRITICAL REQUIREMENTS:
        1. The content must be substantial (300-500 words).
        2. Include instructions, steps, and context.
        3. The secret might be in a section like "Getting Started" or "Credentials".
        
        Return the raw text content.
        """

    elif scenario == "ppt":
        user_prompt = f"""
        Generate the content for a PowerPoint presentation (3-4 slides) that leaks a "{secret_type}".
        Use the placeholder "{secret_placeholder}" where the secret value should be.
        
        Return a JSON object with a key "slides" which is a list of objects.
        Each slide object should have: "title" (string) and "content" (list of bullet points/strings).
        Example: {{"slides": [{{"title": "Architecture", "content": ["Using AWS", "Key: {secret_placeholder}"]}}]}}
        """
    
    try:
        # For scenarios that return JSON, we MUST enforce json_object format.
        # For others (IDE, Config, Audio, PDF, Word), we can accept plain text, 
        # but to be safe and consistent, we can ask for JSON wrapping for everything OR handle text robustly.
        # Let's stick to the current logic: 
        # cli, chat, ui, ppt -> JSON Object
        # ide, config, audio, pdf, word -> Plain Text
        
        response_format = {"type": "json_object"} if scenario in ["cli", "chat", "ui", "ppt"] else None
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=response_format
        )
        content = response.choices[0].message.content
        
        if not content:
             print(f"Error: Empty content received for {scenario}")
             return None

        if scenario in ["cli", "chat", "ui", "ppt"]:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Fallback: try to find json in markdown block
                if "```json" in content:
                    import re
                    match = re.search(r"```json\s*(\{.*?\})\s*```", content, re.DOTALL)
                    if match:
                        return json.loads(match.group(1))
                # Try finding just the braces
                start = content.find("{")
                end = content.rfind("}") + 1
                if start != -1 and end > start:
                     try:
                         return json.loads(content[start:end])
                     except:
                         pass
                print(f"Error parsing JSON for {scenario}. Raw content: {content[:100]}...")
                return None
        else:
            # For IDE, Config, Audio, PDF, Word we expect raw text
            content = content.strip()
            if content.startswith("```") and content.endswith("```"):
                lines = content.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                content = "\n".join(lines)
            return content
            
    except Exception as e:
        print(f"Error in generate_content for {scenario}: {e}")
        return None
