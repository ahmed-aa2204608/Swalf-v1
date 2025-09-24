class TopicClassifier:
    def __init__(self, deployment, model="fanar"):
        self.deployment = deployment
        self.model = model
        
    def classify_topic(self, topic, information=""):
        prompt = f"""Classify this Arabic topic into exactly 3 categories:

Domain: [تقنية/صحة/تعليم/ثقافة/أعمال/عام]
Style: [رسمي/عادي/ودود] 
Sensitivity: [عادي/حساس]

Topic: {topic}
Information: {information}

Return only in this format: Domain|Style|Sensitivity
Example: تقنية|عادي|عادي"""

        try:
            response = self.deployment.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a topic classifier. Return only the requested format."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.choices[0].message.content.strip()
            return self._parse_classification(result)
            
        except Exception as e:
            print(f"Classification error: {e}")
            return self._get_default_classification()
    
    def _parse_classification(self, result):
        """Parse the LLM result and validate format"""
        try:
            parts = result.split('|')
            if len(parts) == 3:
                domain, style, sensitivity = [part.strip() for part in parts]
                
                # Validate domains
                valid_domains = ['تقنية', 'صحة', 'تعليم', 'ثقافة', 'أعمال', 'عام']
                valid_styles = ['رسمي', 'عادي', 'ودود']
                valid_sensitivity = ['عادي', 'حساس']
                
                if (domain in valid_domains and 
                    style in valid_styles and 
                    sensitivity in valid_sensitivity):
                    
                    return {
                        'domain': domain,
                        'style': style,
                        'sensitivity': sensitivity,
                        'raw_output': result
                    }
            
            # If validation fails, try keyword fallback
            return self._keyword_fallback(result)
            
        except Exception:
            return self._get_default_classification()
    
    def _keyword_fallback(self, text):
        """Simple keyword-based classification as backup"""
        domain = 'عام'  # default
        style = 'عادي'   # default
        sensitivity = 'عادي'  # default
        
        # Simple keyword matching for domain
        if any(word in text for word in ['تقنية', 'تكنولوجيا', 'برمجة', 'ذكاء اصطناعي']):
            domain = 'تقنية'
        elif any(word in text for word in ['صحة', 'طب', 'دواء', 'علاج']):
            domain = 'صحة'
        elif any(word in text for word in ['تعليم', 'تعلم', 'دراسة', 'تربية']):
            domain = 'تعليم'
        elif any(word in text for word in ['ثقافة', 'تراث', 'تاريخ', 'أدب']):
            domain = 'ثقافة'
        elif any(word in text for word in ['أعمال', 'اقتصاد', 'تجارة', 'استثمار']):
            domain = 'أعمال'
            
        return {
            'domain': domain,
            'style': style,
            'sensitivity': sensitivity,
            'raw_output': text,
            'fallback_used': True
        }
    
    def _get_default_classification(self):
        """Default safe classification"""
        return {
            'domain': 'عام',
            'style': 'عادي', 
            'sensitivity': 'عادي',
            'raw_output': 'default',
            'fallback_used': True
        }


#Take it from the API init file
def classify_topic(topic, information="", deployment=None):
    classifier = TopicClassifier(deployment, "Fanar-C-1-8.7B")
    classification = classifier.classify_topic(topic, information)
    return classification

# Usage example:
# classifier = TopicClassifier(deployment, "fanar")
# result = classifier.classify_topic("الذكاء الاصطناعي في التعليم", "تأثير التكنولوجيا على طرق التدريس")
# print(result)
# Output: {'domain': 'تقنية', 'style': 'عادي', 'sensitivity': 'عادي', 'raw_output': 'تقنية|عادي|عادي'}