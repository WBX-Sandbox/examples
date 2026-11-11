"""Write, read, list and remove files inside a sandbox."""
from _env import check_env
from wbxsandbox import Sandbox

check_env()

with Sandbox.create(timeout=120, internet=False) as sb:
    sb.files.write("/home/user/demo/hello.txt", "Hello from WBX Sandbox\n")
    sb.files.write("/home/user/demo/data.bin", bytes(range(256)))

    print(sb.files.read_text("/home/user/demo/hello.txt").strip())
    print("binary bytes:", len(sb.files.read("/home/user/demo/data.bin")))
    for entry in sb.files.list("/home/user/demo"):
        print(f"  {entry['name']:<10} {entry['size']:>5} B")

    sb.files.remove("/home/user/demo/data.bin")
    print("after remove:", [e["name"] for e in sb.files.list("/home/user/demo")])
