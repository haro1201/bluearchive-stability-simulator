import subprocess
import webbrowser
import socket
import time
import signal

PORT = 8501
URL = f"http://localhost:{PORT}"

def wait_for_port(port, host="localhost", timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            if sock.connect_ex((host, port)) == 0:
                return True
        time.sleep(0.5)
    return False

def main():
    proc = subprocess.Popen([
        "streamlit", "run", "app.py",
        f"--server.port={PORT}",
        "--browser.gatherUsageStats=false",
        "--server.headless=true"   # ブラウザの自動起動を無効にして、後で手動起動
    ])

    try:
        if wait_for_port(PORT):
            webbrowser.open(URL)
            print(f"ブラウザを開きました → {URL}")
        else:
            print("エラー: サーバーが起動しませんでした")

        proc.wait()

    except KeyboardInterrupt:
        print("終了シグナル検知、Streamlitサーバーを停止します...")
        proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            print("強制終了します")
            proc.kill()
    finally:
        print("終了しました")

if __name__ == "__main__":
    main()
