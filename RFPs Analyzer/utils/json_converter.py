from datetime import datetime
import re

class RFPJsonConverter:
    """
    A class to handle conversion of RFP documents into structured JSON format
    """
    def __init__(self):
        self.section_keywords = {
            'overview': ['overview', 'introduction', 'background', 'purpose', 'scope'],
            'technical': ['technical', 'specifications', 'requirements', 'capabilities'],
            'business': ['business requirements', 'company requirements', 'vendor requirements'],
            'compliance': ['compliance', 'regulations', 'standards', 'certifications'],
            'evaluation': ['evaluation', 'criteria', 'scoring', 'selection'],
            'timeline': ['timeline', 'schedule', 'dates', 'deadlines'],
            'contact': ['contact', 'inquiries', 'questions'],
            'submission': ['submission', 'proposal format', 'response format'],
            'terms': ['terms', 'conditions', 'legal', 'contract']
        }

    def _create_base_structure(self):
        """Create the base JSON structure for RFP data"""
        return {
            "metadata": {
                "processed_date": datetime.now().isoformat(),
                "version": "1.0"
            },
            "sections": {
                "overview": {
                    "description": "",
                    "objectives": []
                },
                "requirements": {
                    "technical": [],
                    "business": [],
                    "compliance": []
                },
                "evaluation_criteria": [],
                "timeline": {
                    "submission_deadline": None,
                    "key_dates": []
                },
                "contact_information": {},
                "submission_requirements": [],
                "terms_and_conditions": [],
                "attachments": []
            }
        }

    def _identify_section(self, line):
        """Identify the section a line belongs to based on keywords"""
        line_lower = line.lower()
        
        for section, keywords in self.section_keywords.items():
            if any(keyword in line_lower for keyword in keywords):
                return section
        
        return None

    def _process_requirement_line(self, line):
        """Process a requirement line into structured format"""
        if ':' in line:
            key, value = line.split(':', 1)
            return {
                'requirement': key.strip(),
                'description': value.strip(),
                'mandatory': any(word in line.lower() for word in ['must', 'shall', 'required', 'mandatory'])
            }
        return None

    def convert_to_json(self, text):
        """
        Convert RFP text into structured JSON format
        Args:
            text: Extracted text from RFP
        Returns:
            dict: Structured RFP data
        """
        rfp_data = self._create_base_structure()
        current_section = None
        section_text = ""
        
        # Process text line by line
        lines = text.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
                
            # Check for section headers
            section = self._identify_section(line)
            if section:
                current_section = section
                i += 1
                continue

            # Process line based on current section
            if current_section == 'overview':
                rfp_data['sections']['overview']['description'] += line + '\n'
                if any(word in line.lower() for word in ['goal', 'objective', 'aim']):
                    rfp_data['sections']['overview']['objectives'].append(line)
                    
            elif current_section == 'technical':
                requirement = self._process_requirement_line(line)
                if requirement:
                    rfp_data['sections']['requirements']['technical'].append(requirement)
                    
            elif current_section == 'business':
                requirement = self._process_requirement_line(line)
                if requirement:
                    rfp_data['sections']['requirements']['business'].append(requirement)
                    
            elif current_section == 'compliance':
                requirement = self._process_requirement_line(line)
                if requirement:
                    rfp_data['sections']['requirements']['compliance'].append(requirement)
                    
            elif current_section == 'evaluation':
                if ':' in line:
                    key, value = line.split(':', 1)
                    rfp_data['sections']['evaluation_criteria'].append({
                        'criterion': key.strip(),
                        'description': value.strip(),
                        'weight': self._extract_weight(value)
                    })
                    
            elif current_section == 'timeline':
                if ':' in line:
                    key, value = line.split(':', 1)
                    if 'deadline' in line.lower() or 'due' in line.lower():
                        rfp_data['sections']['timeline']['submission_deadline'] = value.strip()
                    else:
                        rfp_data['sections']['timeline']['key_dates'].append({
                            'event': key.strip(),
                            'date': value.strip()
                        })
                        
            elif current_section == 'contact':
                if ':' in line:
                    key, value = line.split(':', 1)
                    rfp_data['sections']['contact_information'][key.strip().lower()] = value.strip()
                    
            elif current_section == 'submission':
                if ':' in line:
                    key, value = line.split(':', 1)
                    rfp_data['sections']['submission_requirements'].append({
                        'requirement': key.strip(),
                        'details': value.strip(),
                        'mandatory': any(word in line.lower() for word in ['must', 'shall', 'required', 'mandatory'])
                    })
                    
            elif current_section == 'terms':
                rfp_data['sections']['terms_and_conditions'].append({
                    'item': line,
                    'type': self._identify_term_type(line)
                })
            
            i += 1
        
        # Clean up any empty sections
        rfp_data = self._clean_empty_sections(rfp_data)
        return rfp_data

    def _extract_weight(self, text):
        """Extract evaluation weight/percentage from text"""
        weight_pattern = r'(\d+)%|\((\d+)%\)|(\d+)\s*points?'
        match = re.search(weight_pattern, text)
        if match:
            for group in match.groups():
                if group:
                    return int(group)
        return None

    def _identify_term_type(self, text):
        """Identify the type of terms and conditions item"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['confidential', 'nda', 'disclosure']):
            return 'confidentiality'
        elif any(word in text_lower for word in ['payment', 'invoice', 'cost']):
            return 'payment'
        elif any(word in text_lower for word in ['warranty', 'guarantee']):
            return 'warranty'
        elif any(word in text_lower for word in ['terminate', 'cancellation']):
            return 'termination'
        else:
            return 'general'

    def _clean_empty_sections(self, data):
        """Remove empty sections from the JSON structure"""
        if isinstance(data, dict):
            return {k: self._clean_empty_sections(v) for k, v in data.items() 
                   if v not in (None, "", [], {}, ())}
        elif isinstance(data, list):
            return [self._clean_empty_sections(item) for item in data if item not in (None, "", [], {}, ())]
        return data