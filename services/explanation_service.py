import os
from config import Config

def generate_rule_based_explanation(metrics, risk_level, risk_prob, predicted_marks, increasing_factors, reducing_factors):
    """
    Generate a detailed rule-based plain-language explanation of risk factors.
    Used as primary logic or fallback when GenAI is unavailable.
    """
    # 1. Structure basic explanation overview
    attendance = metrics.get('attendance_percentage', 0.0)
    avg_assess = metrics.get('avg_assessment_score', 0.0)
    sub_rate = metrics.get('assignment_submission_rate', 1.0) * 100
    gpa = metrics.get('previous_gpa', 0.0)
    
    explanation_intro = (
        f"The prediction indicates a **{risk_level}** risk profile with an academic risk probability of "
        f"**{risk_prob * 100:.1f}%** and an expected final grade of **{predicted_marks:.1f}/100**."
    )
    
    # 2. Detail core concerns
    concerns = []
    if attendance < 75:
        concerns.append(
            f"The student's attendance is currently at **{attendance:.1f}%**, which falls below the institutional minimum threshold "
            f"of 75%. This is a significant factor in reduced class engagement and performance."
        )
    if avg_assess < 50:
        concerns.append(
            f"Continuous internal assessments average **{avg_assess:.1f}/100**, demonstrating difficulty in mastering class modules "
            f"and requiring early academic review."
        )
    if sub_rate < 80:
        concerns.append(
            f"The student has completed only **{sub_rate:.1f}%** of coursework assignments. Unsubmitted assessments are negatively "
            f"impacting their current performance trend."
        )
    if metrics.get('consecutive_absences', 0) >= 4:
        concerns.append(
            f"A pattern of consecutive absences (**{metrics['consecutive_absences']} days** in a row) has been identified, "
            f"which often marks a critical disconnect from the course schedule."
        )
        
    if not concerns:
        concerns.append(
            "The student displays steady base metrics. The minor risks identified relate to general coursework load and standard "
            "assessment variations."
        )
        
    concerns_text = " ".join(concerns)
    
    # 3. Formulate positive factors
    strengths = []
    if attendance >= 85:
        strengths.append("regular and consistent class attendance")
    if sub_rate >= 95:
        strengths.append("an exceptional assignment completion record")
    if avg_assess >= 70:
        strengths.append("strong assessment scores indicating topic mastery")
    if gpa >= 3.0:
        strengths.append("a solid prior academic history")
    if metrics.get('lms_engagement_score', 0) >= 70:
        strengths.append("active engagement with resources on the LMS platform")
        
    if strengths:
        strengths_text = f"This risk is mitigated by the student's strengths, including: {', '.join(strengths)}."
    else:
        strengths_text = "There are currently no outstanding metrics to mitigate the identified risk factors."
        
    # Combine sections
    full_explanation = (
        f"{explanation_intro}\n\n"
        f"### Key Observations\n"
        f"{concerns_text}\n\n"
        f"### Academic Mitigations\n"
        f"{strengths_text}\n\n"
        f"**Responsible AI Disclaimer:** *This explanation is generated to assist educator overview and support planning. "
        f"It is a statistical projection based on current performance and must not be used as the sole basis for student grading, "
        f"disciplinary decisions, or course registration changes.*"
    )
    
    return full_explanation

def generate_genai_explanation(metrics, risk_level, risk_prob, predicted_marks, increasing_factors, reducing_factors):
    """
    Attempt to generate an enriched natural language summary using the Gemini GenAI API.
    Falls back to rule-based explanation if the key is missing or fails.
    """
    api_key = Config.GEMINI_API_KEY
    if not api_key:
        # Fall back silently to rule-based
        return generate_rule_based_explanation(metrics, risk_level, risk_prob, predicted_marks, increasing_factors, reducing_factors)
        
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Build strict prompt for Gemini model
        prompt = f"""
You are an expert AI academic advisor helping educators understand student performance risk predictions.
Generate a concise, professional explanation and action summary for the educator based on the following verified student metrics.

STUDENT PROFILE DATA:
- Risk Category: {risk_level}
- Risk Probability: {risk_prob * 100:.1f}%
- Predicted Final Marks: {predicted_marks:.1f}/100
- Class Attendance Rate: {metrics.get('attendance_percentage', 0.0):.1f}%
- Assignment Submission Rate: {metrics.get('assignment_submission_rate', 1.0)*100:.1f}%
- Average Assessment Marks: {metrics.get('avg_assessment_score', 0.0):.1f}/100
- Cumulative Prior GPA: {metrics.get('previous_gpa', 0.0):.2f}
- LMS Platform Login Frequency: {metrics.get('login_frequency', 0)} times/week
- High Risk Factors: {', '.join(increasing_factors)}
- Protective/Strong Factors: {', '.join(reducing_factors)}

OUTPUT STRUCTURE REQUIREMENTS:
1. Explain the prediction and the primary factors contributing to it in clear, plain language (use bullet points if helpful).
2. Suggest 2-3 specific, constructive academic intervention actions (tutoring, study planning, etc.).
3. End with this exact disclaimer: "Responsible AI Disclaimer: This prediction is intended to support educators and must not be used as the sole basis for academic, disciplinary, or administrative decisions."

SAFETY CONSTRAINTS:
- Do NOT invent personal student details, names, gender, or health conditions.
- Do NOT use protected traits (age, gender, background).
- Frame predictions as probability trends, not certain outcomes.
- Keep comments strictly professional, encouraging early support.
"""
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=500
            )
        )
        
        if response.text:
            return response.text.strip()
        else:
            raise ValueError("Empty response from GenAI")
            
    except Exception as e:
        print(f"GenAI Explanation generation failed ({e}). Falling back to rule-based explanation.")
        return generate_rule_based_explanation(metrics, risk_level, risk_prob, predicted_marks, increasing_factors, reducing_factors)
