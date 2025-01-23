import time
import csv
import os

class CourseRecommendationChatbot:
    def __init__(self, csv_file):
        self.courses = self.load_courses(csv_file)
        self.interest_map = {
            "Science": ["Engineering", "Medical", "Computer Science", "Basic Sciences"],
            "Commerce": ["Accounting", "Business Management", "Economics"],
            "Arts": ["Liberal Arts", "Design", "Law", "Media", "Social Work"],
            "Generic": ["Hospitality", "Event Management", "Digital Skills"]
        }

    def load_courses(self, csv_file):
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file not found: {csv_file}")

        courses = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    courses.append({
                        "stream": row["Stream"],
                        "course": row["Course"],
                        "college": row["College"]
                    })
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return []
        
        return courses

    def print_bot_message(self, message):
        print("\nBot: ", end="")
        for char in message:
            print(char, end="", flush=True)
            time.sleep(0.01)  # Adds a typing effect
        print()

    def get_unique_streams(self):
        return sorted(list(set(course["stream"] for course in self.courses)))

    def get_recommendations(self, stream, interest):
        filtered_courses = [course for course in self.courses if course["stream"] == stream]
        
        if interest == "All Courses":
            return filtered_courses

        keywords = {
            "Engineering": ["B.Tech", "M.Tech", "B.Arch"],
            "Medical": ["MBBS", "BDS", "BAMS", "BHMS"],
            "Computer Science": ["Computer", "IT", "Data Science", "BCA"],
            "Basic Sciences": ["B.Sc."],
            "Accounting": ["B.Com", "CA"],
            "Business Management": ["BBA", "BMS", "Management"],
            "Economics": ["Economics", "Statistics"],
            "Liberal Arts": ["B.A."],
            "Design": ["Design", "Fine Arts"],
            "Law": ["Law", "LLB"],
            "Media": ["Media", "Journalism"],
            "Social Work": ["Social Work", "Education"],
            "Hospitality": ["Hotel"],
            "Event Management": ["Event"],
            "Digital Skills": ["Digital"]
        }

        if interest in keywords:
            return [
                course for course in filtered_courses 
                if any(keyword in course["course"] for keyword in keywords[interest])
            ]
        return filtered_courses

    def run(self):
        self.print_bot_message("Hi! I'm your course recommendation assistant. I can help you find courses and colleges in Ernakulam.")
        
        while True:
            # Get available streams from loaded data
            available_streams = self.get_unique_streams()
            
            # Get stream
            self.print_bot_message(f"What stream interests you? ({'/'.join(available_streams)})")
            stream = input("You: ").strip().capitalize()
            
            if stream not in available_streams:
                self.print_bot_message("Please select a valid stream.")
                continue
            
            # Get interest
            interests = self.interest_map[stream]
            interests.append("All Courses")  # Add "All Courses" option
            self.print_bot_message(f"What specific area interests you within {stream}? Options: {', '.join(interests)}")
            interest = input("You: ").strip()
            
            if interest not in interests:
                self.print_bot_message("Please select a valid interest.")
                continue
            
            # Get and display recommendations
            recommendations = self.get_recommendations(stream, interest)
            
            if recommendations:
                self.print_bot_message("\nBased on your interests, here are my recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    self.print_bot_message(f"\n{i}. {rec['course']}")
                    self.print_bot_message(f"   College: {rec['college']}")
            else:
                self.print_bot_message("I couldn't find any courses matching your criteria.")
            
            # Ask if user wants to continue
            self.print_bot_message("\nWould you like to search for more courses? (yes/no)")
            if input("You: ").strip().lower() != "yes":
                self.print_bot_message("Thank you for using the course recommendation chatbot! Good luck with your studies!")
                break

def main():
    # Specify the path to your CSV file
    csv_file = "All_Streams_Ernakulam_Course_Colleges.csv"
    
    try:
        chatbot = CourseRecommendationChatbot(csv_file)
        chatbot.run()
    except FileNotFoundError:
        print(f"Error: Could not find the CSV file '{csv_file}'")
        print("Please make sure the CSV file is in the same directory as this script.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
