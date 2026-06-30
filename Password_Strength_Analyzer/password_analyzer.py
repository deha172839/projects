import re

# List of common passwords
COMMON_PASSWORDS = [
    "123456",
    "password",
    "admin",
    "qwerty",
    "abc123",
    "password123",
    "12345678"
 ]

def analyze_password(password):
    """
    This function analyzes the password and returns:
    - Strength
    - Score
    - Details
    - Suggestions
    """

    score = 0
    details = []
    suggestions = []

    # Check Password Length       
    if len(password) >= 12:
        score += 2
        details.append(" Password length is excellent.")
    elif len(password) >= 8:
        score += 1
        details.append("Password length is acceptable.")
        suggestions.append("Increase password length to at least 12 characters.")
    else:
        details.append(" Password is too short.")
        suggestions.append("Use at least 8 characters.")

    # Uppercase Letter
    if re.search(r"[A-Z]", password):
        score += 1
        details.append(" Contains uppercase letter.")
    else:
        details.append(" No uppercase letter.")
        suggestions.append("Add at least one uppercase letter.")

    # Lowercase Letter
    if re.search(r"[a-z]", password):
        score += 1
        details.append(" Contains lowercase letter.")
    else:
        details.append(" No lowercase letter.")
        suggestions.append("Add at least one lowercase letter.")

    # Number checking
  
    if re.search(r"\d", password):
        score += 1
        details.append(" Contains number.")
    else:
        details.append(" No number.")
        suggestions.append("Add at least one number.")
    # Special Character
    
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
        details.append(" Contains special character.")
    else:
        details.append(" No special character.")
        suggestions.append("Add at least one special character.")

    # Common Password Check
    
    if password.lower() in COMMON_PASSWORDS:
        details.append(" This is a commonly used password.")
        suggestions.append("Choose a unique password.")
        score = max(score - 2, 0)

    
    # Decide Password Strength
   
    if score >= 6:
        strength = "Strong"
    elif score >= 4:
        strength = "Medium"
    else:
        strength = "Weak"

    return {
        "strength": strength,
        "score": score,
        "details": details,
        "suggestions": suggestions
    }