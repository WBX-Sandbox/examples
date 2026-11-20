"""Desktop & Computer Use (beta, enabled per team on request): open a browser window, click, type and take a screenshot.

Watch it live in the portal: Sandboxes → Desktop."""
from _env import check_env
from wbxsandbox import Sandbox, features

check_env()

if not features().get("desktop"):
    raise SystemExit("Desktop & Computer Use is not enabled for your account – it is a beta, enabled on request.")

with Sandbox.create(template="desktop", timeout=600) as sb:
    # programs on the screen run as the desktop user, in the background
    sb.run("su user -c 'DISPLAY=:0 nohup chromium https://example.com >/dev/null 2>&1 &'", timeout=10)
    sb.computer.actions([{"type": "wait", "ms": 3000}])
    print(sb.computer.status())

    sb.computer.click(640, 400)
    shot = sb.computer.screenshot(format="jpeg", quality=70, max_width=1280)
    shot.save("desktop.jpg")
    print("saved desktop.jpg", shot.width, "x", shot.height)
