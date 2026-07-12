import socket
import json
import struct

def test_houdini_connection():
    host = "127.0.0.1"
    port = 9876
    print(f"Connecting to Houdini TCP server at {host}:{port}...")
    
    try:
        # 1. Establish connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((host, port))
        print("Connected successfully!")
        
        # 2. Send ping command (using the framed protocol: 4-byte length header + JSON data)
        command = {"type": "ping", "params": {}}
        data_out = json.dumps(command).encode("utf-8")
        header = struct.pack('>I', len(data_out))
        sock.sendall(header + data_out)
        print(f"Sent: {command}")
        
        # 3. Read response header (4 bytes)
        header_in = sock.recv(4)
        if not header_in or len(header_in) < 4:
            print("Failed to receive valid response header.")
            sock.close()
            return
            
        data_len = struct.unpack('>I', header_in)[0]
        
        # 4. Read response body
        data_in = bytearray()
        while len(data_in) < data_len:
            packet = sock.recv(data_len - len(data_in))
            if not packet:
                break
            data_in.extend(packet)
            
        response = json.loads(data_in.decode("utf-8"))
        print(f"Received response: {response}")
        
        if response.get("status") == "success" or "pong" in response.get("result", {}):
            print("\n🎉 Connection test PASSED! Houdini TCP server is responding correctly.")
        else:
            print("\n⚠️ Received unexpected response format.")
            
        sock.close()
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("Make sure Houdini is running and the HCP Server shelf tool has been clicked.")

if __name__ == "__main__":
    test_houdini_connection()
