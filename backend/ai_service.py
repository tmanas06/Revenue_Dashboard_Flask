import os
from typing import List, Dict, Any
from datetime import datetime
import json
from collections import defaultdict
from dotenv import load_dotenv
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AIRecommendationService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        self.model_name = "microsoft/DialoGPT-medium"
        self.model = None
        self.tokenizer = None
        self.load_model()
    
    def load_model(self):
        """Load the model and tokenizer"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name).to(self.device)
            self.model.eval()
            logger.info("Model loaded successfully")
            
            # Test the model
            test_prompt = "Hello, how are you?"
            test_response = self.generate_text(test_prompt, max_length=50)
            logger.info(f"Test response: {test_response}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
            self.tokenizer = None
    
    def generate_text(self, prompt: str, max_length: int = 200) -> str:
        """Generate text using the local model"""
        if not self.model or not self.tokenizer:
            logger.error("Model or tokenizer not loaded")
            return "Error: Model not loaded"
            
        try:
            logger.info(f"Generating text for prompt: {prompt[:100]}...")
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Add padding token if it exists
            pad_token_id = self.tokenizer.pad_token_id if self.tokenizer.pad_token_id is not None else self.tokenizer.eos_token_id
            
            # Generate with better parameters for business analysis
            outputs = self.model.generate(
                inputs.input_ids,
                max_length=len(inputs.input_ids[0]) + max_length,
                num_return_sequences=1,
                temperature=0.7,
                top_p=0.9,
                top_k=50,
                do_sample=True,
                pad_token_id=pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.2,
                no_repeat_ngram_size=2
            )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Remove the prompt from the response
            response = response[len(prompt):].strip()
            
            # Clean up the response
            response = response.replace("\n\n", "\n").strip()
            if response.startswith("\n"):
                response = response[1:]
            
            logger.info(f"Generated response: {response[:100]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return "Error generating response"
    
    def analyze_revenue_trends(self, revenue_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze revenue trends and generate insights using local model
        """
        try:
            logger.info("Starting revenue trend analysis")
            
            # Prepare data for analysis
            monthly_data = defaultdict(lambda: {'total': 0, 'count': 0, 'categories': defaultdict(float)})
            
            for item in revenue_data:
                date = datetime.strptime(item['date'], '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                monthly_data[month_key]['total'] += item['amount']
                monthly_data[month_key]['count'] += 1
                if item['category']:
                    monthly_data[month_key]['categories'][item['category']] += item['amount']
            
            # Create analysis prompt
            prompt = self._create_analysis_prompt(monthly_data)
            logger.info(f"Analysis prompt created: {prompt[:100]}...")
            
            # Generate analysis using local model
            analysis = self.generate_text(prompt, max_length=500)
            logger.info(f"Analysis generated: {analysis[:100]}...")
            
            # Parse the response
            parsed_analysis = self._parse_analysis(analysis)
            
            # Add growth strategies and potential issues
            growth_strategies = self.generate_text(
                """Based on the following revenue analysis, suggest specific growth strategies:
                """ + analysis,
                max_length=300
            )
            logger.info(f"Growth strategies generated: {growth_strategies[:100]}...")
            
            potential_issues = self.generate_text(
                """Based on the following revenue analysis, identify potential issues and risks:
                """ + analysis,
                max_length=200
            )
            logger.info(f"Potential issues generated: {potential_issues[:100]}...")
            
            return {
                'status': 'success',
                'observations': parsed_analysis.get('observations', ''),
                'price_recommendations': parsed_analysis.get('price_recommendations', ''),
                'product_focus': parsed_analysis.get('product_focus', ''),
                'growth_strategies': growth_strategies,
                'potential_issues': potential_issues
            }
            
        except Exception as e:
            logger.error(f"Error in analyze_revenue_trends: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _create_analysis_prompt(self, monthly_data: dict) -> str:
        """Create a prompt for the AI based on the monthly revenue data"""
        logger.info("Creating analysis prompt")
        
        # Create a more structured and clear prompt
        prompt = """You are a business analyst providing detailed revenue analysis and recommendations.

Revenue Data Analysis:
"""
        
        # Add monthly data
        for month, data in sorted(monthly_data.items()):
            prompt += f"\n{month}:\n"
            prompt += f"  Total Revenue: ${data['total']:,.2f}\n"
            prompt += f"  Transactions: {data['count']}\n"
            if data['categories']:
                prompt += "  Categories:\n"
                for category, amount in data['categories'].items():
                    prompt += f"    {category}: ${amount:,.2f}\n"
        
        # Add clear section headers with specific questions
        prompt += """

Based on this data, please provide:

1. Key Observations:
- What are the main revenue trends?
- Are there any seasonal patterns?
- Which categories are performing well/poorly?

2. Price Recommendations:
- Should prices be adjusted?
- Which products need price changes?
- What is the optimal pricing strategy?

3. Product Focus:
- Which products should we prioritize?
- Are there opportunities for new products?
- How should we position our products?

4. Growth Strategies:
- What are the best growth opportunities?
- How can we increase revenue?
- What new markets should we target?

5. Potential Issues:
- Are there any revenue risks?
- What challenges might we face?
- How can we mitigate risks?

Please provide detailed, actionable recommendations for each section.
"""
        
        logger.info(f"Prompt created with {len(monthly_data)} months of data")
        return prompt
    
    def _parse_analysis(self, analysis: str) -> Dict[str, str]:
        """Parse the AI-generated analysis into structured data"""
        logger.info("Parsing analysis")
        try:
            # Split the analysis into sections
            sections = analysis.split('\n\n')
            result = {}
            
            for section in sections:
                if not section.strip():
                    continue
                
                # Try to find common section headers
                if 'Observations' in section:
                    result['observations'] = section.replace('Observations:', '').strip()
                elif 'Price' in section:
                    result['price_recommendations'] = section.replace('Price:', '').strip()
                elif 'Product' in section:
                    result['product_focus'] = section.replace('Product:', '').strip()
            
            logger.info(f"Parsed analysis sections: {list(result.keys())}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing analysis: {e}")
            return {}
    
    def generate_marketing_ideas(self, business_type: str, target_audience: str) -> Dict[str, Any]:
        """
        Generate marketing ideas based on business type and target audience
        """
        try:
            prompt = f"Generate 5 marketing ideas for a {business_type} business targeting {target_audience}. Include both online and offline strategies."
            ideas = self.generate_text(prompt)
            
            return {
                'status': 'success',
                'marketing_ideas': ideas
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
