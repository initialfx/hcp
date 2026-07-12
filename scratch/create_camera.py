import socket
import json
import struct

def send_command(sock, cmd_type, params):
    command = {"type": cmd_type, "params": params}
    data_out = json.dumps(command).encode("utf-8")
    header = struct.pack('>I', len(data_out))
    sock.sendall(header + data_out)
    
    header_in = sock.recv(4)
    if not header_in or len(header_in) < 4:
        raise ConnectionError("Failed to receive response header.")
    data_len = struct.unpack('>I', header_in)[0]
    
    data_in = bytearray()
    while len(data_in) < data_len:
        packet = sock.recv(data_len - len(data_in))
        if not packet:
            break
        data_in.extend(packet)
    return json.loads(data_in.decode("utf-8"))

def create_camera_scene():
    host = "127.0.0.1"
    port = 9876
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10.0)
        sock.connect((host, port))
        
        print("Connected to Houdini server. Creating camera...")
        
        # 1. Create a Camera Node under /obj
        r1 = send_command(sock, "create_node", {
            "node_type": "cam",
            "parent_path": "/obj",
            "name": "antigravity_camera"
        })
        print(f"1. Created camera: {r1}")
        
        # Check if node was created successfully
        if r1.get("status") == "success":
            cam_path = r1["result"]["path"]
            
            # 2. Set camera translation (t), rotation (r), and focal length (focal)
            r2 = send_command(sock, "set_parameters", {
                "path": cam_path,
                "parameters": {
                    "t": [0.0, 3.5, 10.0],
                    "r": [-15.0, 0.0, 0.0],
                    "focal": 50.0
                }
            })
            print(f"2. Set camera parameters: {r2}")
            
            # 3. Clean layout of /obj context
            r3 = send_command(sock, "layout_children", {
                "path": "/obj"
            })
            print(f"3. Sorted nodes under /obj: {r3}")
            
            print("\nCamera creation and positioning succeeded!")
        else:
            print("Failed to create camera node.")
            
        sock.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_camera_scene()
