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

def build_scene():
    host = "127.0.0.1"
    port = 9876
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10.0)
        sock.connect((host, port))
        
        print("Connected to Houdini server. Creating scene...")
        
        # 1. Create a Geometry Container
        r1 = send_command(sock, "create_node", {
            "node_type": "geo",
            "parent_path": "/obj",
            "name": "antigravity_demo"
        })
        print(f"1. Created geo node: {r1}")
        
        # 2. Create Torus
        r2 = send_command(sock, "create_node", {
            "node_type": "torus",
            "parent_path": "/obj/antigravity_demo",
            "name": "torus1"
        })
        print(f"2. Created torus: {r2}")
        
        # 3. Create Mountain (SOP) to deform the torus
        r3 = send_command(sock, "create_node", {
            "node_type": "mountain",
            "parent_path": "/obj/antigravity_demo",
            "name": "mountain1"
        })
        print(f"3. Created mountain SOP: {r3}")
        
        # 4. Connect Torus output to Mountain input
        r4 = send_command(sock, "connect_nodes", {
            "from_path": "/obj/antigravity_demo/torus1",
            "to_path": "/obj/antigravity_demo/mountain1"
        })
        print(f"4. Connected torus -> mountain: {r4}")
        
        # 5. Set display/render flag on the mountain node
        r5 = send_command(sock, "set_node_flags", {
            "path": "/obj/antigravity_demo/mountain1",
            "display": True,
            "render": True
        })
        print(f"5. Set display/render flags: {r5}")
        
        # 6. Layout nodes neatly
        r6 = send_command(sock, "layout_children", {
            "path": "/obj/antigravity_demo"
        })
        print(f"6. Laid out nodes: {r6}")
        
        print("\nSuccessfully built a test scene inside Houdini!")
        sock.close()
        
    except Exception as e:
        print(f"Error during scene creation: {e}")

if __name__ == "__main__":
    build_scene()
