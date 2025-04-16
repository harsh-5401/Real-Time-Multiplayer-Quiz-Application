import socket
import json
import threading
import sys
import time
from typing import Dict, List, Optional

class QuizClient:
    def __init__(self, server_host: str = '127.0.0.1', server_port: int = 12345):
        """Initialize the quiz client with server connection details."""
        self.server_address = (server_host, server_port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Bind to a random port
        self.socket.bind(('0.0.0.0', 0))
        
        # Timeout for socket operations
        self.socket.settimeout(0.1)
        
        # Client name
        self.name = ""
        
        # Current question data
        self.current_question: Optional[Dict] = None
        
        # Flag to track client state
        self.running = True
        
        print(f"Client initialized, connecting to server at {server_host}:{server_port}")
    
    def send_message(self, message: dict) -> None:
        """Send a JSON message to the server."""
        try:
            self.socket.sendto(json.dumps(message).encode(), self.server_address)
        except Exception as e:
            print(f"Error sending message: {e}")
    
    def join_quiz(self, name: str) -> None:
        """Join the quiz with the given name."""
        self.name = name
        join_message = {
            "type": "join",
            "name": name
        }
        self.send_message(join_message)
        print(f"Joining quiz as {name}...")
    
    def leave_quiz(self) -> None:
        """Leave the quiz properly."""
        if self.name:
            leave_message = {
                "type": "leave",
                "name": self.name
            }
            self.send_message(leave_message)
            print("Leaving quiz...")
    
    def send_answer(self, answer: str) -> None:
        """Send an answer to the current question."""
        if self.current_question:
            answer_message = {
                "type": "answer",
                "answer": answer
            }
            self.send_message(answer_message)
            print(f"Sent answer: {answer}")
        else:
            print("No active question to answer")
    
    def display_question(self, question_data: Dict) -> None:
        """Display a quiz question to the user."""
        self.current_question = question_data
        
        question_num = question_data.get("question_number", 0)
        total = question_data.get("total_questions", 0)
        question = question_data.get("question", "")
        options = question_data.get("options", [])
        
        print("\n" + "="*50)
        print(f"Question {question_num} of {total}")
        print(f"\n{question}\n")
        
        for i, option in enumerate(options):
            print(f"{i+1}. {option}")
        
        print("\nEnter the number or text of your answer:")
    
    def display_results(self, result_data: Dict) -> None:
        """Display question results and leaderboard."""
        correct_answer = result_data.get("correct_answer", "")
        top_players = result_data.get("top_players", [])
        
        print("\n" + "="*50)
        print(f"The correct answer was: {correct_answer}")
        
        print("\nCurrent Leaderboard:")
        for i, player in enumerate(top_players):
            print(f"{i+1}. {player['name']}: {player['score']} points")
        print("="*50)
    
    def display_final_results(self, result_data: Dict) -> None:
        """Display final quiz results."""
        final_scores = result_data.get("final_scores", [])
        
        print("\n" + "="*50)
        print("QUIZ FINISHED - FINAL RESULTS")
        
        print("\nFinal Leaderboard:")
        for i, player in enumerate(final_scores):
            print(f"{i+1}. {player['name']}: {player['score']} points")
        print("="*50)
    
    def handle_server_message(self, message: Dict) -> None:
        """Process messages received from the server."""
        message_type = message.get("type")
        
        if message_type == "join_ack":
            print(message.get("message", "Joined successfully"))
            
        elif message_type == "quiz_start":
            print("\n" + "="*50)
            print("QUIZ IS STARTING!")
            print(f"Total questions: {message.get('total_questions', 0)}")
            print("="*50)
            
        elif message_type == "question":
            self.display_question(message)
            
        elif message_type == "answer_result":
            self.current_question = None
            self.display_results(message)
            
        elif message_type == "quiz_end":
            print(message.get("message", "Quiz has ended!"))
            self.display_final_results(message)
            
        elif message_type == "server_shutdown":
            print("Server is shutting down. Goodbye!")
            self.running = False
    
    def receive_messages(self) -> None:
        """Listen for incoming messages from the server."""
        while self.running:
            try:
                data, _ = self.socket.recvfrom(4096)
                message = json.loads(data.decode())
                self.handle_server_message(message)
            except socket.timeout:
                # This is expected due to the socket timeout we set
                pass
            except json.JSONDecodeError:
                print("Received invalid data from server")
            except Exception as e:
                if self.running:  # Only print errors if still running
                    print(f"Error receiving message: {e}")
    
    def user_input_loop(self) -> None:
        """Handle user input during the quiz."""
        while self.running:
            try:
                if self.current_question:
                    # There's an active question waiting for an answer
                    options = self.current_question.get("options", [])
                    user_input = input().strip()
                    
                    # Check if user entered a number (1, 2, 3, 4) or the full answer
                    if user_input.isdigit() and 1 <= int(user_input) <= len(options):
                        # User entered option number
                        answer = options[int(user_input) - 1]
                        self.send_answer(answer)
                    else:
                        # User entered text answer
                        self.send_answer(user_input)
                else:
                    # No active question, wait a bit to avoid CPU spinning
                    time.sleep(0.1)
            except Exception as e:
                print(f"Error handling input: {e}")
    
    def run(self) -> None:
        """Run the client, connect to server and handle the quiz flow."""
        try:
            # Ask for the player's name
            player_name = input("Enter your name: ").strip()
            if not player_name:
                player_name = "Anonymous"
            
            # Join the quiz
            self.join_quiz(player_name)
            
            # Start a thread to listen for messages from the server
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            # Start a thread to handle user input
            input_thread = threading.Thread(target=self.user_input_loop)
            input_thread.daemon = True
            input_thread.start()
            
            # Main thread waits for termination signal
            while self.running:
                # Check for Ctrl+C or other exit conditions
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nExiting...")
        finally:
            # Clean up when exiting
            self.running = False
            self.leave_quiz()
            self.socket.close()

if __name__ == "__main__":
    # Get server address from command line arguments if provided
    server_host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    server_port = int(sys.argv[2]) if len(sys.argv) > 2 else 12345
    
    client = QuizClient(server_host, server_port)
    client.run()