# Task 6: Multi-Client Chat Server (TCP)

## Overview
A real-time multi-client chat system where multiple users can connect simultaneously, broadcast messages to everyone, and send private messages to specific users.

## Features Implemented

### Core Requirements ✓
1. **Multiple Clients Support**
   - Multiple clients can connect simultaneously
   - Each connection handled in a separate thread
   - Thread-safe operations on shared data structures

2. **Message Broadcasting**
   - Messages from any client broadcast to all other connected clients
   - Real-time message delivery
   - Timestamp for all messages

3. **Server State Management**
   - **Client list**: Dictionary mapping usernames to connections
   - **Usernames**: Unique username for each client (validation on join)
   - **Join/Leave notifications**: System messages when users join or leave

4. **Private Messaging**
   - Command: `/pm <username> <message>`
   - Direct message to specific user
   - Sender receives confirmation
   - Error handling for invalid usernames

### Additional Features ✓
5. **Chat Commands**
   - `/pm <username> <message>` - Send private message
   - `/list` - Show all online users
   - `/help` - Display available commands
   - `/quit` - Leave the chat gracefully

6. **User Experience**
   - Welcome message on join
   - Online user list displayed on join
   - Formatted timestamps for all messages
   - Clean message formatting
   - Username validation (no duplicates, no spaces, no empty)

## File Structure
```
task6/
├── server.py       # Chat server
├── client.py       # Chat client
└── README.md       # This file
```

## How to Run

### 1. Start the Server
```bash
python server.py
```
Output:
```
============================================================
              MULTI-CLIENT CHAT SERVER
============================================================
Server IP: 192.168.x.x
Port: 5173
Status: Listening for connections...
============================================================
```

### 2. Run Multiple Clients
Open multiple terminals and run:
```bash
python client.py
```

Enter a username when prompted (must be unique).

### 3. Start Chatting!
- Type messages to broadcast to everyone
- Use `/pm Alice Hello!` to send private message to Alice
- Use `/list` to see who's online
- Use `/quit` to leave the chat

## Example Usage

### Scenario: Three Users Chatting

**User Alice:**
```
Enter your username: Alice
Connecting to server at 192.168.1.100:5173...
✓ Connected successfully!

==================================================
Welcome to the chat server, Alice!
Type '/help' for commands
==================================================

==================================================
Online Users (1): Alice
==================================================

[14:30:15] [SYSTEM] Bob has joined the chat

==================================================
Online Users (2): Alice, Bob
==================================================

You: Hello Bob!

[14:30:30] Bob: Hi Alice! How are you?

[14:30:45] [SYSTEM] Charlie has joined the chat

You: /pm Bob This is a private message

[14:31:00] [PM to Bob] This is a private message

[14:31:10] [PM from Bob] Got your message, thanks!
```

**User Bob:**
```
Enter your username: Bob
Connecting to server at 192.168.1.100:5173...
✓ Connected successfully!

==================================================
Welcome to the chat server, Bob!
Type '/help' for commands
==================================================

==================================================
Online Users (2): Alice, Bob
==================================================

[14:30:18] Alice: Hello Bob!

You: Hi Alice! How are you?

[14:30:45] [SYSTEM] Charlie has joined the chat

[14:31:00] [PM from Alice] This is a private message

You: /pm Alice Got your message, thanks!

[14:31:10] [PM to Alice] Got your message, thanks!
```

**User Charlie:**
```
Enter your username: Charlie
Connecting to server at 192.168.1.100:5173...
✓ Connected successfully!

==================================================
Welcome to the chat server, Charlie!
Type '/help' for commands
==================================================

==================================================
Online Users (3): Alice, Bob, Charlie
==================================================

You: Hi everyone!

[14:32:00] Alice: Welcome Charlie!

[14:32:05] Bob: Hey Charlie!

You: /list

==================================================
Online Users (3): Alice, Bob, Charlie
==================================================
```

### Server Console:
```
============================================================
              MULTI-CLIENT CHAT SERVER
============================================================
Server IP: 192.168.1.100
Port: 5173
Status: Listening for connections...
============================================================

[INFO] New connection attempt from ('192.168.1.101', 54321)
[14:30:10] [JOIN] Alice joined from ('192.168.1.101', 54321)
[INFO] Active clients: 1

[INFO] New connection attempt from ('192.168.1.102', 54322)
[14:30:15] [JOIN] Bob joined from ('192.168.1.102', 54322)
[INFO] Active clients: 2

[14:30:18] [BROADCAST] Alice: Hello Bob!
[14:30:30] [BROADCAST] Bob: Hi Alice! How are you?

[INFO] New connection attempt from ('192.168.1.103', 54323)
[14:30:45] [JOIN] Charlie joined from ('192.168.1.103', 54323)
[INFO] Active clients: 3

[14:31:00] [PM] Alice -> Bob: This is a private message
[14:31:10] [PM] Bob -> Alice: Got your message, thanks!

[14:32:00] [BROADCAST] Charlie: Hi everyone!
[14:32:00] [BROADCAST] Alice: Welcome Charlie!
[14:32:05] [BROADCAST] Bob: Hey Charlie!

[14:35:00] [LEAVE] Bob left the chat
[INFO] Active clients: 2
```

## Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/pm <user> <msg>` | Send private message | `/pm Alice Hello there!` |
| `/list` | Show online users | `/list` |
| `/help` | Show commands | `/help` |
| `/quit` | Leave chat | `/quit` |
| Regular text | Broadcast to all | `Hello everyone!` |

## Technical Implementation

### Server Architecture

**Data Structures:**
```python
clients = {}  # {username: (conn, addr)}
clients_lock = threading.Lock()  # Thread-safe access
```

**Key Functions:**
- `broadcast_message()` - Send to all clients (with exclusion option)
- `send_private_message()` - Direct message between two users
- `send_client_list()` - Send online users list
- `handle_client()` - Per-client thread handler
- `remove_client()` - Clean disconnect handling

**Thread Safety:**
- All access to `clients` dictionary protected by `clients_lock`
- Prevents race conditions in multi-threaded environment
- Safe concurrent add/remove operations

### Client Architecture

**Threading Model:**
- **Main thread**: Handles user input and sending messages
- **Receive thread**: Continuously listens for server messages
- Daemon thread ensures clean exit

**Key Functions:**
- `receive_messages()` - Listen for incoming messages
- `send_messages()` - Handle user input and sending
- Input/output synchronized for clean terminal display

### Message Protocol

**Username Exchange:**
1. Client connects
2. Client sends username
3. Server validates (unique, non-empty, no spaces)
4. Server confirms or rejects

**Message Format:**
- `[HH:MM:SS] username: message` - Regular broadcast
- `[HH:MM:SS] [PM from user] message` - Private message received
- `[HH:MM:SS] [PM to user] message` - Private message sent confirmation
- `[HH:MM:SS] [SYSTEM] notification` - System messages

**Error Handling:**
- Connection loss detection
- Invalid username handling
- User not found for PMs
- Graceful disconnect

## Advanced Features

### Username Validation
```python
- Cannot be empty
- Cannot contain spaces
- Cannot start with '/'
- Must be unique across all connected clients
```

### Connection Management
- Automatic cleanup on disconnect
- Broadcast leave notifications
- Thread-safe removal from client list
- Connection timeout handling

### Private Messaging
- Recipient validation before sending
- Confirmation to sender
- Error messages for invalid recipients
- Logged on server console

### System Messages
- Join notifications to all users
- Leave notifications to all users  
- Server shutdown notification
- Error messages for failed operations

## Testing Scenarios

1. **Basic Chat**
   - Start server
   - Connect 2-3 clients
   - Send messages
   - Verify broadcast to all

2. **Private Messages**
   - Send PMs between users
   - Verify only recipient receives
   - Test invalid usernames

3. **User Management**
   - Try duplicate username (should reject)
   - Users join/leave dynamically
   - Check `/list` updates correctly

4. **Edge Cases**
   - Client disconnects abruptly
   - Network interruption
   - Empty messages
   - Very long messages

5. **Commands**
   - Test all commands: `/pm`, `/list`, `/help`, `/quit`
   - Invalid command formats
   - PM to offline user

## Configuration

Modify these constants in both files:
```python
PORT = 5173              # Server port
BUFFER_SIZE = 2048       # Message buffer size
```

## Error Handling

✓ **Connection errors**: Graceful handling and cleanup  
✓ **Invalid username**: Rejection with error message  
✓ **Duplicate username**: Connection refused  
✓ **Network issues**: Automatic disconnect and notification  
✓ **Invalid commands**: Error messages with usage info  
✓ **PM to offline user**: Error message to sender  

## Key Advantages

✓ **Real-time Communication**: Instant message delivery  
✓ **Scalable**: Handles multiple concurrent users  
✓ **Thread-safe**: No race conditions or data corruption  
✓ **User-friendly**: Clear commands and formatting  
✓ **Robust**: Comprehensive error handling  
✓ **Private Messaging**: Secure 1-on-1 communication  
✓ **State Management**: Accurate client tracking  
✓ **Clean Exit**: Proper cleanup and notifications  
