import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class EnhancedCareerGuidanceBot:
    def __init__(self):
        # Initialize model and tokenizer
        self.model_name = "microsoft/DialoGPT-small"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        
        # Load and process the dataset
        self.df = pd.read_csv('truncated_career_recommender_dataset.csv')
        self.process_dataset()
        
        # Initialize vectorizer for skill matching
        self.skill_vectorizer = TfidfVectorizer(stop_words='english')
        self.create_skill_vectors()

    def process_dataset(self):
        """Process the dataset to extract unique career paths and their requirements"""
        # Create a mapping of specializations to common career paths
        self.career_mapping = {}
        for _, row in self.df.iterrows():
            spec = row['UG Specialization']
            career = row['Career Path']
            if spec not in self.career_mapping:
                self.career_mapping[spec] = set()
            self.career_mapping[spec].add(career)
            
        # Convert sets to lists for easier handling
        self.career_mapping = {k: list(v) for k, v in self.career_mapping.items()}
        
        # Extract skills for each career path
        self.career_skills = {}
        for _, row in self.df.iterrows():
            career = row['Career Path']
            if career not in self.career_skills:
                self.career_skills[career] = set()
            if pd.notna(row['Skills']):
                skills = row['Skills'].split(';')
                self.career_skills[career].update(skills)
        
        # Convert sets to lists
        self.career_skills = {k: list(v) for k, v in self.career_skills.items()}

    def create_skill_vectors(self):
        """Create TF-IDF vectors for skill matching"""
        # Combine all skills for each career into single strings
        career_skill_docs = {career: ' '.join(skills) for career, skills in self.career_skills.items()}
        self.skill_vectors = self.skill_vectorizer.fit_transform(career_skill_docs.values())
        self.career_list = list(career_skill_docs.keys())

    def get_skill_recommendations(self, user_skills):
        """Get career recommendations based on skill similarity"""
        if not user_skills:
            return []
        
        # Convert user skills to TF-IDF vector
        user_skill_text = ' '.join(user_skills)
        user_vector = self.skill_vectorizer.transform([user_skill_text])
        
        # Calculate similarity with all careers
        similarities = cosine_similarity(user_vector, self.skill_vectors).flatten()
        
        # Get top matching careers
        career_scores = list(zip(self.career_list, similarities))
        return sorted(career_scores, key=lambda x: x[1], reverse=True)

    def get_response(self, user_input, context):
        # Combine context and user input
        full_input = f"{context}\n{user_input}" if context else user_input
        
        # Tokenize and generate response
        inputs = self.tokenizer.encode(full_input, return_tensors="pt")
        outputs = self.model.generate(
            inputs,
            max_length=150,
            num_return_sequences=1,
            pad_token_id=self.tokenizer.eos_token_id
        )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response

    def start_guidance(self):
        user_data = {}
        
        print("Bot: Hello! I'm your enhanced career guidance assistant. What's your name?")
        user_data['name'] = input("You: ")
        
        print(f"\nBot: Hi {user_data['name']}! What's your educational qualification?")
        print("Available qualifications from our dataset:")

        # Normalize case and remove duplicates
        qualifications = set(self.df['Undergraduate Course'].str.strip().str.upper())

        # Display the options
        for i, qual in enumerate(qualifications, 1):
            print(f"{i}. {qual}")

        user_data['education'] = input("You: ")


        
        print("\nBot: What's your specialization?")
        print("Available specializations from our dataset:")
        specializations = self.df['UG Specialization'].unique()
        for spec in specializations:
            print(f"- {spec}")
        user_data['specialization'] = input("You: ")
        
        print("\nBot: What skills do you have? (Enter comma-separated skills)")
        user_data['skills'] = [skill.strip() for skill in input("You: ").split(',')]
        
        print("\nBot: What's your academic score (percentage)?")
        user_data['score'] = float(input("You: "))
        
        # Generate recommendations
        recommendations = self.generate_recommendations(user_data)
        return recommendations

    def generate_recommendations(self, user_data):
        recommendations = []
        
        # Get career recommendations based on specialization
        spec_careers = self.career_mapping.get(user_data['specialization'], [])
        
        # Get career recommendations based on skills
        skill_based_careers = self.get_skill_recommendations(user_data['skills'])
        
        # Combine both types of recommendations
        for career, score in skill_based_careers:
            if score > 0.1:  # Only include careers with some skill match
                # Find similar profiles from the dataset
                similar_profiles = self.df[self.df['Career Path'] == career]
                avg_score = similar_profiles['UG CGPA/Percentage'].mean()
                
                # Get required and recommended skills
                career_required_skills = self.career_skills.get(career, [])
                user_skill_set = set(user_data['skills'])
                missing_skills = [skill for skill in career_required_skills 
                                if skill.lower() not in [s.lower() for s in user_skill_set]]
                
                recommendations.append({
                    "career": career,
                    "match_score": score,
                    "avg_score_required": avg_score,
                    "missing_skills": missing_skills[:5],  # Top 5 missing skills
                    "similar_profiles_count": len(similar_profiles)
                })
        
        return self.format_recommendations(user_data['name'], recommendations)

    def format_recommendations(self, name, recommendations):
        if not recommendations:
            return f"Dear {name}, based on your profile, I couldn't find specific career matches. Consider exploring more skills or different specializations."
        
        response = f"Dear {name}, here are your personalized career recommendations:\n\n"
        for i, rec in enumerate(recommendations[:5], 1):  # Top 5 recommendations
            response += f"{i}. {rec['career']}\n"
            response += f"   Match Score: {rec['match_score']*100:.1f}%\n"
            response += f"   Average Required Score: {rec['avg_score_required']:.1f}%\n"
            if rec['missing_skills']:
                response += f"   Recommended skills to acquire: {', '.join(rec['missing_skills'])}\n"
            response += f"   Similar profiles in our database: {rec['similar_profiles_count']}\n\n"
        
        return response

def main():
    bot = EnhancedCareerGuidanceBot()
    recommendations = bot.start_guidance()
    print("\nBot:", recommendations)

if __name__ == "__main__":
    main()