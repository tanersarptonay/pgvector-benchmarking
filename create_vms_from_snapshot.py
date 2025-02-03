import subprocess
import time

PROJECT_ID = "pgvector-benchmark-2"
ZONE = "europe-west10-a"
SNAPSHOT_NAME = "pgvector-bootable-snap"
BASE_VM_NAME = "postgresql-vm"

DIMENSIONS_DISK_SIZES = {
    128: 50,
    256: 50,
    512: 100
}

NEW_VMS = [
    {
        "name": f"{BASE_VM_NAME}-{dim}d-{size}gb",
        "disk_size": size,
        "dimensions": dim
    }
    for dim, size in DIMENSIONS_DISK_SIZES.items()
]

def create_vm_from_snapshot(vm_name, disk_size):
    """Create a new VM from a snapshot (older gcloud style)."""
    print(f"Creating VM: {vm_name} with disk size {disk_size}GB...")
    cmd = [
        "gcloud", "compute", "instances", "create", vm_name,
        "--project", PROJECT_ID,
        "--zone", ZONE,
        "--machine-type", "e2-standard-4",      # adjust as needed
        f"--boot-disk-size={disk_size}GB",
        "--boot-disk-type=pd-ssd",
        f"--source-snapshot={SNAPSHOT_NAME}",   # using --source-snapshot
        "--tags=postgresql"
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"VM {vm_name} created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating VM {vm_name}: {e}")

def resize_file_system(vm_name):
    """Resize the file system on the VM."""
    print(f"Resizing file system for VM: {vm_name}...")
    # If the OS uses ext4:
    resize_command = "sudo resize2fs $(findmnt -n -o SOURCE /) && df -h"
    # If XFS, use: resize_command = "sudo xfs_growfs / && df -h"

    cmd = [
        "gcloud", "compute", "ssh", vm_name,
        "--project", PROJECT_ID,
        "--zone", ZONE,
        "--command", resize_command
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"File system resized successfully for VM: {vm_name}.")
    except subprocess.CalledProcessError as e:
        print(f"Error resizing file system on VM {vm_name}: {e}")

def main():
    # Step 1: Create VMs
    for vm_info in NEW_VMS:
        vm_name = vm_info["name"]
        disk_size = vm_info["disk_size"]
        create_vm_from_snapshot(vm_name, disk_size)
        time.sleep(10)  # give some time for each VM to initialize

    # Step 2: Resize file systems (optional if the OS auto-resizes)
    for vm_info in NEW_VMS:
        vm_name = vm_info["name"]
        resize_file_system(vm_name)
        time.sleep(5)

    print("All VMs created and file systems resized successfully.")

if __name__ == "__main__":
    main()
