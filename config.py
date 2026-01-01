import socket
from config import SERVER_IP, PORT, EXCHANGE_FORMAT
import threading

running = True
def receive_messages(client_socket):
    """Function to receive messages from the server"""
    global running
    while running:
        try:
            message = client_socket.recv(1024).decode(EXCHANGE_FORMAT)
            if message:
                print(f"\n{message}")
            else:
                print("\n[SYSTEM] Disconnected from server.")
                running = False
                break
        except Exception as e:
            if running:
                print(f"\n[ERROR] Failed to receive message: {e}")
            break
        print("[ERROR] Username cannot be empty.")
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, PORT))

        # Start thread to receive messages
        threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()
        receive_thread.start()
        receive_thread.start()

    # Main loop to send messages
    while running:
        try:
            message = input()
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
        client.connect((SERVER_IP, PORT))
        print("✓ Connected successfully!")
        
        # Send username to server
        client.send(username.encode(EXCHANGE_FORMAT))
        
        # Start receiving thread
        receive_thread = threading.Thread(target=receive_messages, args=(client,))
        receive_thread.daemon = True
        receive_thread.start()
        
    except Exception as e:
        print(f"[ERROR] Could not connect to server: {e}")
        return

    # Main loop to send messages
    while running:
        try:
            message = input()
            if message.strip():
                if message.strip() == '/quit':
                    running = False
                    client.send(message.encode(EXCHANGE_FORMAT))
                    print("\n[SYSTEM] Leaving chat...")
                    break
                else:
                    client.send(message.encode(EXCHANGE_FORMAT))
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
        print("[ERROR] Username cannot be empty.")