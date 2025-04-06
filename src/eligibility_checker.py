import re

def extract_company_data(company_data_text):
    lines = company_data_text.strip().split('\n')
    data = {}
    for i in range(0, len(lines) - 1, 2):
        key, value = lines[i].strip(), lines[i+1].strip()
        if key and value and key.lower() not in ["field", "data"]:
            data[key] = value
    return data

def check_eligibility(company_data, rfp_text):
    status = {}

    # Experience
    match = re.search(r"minimum\s+(\d+)\s+years\s+of\s+experience\s+in\s+temporary\s+staffing", rfp_text, re.I)
    if match:
        required = int(match.group(1))
        company_exp = int(company_data.get("Years of Experience in Temporary Staffing", "0").split()[0])
        status["Minimum Years of Experience in Temporary Staffing"] = company_exp >= required
    else:
        status["Minimum Years of Experience in Temporary Staffing"] = "Not mentioned"

    status["Attendance at Pre-Proposal Conference"] = "Mandatory - Attendance data not available"
    status["DUNS Number Provided"] = company_data.get("DUNS Number") is not None
    status["CAGE Code Provided"] = company_data.get("CAGE Code") is not None
    status["SAM.gov Registration"] = company_data.get("SAM.gov Registration Date") is not None
    status["NAICS Codes include Temporary Help (561320)"] = "561320" in company_data.get("NAICS Codes", "")

    return status
