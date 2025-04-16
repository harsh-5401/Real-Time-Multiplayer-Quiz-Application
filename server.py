import socket
import threading
import json
import time
import random
from typing import Dict, List, Tuple, Optional

class QuizServer:
    def __init__(self, host: str = '127.0.0.1', port: int = 12345):
        """Initialize the quiz server with host, port and necessary data structures."""
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))
        
        # Dictionary to store client information: {address: {'name': str, 'score': int}}
        self.clients: Dict[Tuple[str, int], Dict[str, any]] = {}
        
        # Client response tracking for current question
        self.current_responses: Dict[Tuple[str, int], Optional[str]] = {}
        
        # Lock for thread-safe operations on shared data
        self.lock = threading.Lock()
        
        # Track the current question index
        self.current_question_idx = 0
        
        # Flag to track if a quiz is in progress
        self.quiz_in_progress = False
        
        # Sample questions (in real app, load from file or database)
        self.questions = [
            {
                "question": "What is the capital of France?",
                "options": ["London", "Paris", "Berlin", "Madrid"],
                "correct_answer": "Paris"
            },
            {
                "question": "Which planet is known as the Red Planet?",
                "options": ["Earth", "Mars", "Jupiter", "Venus"],
                "correct_answer": "Mars"
            },
            {
                "question": "What is the largest mammal?",
                "options": ["Elephant", "Giraffe", "Blue Whale", "Gorilla"],
                "correct_answer": "Blue Whale"
            },
            {
                "question": "Who wrote 'Romeo and Juliet'?",
                "options": ["Charles Dickens", "William Shakespeare", "Jane Austen", "Mark Twain"],
                "correct_answer": "William Shakespeare"
            },
            {
                "question": "What is the chemical symbol for gold?",
                "options": ["Go", "Gd", "Au", "Ag"],
                "correct_answer": "Au"
            }
        ]
        
        print(f"Server started on {host}:{port}")
    
    def send_message(self, message: dict, address: Tuple[str, int]) -> None:
        """Send a JSON message to a specific client."""
        try:
            self.socket.sendto(json.dumps(message).encode(), address)
        except Exception as e:
            print(f"Error sending message to {address}: {e}")
    
    def broadcast_message(self, message: dict) -> None:
        """Send a message to all connected clients."""
        for client_address in self.clients:
            self.send_message(message, client_address)
    
    def get_top_players(self, limit: int = 10) -> List[Dict[str, any]]:
        """Return the top N players by score."""
        players = [
            {"name": client_data["name"], "score": client_data["score"]}
            for client_data in self.clients.values()
        ]
        return sorted(players, key=lambda x: x["score"], reverse=True)[:limit]
    
    def handle_client_message(self, message: dict, client_address: Tuple[str, int]) -> None:
        """Process incoming messages from clients."""
        message_type = message.get("type")
        
        if message_type == "join":
            with self.lock:
                name = message.get("name", "Anonymous")
                self.clients[client_address] = {"name": name, "score": 0}
                print(f"New client joined: {name} from {client_address}")
                
                # Acknowledge the join
                self.send_message({
                    "type": "join_ack",
                    "message": f"Welcome {name}! Waiting for quiz to start."
                }, client_address)
                
                # If quiz is in progress, send current question
                if self.quiz_in_progress and self.current_question_idx < len(self.questions):
                    self.send_question_to_client(client_address)
        
        elif message_type == "answer":
            answer = message.get("answer")
            with self.lock:
                if client_address in self.clients and self.quiz_in_progress:
                    self.current_responses[client_address] = answer
                    print(f"Received answer from {self.clients[client_address]['name']}: {answer}")
                    
                    # Check if everyone has answered
                    if all(addr in self.current_responses for addr in self.clients):
                        self.process_answers()
        
        elif message_type == "leave":
            with self.lock:
                if client_address in self.clients:
                    print(f"Client left: {self.clients[client_address]['name']} from {client_address}")
                    del self.clients[client_address]
                    if client_address in self.current_responses:
                        del self.current_responses[client_address]
    
    def send_question_to_client(self, client_address: Tuple[str, int]) -> None:
        """Send the current question to a specific client."""
        if self.current_question_idx < len(self.questions):
            question_data = self.questions[self.current_question_idx]
            self.send_message({
                "type": "question",
                "question_number": self.current_question_idx + 1,
                "total_questions": len(self.questions),
                "question": question_data["question"],
                "options": question_data["options"]
            }, client_address)
    
    def process_answers(self) -> None:
        """Process all client answers for the current question and update scores."""
        current_question = self.questions[self.current_question_idx]
        correct_answer = current_question["correct_answer"]
        
        # Update scores for correct answers
        for client_address, answer in self.current_responses.items():
            if answer == correct_answer and client_address in self.clients:
                self.clients[client_address]["score"] += 1
        
        # Broadcast results
        self.broadcast_message({
            "type": "answer_result",
            "correct_answer": correct_answer,
            "question_number": self.current_question_idx + 1,
            "top_players": self.get_top_players()
        })
        
        # Move to next question or end quiz
        self.current_question_idx += 1
        self.current_responses.clear()
        
        if self.current_question_idx < len(self.questions):
            # Short delay before next question
            time.sleep(3)
            # Send next question to all clients
            for client_address in self.clients:
                self.send_question_to_client(client_address)
        else:
            # End of quiz
            self.quiz_in_progress = False
            self.broadcast_message({
                "type": "quiz_end",
                "message": "Quiz has ended!",
                "final_scores": self.get_top_players(limit=len(self.clients))
            })
            print("Quiz ended!")
    
    def start_quiz(self) -> None:
        """Start the quiz for all connected clients."""
        if not self.clients:
            print("No clients connected. Waiting for players...")
            return
        
        print("Starting quiz...")
        self.quiz_in_progress = True
        self.current_question_idx = 0
        self.current_responses.clear()
        
        # Shuffle questions for variety
        random.shuffle(self.questions)
        
        # Notify all clients
        self.broadcast_message({
            "type": "quiz_start",
            "message": "Quiz is starting!",
            "total_questions": len(self.questions)
        })
        
        # Short delay before first question
        time.sleep(2)
        
        # Send first question to all clients
        for client_address in self.clients:
            self.send_question_to_client(client_address)
    
    def receive_messages(self) -> None:
        """Listen for incoming messages from clients."""
        while True:
            try:
                data, address = self.socket.recvfrom(4096)
                message = json.loads(data.decode())
                
                # Handle the message in a separate thread
                threading.Thread(target=self.handle_client_message, args=(message, address)).start()
            except json.JSONDecodeError:
                print(f"Received invalid JSON from {address}")
            except Exception as e:
                print(f"Error receiving message: {e}")
    
    def run(self) -> None:
        """Run the server, start listening for messages and handle admin commands."""
        # Start thread to listen for messages
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        # Simple admin interface
        while True:
            command = input("Server command (start/status/exit): ").strip().lower()
            
            if command == "start":
                if not self.quiz_in_progress:
                    self.start_quiz()
                else:
                    print("Quiz is already in progress")
            elif command == "status":
                with self.lock:
                    print(f"Connected clients: {len(self.clients)}")
                    for addr, client_data in self.clients.items():
                        print(f"  - {client_data['name']} (Score: {client_data['score']})")
                    print(f"Quiz in progress: {self.quiz_in_progress}")
                    if self.quiz_in_progress:
                        print(f"Current question: {self.current_question_idx + 1}/{len(self.questions)}")
            elif command == "exit":
                print("Shutting down server...")
                self.broadcast_message({"type": "server_shutdown"})
                break
            else:
                print("Unknown command")

if __name__ == "__main__":
    server = QuizServer()
    server.run()