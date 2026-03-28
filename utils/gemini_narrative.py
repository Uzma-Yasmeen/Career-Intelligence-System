import streamlit as st
from google import genai
from google.genai import types

def generate_career_narrative(role, salary_str, user_country,
                               similarity, missing_skills,
                               selected_skills, years_exp):

    # Load API key
    api_key = (
        st.secrets.get("GEMINI_API_KEY") or
        st.secrets.get("gemini_api_key") or
        ""
    )

    if not api_key or api_key == "YOUR_GEMINI_API_KEY":
        return _fallback(role, salary_str,
                        similarity, missing_skills)

    import time
    
    max_retries = 2
    for attempt in range(max_retries):
        try:
            client = genai.Client(api_key=api_key)

            prompt = f"""
I am a software engineer looking for career insights.
Here is my profile:

- Country: {user_country}
- Predicted Best-Fit Role: {role}
- Estimated Market Salary: {salary_str} 
  (adjusted for {user_country} local market)
- Skill Alignment with Role: {similarity:.1f}%
- Years of Experience: {years_exp}
- Current Skills: {', '.join(selected_skills) if selected_skills else 'None listed'}
- Missing Skills: {', '.join([s[0] for s in missing_skills]) if missing_skills else 'None'}

Write a 3-paragraph personalized career summary:
Paragraph 1: What my profile says about me and my 
current trajectory. Be encouraging but honest.
Paragraph 2: What my salary means for my experience 
level in {user_country} and how I sit in the market.
Paragraph 3: The single most important skill I should 
learn next and why it will make the biggest difference.

Write directly to me as "you".
Keep it under 200 words total.
Be specific — reference the actual numbers and skills.
"""

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                )
            )

            if response and response.text:
                return response.text
            else:
                break # Go to fallback

        except Exception as e:
            error = str(e)
            if "quota" in error.lower() and attempt < max_retries - 1:
                time.sleep(2) # Wait 2 seconds before retry
                continue
            
            if "API_KEY_INVALID" in error:
                return (
                    "❌ Invalid Gemini API key. "
                    "Please check your secrets.toml."
                )
            # For other errors or exhausted retries, return fallback
            break

    return _fallback(role, salary_str, similarity, missing_skills)


def _fallback(role, salary_str, similarity, missing_skills):
    top3 = ', '.join([s[0] for s in missing_skills[:3]]) if missing_skills else 'your current specialized toolkit'
    
    return (
        f"### Profile Analysis & Potential\n"
        f"Based on your current trajectory, you are emerging as a prime candidate for a **{role}** role. "
        f"With a **{similarity:.1f}%** alignment to industry standards, you possess a solid foundation. "
        f"To maximize your impact, pivoting towards **{top3}** will provide the highest return on your learning time.\n\n"
        
        f"### Market Value Insight\n"
        f"The current market benchmark for your profile is estimated at **{salary_str}**. "
        f"This reflects the high demand for your specific combination of experience and technical proficiency. "
        f"Acquiring your identified missing skills could potentially shift you into an even higher compensation bracket.\n\n"
        
        f"### Next Strategic Step\n"
        f"Focus your next 90 days on deep-diving into **{missing_skills[0][0] if missing_skills else 'advanced system architecture'}**. "
        f"Mastering this will not only close a critical gap but will also serve as a signal of senior-level competence to potential employers.\n\n"
        
        f"*(Note: This summary is generated from profile metrics while AI narrative services are undergoing maintenance)*"
    )