import sys
import os
import time

time = time.time()
container_id = (sys.argv[1] if len(sys.argv) >= 2 else None) or os.popen("docker ps | grep database | awk '{print $1}'").read().strip()
print(f"Backing up {container_id}")
os.system(f"docker-compose exec database pg_dumpall -U tts -f back-{time}.sql")
print(f"Dumped database to backup file")
os.system(f"docker cp {container_id}:back-{time}.sql backups")
print(f"Copied database backup out of container")
os.system("rclone sync backups")