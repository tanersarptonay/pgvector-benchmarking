import subprocess
import time

# Configuration
PROJECT_ID = "pgvector-benchmark-2"  # Replace with your Google Cloud project ID
ZONE = "europe-west10-a"  # Zone of the VMs
SNAPSHOT_NAME = "postgresql-snapshot"  # Name of the snapshot to use
BASE_VM_NAME = "postgresql-vm"  # Base name for new VMs
DIMENSIONS_DISK_SIZES = {
    128: 50,  # 128 dimensions → 50GB disk
    256: 100,  # 256 dimensions → 100GB disk
    512: 200  # 512 dimensions → 200GB disk
}
NEW_VMS = [
    {"name": f"{BASE_VM_NAME}-{dim}d-{size}gb", "disk_size": size, "dimensions": dim}
    for dim, size in DIMENSIONS_DISK_SIZES.items()
]

def create_vm_from_snapshot(vm_name, disk_size):
    """Create a new VM from the specified snapshot."""
    print(f"Creating VM: {vm_name} with disk size {disk_size}GB...")
    try:
        subprocess.run([
            "gcloud", "compute", "instances", "create", vm_name,
            "--zone", ZONE,
            "--machine-type", "e2-standard-4",  # Adjust machine type as needed
            "--boot-disk-size", f"{disk_size}GB",
            "--boot-disk-type", "pd-ssd",
            "--boot-disk-device-name", f"{vm_name}-disk",
            "--source-snapshot", SNAPSHOT_NAME,
            "--tags", "postgresql",
            "--project", PROJECT_ID
        ], check=True)
        print(f"VM {vm_name} created successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error creating VM {vm_name}: {e}")

def resize_file_system(vm_name):
    """Resize the file system on the VM."""
    print(f"Resizing file system for VM: {vm_name}...")
    try:
        # SSH into the VM and resize the file system
        resize_command = (
            "sudo resize2fs $(findmnt -n -o SOURCE /) && df -h"
        )
        subprocess.run([
            "gcloud", "compute", "ssh", vm_name,
            "--zone", ZONE,
            "--command", resize_command,
            "--project", PROJECT_ID
        ], check=True)
        print(f"File system resized successfully for VM: {vm_name}.")
    except subprocess.CalledProcessError as e:
        print(f"Error resizing file system on VM {vm_name}: {e}")

def main():
    # Step 1: Create VMs
    for vm in NEW_VMS:
        create_vm_from_snapshot(vm["name"], vm["disk_size"])
        time.sleep(5)  # Allow time for the VM to initialize

    # Step 2: Resize file systems
    for vm in NEW_VMS:
        resize_file_system(vm["name"])

    print("All VMs created and file systems resized successfully.")

if __name__ == "__main__":
    main()
