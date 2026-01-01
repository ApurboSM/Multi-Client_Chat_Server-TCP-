import socket
import threading
from datetime import datetime

PORT = 5173
DEVICE_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(DEVICE_NAME)
SOCKET_ADDR = (SERVER_IP, PORT)
EXCHANGE_FORMAT = "utf-8"
BUFFER_SIZE = 2048

# Dictionary to store all connected clients: {username: (conn, addr)}
clients = {}
clients_lock = threading.Lock()  # Thread-safe operations on clients dict

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(SOCKET_ADDR)
server.listen()
print(f"{'='*60}")
print(f"{'MULTI-CLIENT CHAT SERVER':^60}")
print(f"{'='*60}")
print(f"Server IP: {SERVER_IP}")
print(f"Port: {PORT}")
print(f"Status: Listening for connections...")
print(f"{'='*60}\n")

def get_timestamp():
    """Get current timestamp for messages"""
    return datetime.now().strftime("%H:%M:%S")

def broadcast_message(message, sender_username=None, exclude_username=None):
    """Broadcast message to all clients except excluded one"""
    with clients_lock:
        disconnected_clients = []
        for username, (conn, addr) in clients.items():
            # Skip the excluded client (usually the sender for echoing)
            if username == exclude_username:
                continue
            
            try:
                conn.send(message.encode(EXCHANGE_FORMAT))
            except Exception as e:
                print(f"[ERROR] Failed to send to {username}: {e}")
                disconnected_clients.append(username)
        
        # Remove disconnected clients
        for username in disconnected_clients:
            remove_client(username)

def send_private_message(sender_username, recipient_username, message):
    """Send private message to specific user"""
    with clients_lock:
        if recipient_username in clients:
            try:
                conn, _ = clients[recipient_username]
                timestamp = get_timestamp()
                pm_msg = f"[{timestamp}] [PM from {sender_username}] {message}"
                conn.send(pm_msg.encode(EXCHANGE_FORMAT))
                
                # Send confirmation to sender
                sender_conn, _ = clients[sender_username]
                confirm_msg = f"[{timestamp}] [PM to {recipient_username}] {message}"
                sender_conn.send(confirm_msg.encode(EXCHANGE_FORMAT))
                
                print(f"[{timestamp}] [PM] {sender_username} -> {recipient_username}: {message}")
                return True
            except Exception as e:
                print(f"[ERROR] Failed to send PM: {e}")
                return False
        else:
            return False

def send_client_list(username):
    """Send list of all connected users to a specific client"""
    with clients_lock:
        if username in clients:
            try:
                conn, _ = clients[username]
                user_list = ", ".join(clients.keys())
                message = f"\n{'='*50}\nOnline Users ({len(clients)}): {user_list}\n{'='*50}"
                conn.send(message.encode(EXCHANGE_FORMAT))
            except Exception as e:
                print(f"[ERROR] Failed to send client list to {username}: {e}")

def remove_client(username):
    """Remove client from the clients dictionary (should be called with lock held)"""
    if username in clients:
        try:
            conn, addr = clients[username]
            conn.close()
        except:
            pass
        del clients[username]

def handle_client(conn, addr):
    """Handle individual client connection"""
    username = None
    
    try:
        # First, receive username from client
        username = conn.recv(BUFFER_SIZE).decode(EXCHANGE_FORMAT).strip()
        
        if not username:
            print(f"[{addr}] No username received, closing connection")
            conn.close()
            return
        
        # Check if username already exists
        with clients_lock:
            if username in clients:
                error_msg = "ERROR: Username already taken. Please try again with a different name."
                conn.send(error_msg.encode(EXCHANGE_FORMAT))
                conn.close()
                print(f"[{addr}] Username '{username}' already taken, connection rejected")
                return
            
            # Add client to dictionary
            clients[username] = (conn, addr)
        
        # Send welcome message to the new user
        timestamp = get_timestamp()
        welcome_msg = f"\n{'='*50}\nWelcome to the chat server, {username}!\nType '/help' for commands\n{'='*50}"
        conn.send(welcome_msg.encode(EXCHANGE_FORMAT))
        
        # Log and broadcast join notification
        print(f"[{timestamp}] [JOIN] {username} joined from {addr}")
        join_notification = f"[{timestamp}] [SYSTEM] {username} has joined the chat"
        broadcast_message(join_notification, exclude_username=username)
        
        # Send client list to new user
        send_client_list(username)
        
        # Main message handling loop
        while True:
            try:
                message = conn.recv(BUFFER_SIZE).decode(EXCHANGE_FORMAT)
                
                if not message:
                    # Client disconnected
                    break
                
                message = message.strip()
                timestamp = get_timestamp()
                
                # Handle commands
                if message.startswith('/pm '):
                    # Private message format: /pm <username> <message>
                    parts = message.split(' ', 2)
                    if len(parts) >= 3:
                        recipient = parts[1]
                        pm_content = parts[2]
                        success = send_private_message(username, recipient, pm_content)
                        if not success:
                            error_msg = f"[{timestamp}] [ERROR] User '{recipient}' not found or offline"
                            conn.send(error_msg.encode(EXCHANGE_FORMAT))
                    else:
                        error_msg = f"[{timestamp}] [ERROR] Usage: /pm <username> <message>"
                        conn.send(error_msg.encode(EXCHANGE_FORMAT))
                
                elif message == '/list':
                    # List all online users
                    send_client_list(username)
                
                elif message == '/help':
                    # Show help message
                    help_msg = f"""
{'='*50}
CHAT COMMANDS:
  /pm <username> <message>  - Send private message
  /list                     - Show online users
  /help                     - Show this help
  /quit                     - Leave the chat
  
Just type your message to broadcast to everyone!
{'='*50}"""
                    conn.send(help_msg.encode(EXCHANGE_FORMAT))
                
                elif message == '/quit':
                    # Client wants to quit
                    break
                
                else:
                    # Regular broadcast message
                    broadcast_msg = f"[{timestamp}] {username}: {message}"
                    print(f"[{timestamp}] [BROADCAST] {username}: {message}")
                    broadcast_message(broadcast_msg, sender_username=username)
                    
            except Exception as e:
                print(f"[ERROR] Error receiving from {username}: {e}")
                break
    
    except Exception as e:
        print(f"[ERROR] Error handling client {addr}: {e}")
    
    finally:
        # Client disconnected - cleanup
        if username:
            with clients_lock:
                remove_client(username)
            
            timestamp = get_timestamp()
            print(f"[{timestamp}] [LEAVE] {username} left the chat")
            leave_notification = f"[{timestamp}] [SYSTEM] {username} has left the chat"
            broadcast_message(leave_notification)

def main():
    """Main server loop"""
    try:
        while True:
            conn, addr = server.accept()
            # Handle each client in a separate thread
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True  # Daemon thread will exit when main thread exits
            thread.start()
            
            with clients_lock:
                active_clients = len(clients)
            print(f"\n[INFO] New connection attempt from {addr}")
            print(f"[INFO] Active clients: {active_clients}")
    
    except KeyboardInterrupt:
        print("\n\n[SERVER] Shutting down...")
        # Close all client connections
        with clients_lock:
            for username, (conn, addr) in list(clients.items()):
                try:
                    shutdown_msg = "[SYSTEM] Server is shutting down. Goodbye!"
                    conn.send(shutdown_msg.encode(EXCHANGE_FORMAT))
                    conn.close()
                except:
                    pass
        server.close()
        print("[SERVER] Server closed. Goodbye!")
    
    except Exception as e:
        print(f"[ERROR] Server error: {e}")
        server.close()

if __name__ == "__main__":
    main()
