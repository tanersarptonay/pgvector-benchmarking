# Configuration
PROJECT_ID="pgvector-benchmark-2" # Replace with your project ID
ZONE="europe-west3-a"             # Adjust based on your location
VM_NAME="load-generator-vm"       # Name of the load generator VM
MACHINE_TYPE="e2-standard-4"      # Machine type (adjust as needed)
DISK_SIZE="10GB"                  # Disk size
IMAGE_PROJECT="ubuntu-os-cloud"   # Ubuntu image project
IMAGE_FAMILY="ubuntu-2004-lts"    # Ubuntu 20.04 LTS image family

# Create the Load Generator VM
gcloud compute instances create $VM_NAME \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --boot-disk-size=$DISK_SIZE \
    --image-project=$IMAGE_PROJECT \
    --image-family=$IMAGE_FAMILY \
    --tags="load-generator" \
    --project=$PROJECT_ID
