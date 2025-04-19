# 🎮 Real-Time Multiplayer Quiz Game 🎮

## 🌟 Overview

A fast-paced, real-time multiplayer quiz application built with Python's UDP socket programming. Challenge your friends with trivia questions and compete to see who's the ultimate quiz master!

## ✨ Features

- 🚀 **Real-time multiplayer** gameplay
- 🧠 **Multiple-choice questions** across various topics
- 📊 **Live leaderboard** to track scores and rankings
- 👥 **Unlimited players** can join simultaneously
- 🔄 **Synchronized quiz flow** - everyone answers the same questions together
- 🎛️ **Simple server controls** to manage game sessions

## 📋 Requirements

- Python 3.7+
- Basic understanding of terminal/command prompt
- Local network connection (for multi-device play)

## 🚀 Quick Start Guide

### Installation

1. Clone this repository or download the source code:
   ```bash
   https://github.com/harsh-5401/Real-Time-Multiplayer-Quiz-Application.git
   cd multiplayer-quiz-game
   ```

No additional dependencies required - just standard Python libraries!

### Running the Game

#### Step 1: Start the Server
```bash
python quiz_server.py
```
You'll see a message confirming the server is running, like:
```
Server started on 127.0.0.1:12345
Server command (start/status/exit):
```

#### Step 2: Start the Client(s)
Open a new terminal window for each player and run:
```bash
python quiz_client.py
```
For each client, enter a player name when prompted:
```
Enter your name: [Your Name]
```

#### Step 3: Start the Quiz
In the server terminal, type `start` to begin the quiz:
```
Server command (start/status/exit): start
```

## 🎮 Playing with Friends

### Playing on the Same Computer
- Follow the steps above, with multiple terminal windows for each player
- Each player uses a different name when joining

### Playing on Different Computers (Same Network)

#### On the Host Computer:
1. Find your local IP address:
   - Windows: Open Command Prompt and type `ipconfig`
   - macOS/Linux: Open Terminal and type `ifconfig` or `ip addr`
2. Start the server:
   ```bash
   python quiz_server.py
   ```

#### On Player Computers:
1. Run the client with the host's IP address:
   ```bash
   python quiz_client.py [host_ip_address]
   ```
   For example:
   ```bash
   python quiz_client.py 192.168.1.5
   ```
2. Enter your name when prompted and wait for the host to start the game

### Playing Over the Internet
To play over the internet, you'll need to:
1. Configure port forwarding on your router (port 12345)
2. Use your public IP address instead of local IP
3. Modify the server to bind to 0.0.0.0 instead of 127.0.0.1

## 🎯 How to Play

1. **Join the Game**: Start a client and enter your name
2. **Wait for the Quiz**: The server admin will start the quiz when all players have joined
3. **Answer Questions**: For each question:
   - Read the question and options carefully
   - Type the number (1-4) or the full text of your answer
4. **Check the Leaderboard**: After each question, see the current standings
5. **Final Results**: At the end of the quiz, final rankings will be displayed

## 🛠️ Server Commands

The server admin can use these commands:
- `start`: Begin a new quiz session
- `status`: Check connected players and current game status
- `exit`: Shut down the server

## 🎨 Customizing the Quiz

To add your own questions:
1. Open `quiz_server.py` in a text editor
2. Locate the `self.questions` list in the `__init__` method
3. Add new question dictionaries following this format:
   ```python
   {
       "question": "Your question text here?",
       "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
       "correct_answer": "Option 2"
   }
   ```

## 🐛 Troubleshooting

- **Connection Issues**: Make sure the server is running before starting clients
- **Address Already in Use**: Change the port number in both server and client
- **Firewall Problems**: Allow Python through your firewall or antivirus
- **Display Issues**: Resize your terminal window if text doesn't display properly

## 📝 License

This project is open source and available under the MIT License.

## 🙌 Have Fun!

Gather your friends, test your knowledge, and may the smartest player win!   
