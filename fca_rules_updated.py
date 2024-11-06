fca_handbook_full_names = [
    "Financial Services and Markets Act (FSMA)",
    "FCA Consumer Credit sourcebook (CONC)",
    "FCA Principles for Businesses (PRIN)",
    "FCA Conduct of Business Sourcebook (COBS)",
    "Financial promotions on social media"
] # used for user interface only

fca_handbook_list = ["FSMA", "FCA CONC", "FCA PRIN", "FCA COBS", "Financial promotions on social media"]

Clear_Fair_and_Not_Misleading = {
    'rule_name': "Clear, Fair, and Not Misleading",
    'handbooks': [fca_handbook_list[1], fca_handbook_list[2], fca_handbook_list[3], fca_handbook_list[4]],
    'rule_text': "The video's content must be presented clearly, fairly, and in a way that doesn't mislead viewers. This applies to the overall message, the presentation of risks and benefits, and any claims or statements made."
}

Transparent_and_Fair_Terms_and_Comparisons = {
    'rule_name': "Transparent and Fair Terms and Comparisons",
    'handbooks': [fca_handbook_list[1], fca_handbook_list[3]],
    'rule_text': "The video content must use terms like 'guaranteed,' 'protected,' or 'secure' only if they are fully backed by clear, accurate information, with any risks clearly highlighted. For products with complex fees or payments, provide enough detail to ensure viewers understand the costs. Comparisons with other products should be fair, balanced, and easy to understand."
}

Disclosure_of_Risks_for_Credit_and_BNPL_Offers = {
    'rule_name': "Disclosure of Risks for Credit and BNPL Offers",
    'handbooks': [fca_handbook_list[1], fca_handbook_list[3]],
    'rule_text': "In case of video content promoting 'Buy Now, Pay Later' (BNPL) or credit offers, any risks must be clearly disclosed. This includes interest rates after promotions, conditions where interest may apply, and potential impacts on credit ratings. For debt solutions, explain any possible increase in the total payable amount, changes in repayment terms, or credit rating effects."
}

Risk_Warnings = {
    'rule_name': "Risk Warnings",
    'handbooks': [fca_handbook_list[1], fca_handbook_list[3], fca_handbook_list[4]],
    'rule_text': "The video must include clear and prominent risk warnings, especially if it features high-cost short-term credit (HCSTC) products or high-risk investments (HRIs). These warnings should be easily visible and understandable, not hidden in captions or supplementary text."
}

Consumer_Understanding = {
    'rule_name': "Consumer Understanding",
    'handbooks': [fca_handbook_list[2], fca_handbook_list[4]],
    'rule_text': "The video should be designed to be easily understood by its target audience. It should avoid using jargon or complex language, particularly when targeting retail clients. The information should be presented in a way that avoids confusion and empowers viewers to make informed decisions."
}

Avoidance_of_High_Pressure_Selling = {
    'rule_name': "Avoidance of High-Pressure Selling",
    'handbooks': [fca_handbook_list[1]],
    'rule_text': "The video should not employ high-pressure tactics or create an undue sense of urgency. Viewers should be given adequate time to consider their options without feeling pressured or manipulated."
}

rules_list = [Clear_Fair_and_Not_Misleading, Transparent_and_Fair_Terms_and_Comparisons, Disclosure_of_Risks_for_Credit_and_BNPL_Offers, Risk_Warnings, Consumer_Understanding, Avoidance_of_High_Pressure_Selling]
