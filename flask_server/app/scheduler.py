from apscheduler.schedulers.background import BackgroundScheduler
from flask_server.app.controller.api.device_controller import DeviceController
import atexit
import logging

# Setup Logging
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.WARNING)

def job_sync_all(app):
    print("\n[SCHEDULER] Auto-Sync Started (Every 5 Mins)...")
    types = ['power', 'water', 'gas', 'smoke', 'fire', 'weather', 'lux', 'humidity_temp', 'ultrasonic', 'other']
    
    # Use the passed app instance
    with app.app_context():
        for t in types:
            try:
                # Call sync logic
                DeviceController.sync_data_records(t)
            except Exception as e:
                print(f"[SCHEDULER] Error syncing {t}: {e}")
    
    print("[SCHEDULER] Auto-Sync Finished!\n")

def init_scheduler(app):
    scheduler = BackgroundScheduler()
    # Pass 'app' as argument to the job
    scheduler.add_job(func=job_sync_all, args=[app], trigger="interval", minutes=5)
    
    scheduler.start()
    print("Background Scheduler Started: Auto-Sync every 5 minutes.")
    
    # Matikan scheduler saat app mati
    atexit.register(lambda: scheduler.shutdown())
