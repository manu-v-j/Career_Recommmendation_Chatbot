from course import CourseRecommendationChatbot
from career_guidence import EnhancedCareerGuidanceBot


class CareerSuggestionBot:
    def __init__(self):
        # Initialize the Enhanced Career Guidance Bot
        self.bot=EnhancedCareerGuidanceBot()

    def run(self):
        # Run the career suggestion logic
        recommendations=self.bot.start_guidance()
        print("\nBot:", recommendations)

class CoursesuggestionBot:
    def __init__(self):
        # Provide the correct path to your CSV file
        csv_file="All_Streams_Ernakulam_Course_Colleges.csv"
        self.bot=CourseRecommendationChatbot(csv_file)

    def run(self):
        # Start the course guidance process
        self.bot.run()



def main():
    print("Welcome to the Career and Course Suggestion System!")
    print("Choose an option:")
    print("1. Career Suggestion")
    print("2. Course Suggestion")

    choice=input("Enter 1 or 2: ").strip()

    if choice=="1":
        career_bot=CareerSuggestionBot()
        career_bot.run()
    elif choice=="2":
        course_bot=CoursesuggestionBot()
        course_bot.run()
    else:
        print("Invalid choice. Please restart the application and choose a valid option.")


if __name__ == "__main__":
    main()