import socket
import threading
import sys

PORT = 5173
DEVICE_NAME = socket.gethostname()
SERVER_IP = socket.gethostbyname(DEVICE_NAME)
SOCKET_ADDR = (SERVER_IP, PORT)
EXCHANGE_FORMAT = "utf-8"
BUFFER_SIZE = 2048

# Flag to control receiving thread
running = True

def receive_messages(client_socket):
    """Continuously receive messages from server"""
    global running
    while running:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode(EXCHANGE_FORMAT)
            if message:
                # Check for error messages or system messages
                if message.startswith("ERROR:"):
                    print(f"\n{message}")
                    running = False
                    client_socket.close()
                    print("\nPress Enter to exit...")
                    break
                else:
                    print(f"\n{message}")
                    print("You: ", end="", flush=True)
            else:
                # Server closed connection
                print("\n\n[SYSTEM] Disconnected from server.")
                running = False
                break
        except Exception as e:
            if running:  # Only print error if we're still supposed to be running
                print(f"\n[ERROR] Connection lost: {e}")
            running = False
            break

def send_messages(client_socket, username):
    """Handle sending messages to server"""
    global running
    print("\n" + "="*60)
    print("Connected to chat server!")
    print("="*60)
    print("\nCommands:")
    print("  /pm <username> <message>  - Send private message")
    print("  /list                     - Show online users")
    print("  /help                     - Show help")
    print("  /quit                     - Leave chat")
    print("\nType your message and press Enter to send:")
    print("="*60 + "\n")
    
    while running:
        try:
            print("You: ", end="", flush=True)
            message = input()
            
            if not running:
                break
            
            if message.strip():
                if message.strip() == '/quit':
                    running = False
                    client_socket.send(message.encode(EXCHANGE_FORMAT))
                    print("\n[SYSTEM] Leaving chat...")
                    break
                else:
                    client_socket.send(message.encode(EXCHANGE_FORMAT))
        except EOFError:
            # Handle Ctrl+D or end of input
            break
        except KeyboardInterrupt:
            # Handle Ctrl+C
            print("\n\n[SYSTEM] Disconnecting...")
            running = False
            break
        except Exception as e:
            if running:
                print(f"\n[ERROR] Failed to send message: {e}")
            break

def main():
    """Main client function"""
    global running
    
    print("="*60)
    print("MULTI-CLIENT CHAT CLIENT".center(60))
    print("="*60)
    print(f"Server: {SERVER_IP}:{PORT}")
    print("="*60 + "\n")
    
    # Get username from user
    username = input("Enter your username: ").strip()
    
    if not username:
        print("[ERROR] Username cannot be empty!")
        return
    
    if ' ' in username:
        print("[ERROR] Username cannot contain spaces!")
        return
    
    if username.startswith('/'):
        print("[ERROR] Username cannot start with '/'!")
        return
    
    try:
        # Connect to server
        print(f"\nConnecting to server at {SERVER_IP}:{PORT}...")
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(SOCKET_ADDR)
        print("✓ Connected successfully!")
        
        # Send username to server
        client.send(username.encode(EXCHANGE_FORMAT))
        
        # Start receiving thread
        receive_thread = threading.Thread(target=receive_messages, args=(client,))
        receive_thread.daemon = True
        receive_thread.start()
        
        # Small delay to receive welcome message first
        import time
        time.sleep(0.5)
        
        # Handle sending messages (runs in main thread)
        send_messages(client, username)
        
        # Cleanup
        running = False
        client.close()
        print("\n[SYSTEM] Disconnected from server. Goodbye!\n")
        
    except ConnectionRefusedError:
        print(f"\n[ERROR] Could not connect to server at {SERVER_IP}:{PORT}")
        print("Make sure the server is running!")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
    finally:
        running = False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[SYSTEM] Client terminated. Goodbye!")
        sys.exit(0)
