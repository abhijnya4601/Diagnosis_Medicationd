# Install ngrok first
# pip install pyngrok

from pyngrok import ngrok

def launch_streamlit_with_ngrok():
    """Launch Streamlit and create public link"""
    import threading
    import time
    
    # Create streamlit file
    create_streamlit_file()
    
    # Start streamlit in background
    def run_streamlit():
        subprocess.run(['streamlit', 'run', 'streamlit_patient_app.py', '--server.port=8501'])
    
    thread = threading.Thread(target=run_streamlit)
    thread.daemon = True
    thread.start()
    
    time.sleep(3)  # Wait for streamlit to start
    
    # Create public URL
    public_url = ngrok.connect(8501)
    
    print("\n" + "="*80)
    print("🌐 PUBLIC URL (Share this with your team):")
    print("="*80)
    print(f"\n{public_url}\n")
    print("⚠️  This link works as long as this notebook is running")
    print("⚠️  To stop: Kernel → Interrupt")
    print("="*80)
    
    display(HTML(f'<h2>🔗 Share this link: <a href="{public_url}" target="_blank">{public_url}</a></h2>'))
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        ngrok.disconnect(public_url)
        print("\n✓ Stopped")

# To use:
# launch_streamlit_with_ngrok()
