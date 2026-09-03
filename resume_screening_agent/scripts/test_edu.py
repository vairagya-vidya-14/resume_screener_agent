import re

EDUCATION_PATTERNS = [
    (r'\b(Ph\.?\s*D\.?|Doctorate|Doctor of Philosophy)\b', 'PhD'),
    (r'\b(Master|Masters|Master\'s|M[\s\.]*Tech|M[\s\.]*S|M[\s\.]*E|M[\s\.]*A|M[\s\.]*C[\s\.]*A|MBA|PGDM|Post\s*Graduat\w*)\b', 'Master\'s'),
    (r'\b(Bachelor|Bachelors|Bachelor\'s|B[\s\.]*Tech|B[\s\.]*E|B[\s\.]*S|B[\s\.]*A|B[\s\.]*C[\s\.]*A|B[\s\.]*Com|BTech|BE|BSc|BCA|BCom|Undergraduat\w*)\b', 'Bachelor\'s'),
    (r'\b(Diploma|Associate Degree|A\.?S|A\.?A)\b', 'Diploma / Associate'),
    (r'\b(Intermediate|Class\s*12|12th|Class\s*10|10th|SSC|High\s*School)\b', 'High School / Intermediate')
]

def extract_education(text):
    text_clean = re.sub(r'\s+', ' ', text)
    found = []
    for pattern, degree in EDUCATION_PATTERNS:
        if re.search(pattern, text_clean, re.IGNORECASE):
            if degree not in found:
                found.append(degree)

    higher = [d for d in found if d in ['PhD', 'Master\'s', 'Bachelor\'s']]
    if higher:
        return higher

    if re.search(r'\bEDUCATION\b', text_clean, re.IGNORECASE):
        edu_sec = re.search(r'\bEDUCATION\b(.*?)(?:\bSKILLS\b|\bPROJECTS\b|\bWORK EXPERIENCE\b|\bEXPERIENCE\b|\bCERTIFICATIONS\b|$)', text_clean, re.IGNORECASE | re.DOTALL)
        sec_text = edu_sec.group(1) if edu_sec else text_clean
        if re.search(r'\b(JNTU|JNTUH|College|University|Engineering|CGPA|Percentage|B\.?Tech|BTech|Degree|202\d|201\d)\b', sec_text, re.IGNORECASE):
            return ["Bachelor's"]

    return found if found else ['Not Specified']

tests = [
    'KANDI SHRAVYA +91-8639978043 kandishravya79@gmail.com SUMMARY Computer Science graduate EDUCATION B.Tech Computer Science & Engineering JNTUH Sulthanpur 2022-2026 CGPA:7.97 INTERMEDIATE Narayana junior College 2020-2022 SSC Vidya Vikas High School 2019-2020 CGPA:10.0',
    'B.Tech Computer Science Engineering JNTUH Sulthanpur 2022-2026',
    'B. Tech Computer Science Engineering',
    'JNTUH Sulthanpur 2022-2026 CGPA:7.97 EDUCATION'
]

for t in tests:
    print('Result -->', extract_education(t))
