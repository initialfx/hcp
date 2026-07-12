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

def create_fx_scene():
    host = "127.0.0.1"
    port = 9876
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10.0)
        sock.connect((host, port))
        
        print("Connected to Houdini server. Constructing Curl Noise Trail Effect...")
        
        # 1. Create a Geometry Container
        r1 = send_command(sock, "create_node", {
            "node_type": "geo",
            "parent_path": "/obj",
            "name": "antigravity_fx"
        })
        print(f"1. Created geo container: {r1}")
        
        # 2. Create Sphere SOP (Source emitter)
        r2 = send_command(sock, "create_node", {
            "node_type": "sphere",
            "parent_path": "/obj/antigravity_fx",
            "name": "source_sphere"
        })
        print(f"2. Created sphere: {r2}")
        
        # Modify Sphere properties (make it a polygon sphere with high rows/cols)
        send_command(sock, "set_parameters", {
            "path": "/obj/antigravity_fx/source_sphere",
            "parameters": {
                "type": "polygon",
                "rad": [1.5, 1.5, 1.5],
                "freq": 3
            }
        })
        
        # 3. Create Scatter SOP
        r3 = send_command(sock, "create_node", {
            "node_type": "scatter",
            "parent_path": "/obj/antigravity_fx",
            "name": "scatter_points"
        })
        print(f"3. Created scatter: {r3}")
        
        # Modify Scatter properties (scatter 300 points)
        send_command(sock, "set_parameters", {
            "path": "/obj/antigravity_fx/scatter_points",
            "parameters": {
                "npts": 300
            }
        })
        
        # Connect Sphere to Scatter
        send_command(sock, "connect_nodes", {
            "from_path": "/obj/antigravity_fx/source_sphere",
            "to_path": "/obj/antigravity_fx/scatter_points"
        })
        
        # 4. Create Attribute Wrangle to apply Curl Noise
        vex_code = (
            "vector pos = @P;\n"
            "// Apply time-based curl noise\n"
            "vector noise = curlnoise(pos * 0.7 + @Time * 0.5);\n"
            "@P += noise * 1.5;\n"
            "@v = noise; // Save velocity for visualization or coloring\n"
        )
        r4 = send_command(sock, "create_wrangle", {
            "parent_path": "/obj/antigravity_fx",
            "name": "curl_noise_wrangle",
            "vex_code": vex_code,
            "run_over": "points",
            "input_node": "/obj/antigravity_fx/scatter_points"
        })
        print(f"4. Created Wrangle with Curl Noise VEX: {r4}")
        
        # 5. Create Trail SOP to connect moving points into trails
        r5 = send_command(sock, "create_node", {
            "node_type": "trail",
            "parent_path": "/obj/antigravity_fx",
            "name": "make_trails"
        })
        print(f"5. Created trail SOP: {r5}")
        
        # Set Trail parameters (Result Type = Connect as Polygons, Trail Length = 15)
        send_command(sock, "set_parameters", {
            "path": "/obj/antigravity_fx/make_trails",
            "parameters": {
                "result": "connect", # Connect as Polygons
                "length": 15
            }
        })
        
        # Connect Wrangle to Trail
        send_command(sock, "connect_nodes", {
            "from_path": "/obj/antigravity_fx/curl_noise_wrangle",
            "to_path": "/obj/antigravity_fx/make_trails"
        })
        
        # 6. Create Color SOP to color trails based on velocity or bounding box
        r6 = send_command(sock, "create_node", {
            "node_type": "color",
            "parent_path": "/obj/antigravity_fx",
            "name": "color_trails"
        })
        print(f"6. Created color SOP: {r6}")
        
        # Set Color parameter to Bounding Box / Ramp
        send_command(sock, "set_parameters", {
            "path": "/obj/antigravity_fx/color_trails",
            "parameters": {
                "colortype": "bbox", # Bounding Box ramp
                "rampattribute": "P"
            }
        })
        
        # Connect Trail to Color
        send_command(sock, "connect_nodes", {
            "from_path": "/obj/antigravity_fx/make_trails",
            "to_path": "/obj/antigravity_fx/color_trails"
        })
        
        # Set display and render flags on Color node
        send_command(sock, "set_node_flags", {
            "path": "/obj/antigravity_fx/color_trails",
            "display": True,
            "render": True
        })
        
        # Clean layout of node graph
        send_command(sock, "layout_children", {
            "path": "/obj/antigravity_fx"
        })
        
        print("\nCurl Noise Trail Effect Scene built successfully!")
        sock.close()
        
    except Exception as e:
        print(f"Error during FX scene creation: {e}")

if __name__ == "__main__":
    create_fx_scene()
