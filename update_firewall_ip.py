import subprocess
import requests

# Constants
PROJECT_ID = "pgvector-benchmark-2"  # Replace with your Google Cloud project ID.
LOAD_GENERATOR_INTERNAL_IP = "10.214.0.3/32"  # Replace with the internal IP of your Load Generator
POSTGRESQL_INTERNAL_IP = "10.214.0.4/32"  # Replace with the internal IP of your PostgreSQL VM

# Firewall rules to manage
FIREWALL_RULES = {
    "allow-postgresql-ingress": {
        "ports": ["5433"],
        "source_ips": [LOAD_GENERATOR_INTERNAL_IP],  # Static internal IP
        "description": "PostgreSQL access"
    },
    # "allow-prometheus": {
    #     "ports": ["9090"],
    #     "source_ips": [],  # Leave empty for dynamic public IPs
    #     "description": "Prometheus access"
    # },
    # "allow-node-exporter": {
    #     "ports": ["9100"],
    #     "source_ips": [],  # Leave empty for dynamic public IPs
    #     "description": "Node Exporter access"
    # },
    # "default-allow-ssh": {
    #     "ports": ["22"],
    #     "source_ips": [],  # Leave empty for dynamic public IPs
    #     "description": "SSH access"
    # },
    # "default-allow-http": {
    #     "ports": ["80"],
    #     "source_ips": [],  # Leave empty for dynamic public IPs
    #     "description": "HTTP access"
    # },
    # "default-allow-https": {
    #     "ports": ["443"],
    #     "source_ips": [],  # Leave empty for dynamic public IPs
    #     "description": "HTTPS access"
    # }
}

def get_current_public_ip():
    """Fetch the current public IP address (supports IPv6 and IPv4)."""
    try:
        response = requests.get("https://ifconfig.me", timeout=10)
        response.raise_for_status()
        public_ip = response.text.strip()
        return public_ip
    except Exception as e:
        print(f"Error fetching public IP: {e}")
        return None

def update_firewall_rule(rule_name, ports, source_ips):
    """Update the specified firewall rule with the given source IPs."""
    try:
        source_ranges = ",".join(source_ips) if source_ips else "::/0"  # Support IPv4 or IPv6 ranges
        print(f"Updating rule: {rule_name}, Ports: {ports}, Source: {source_ranges}")

        subprocess.run([
            "gcloud", "compute", "firewall-rules", "update", rule_name,
            "--allow", ",".join([f"tcp:{port}" for port in ports]),
            "--source-ranges", source_ranges,
            "--project", PROJECT_ID
        ], check=True)

        print(f"Firewall rule '{rule_name}' updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error updating rule {rule_name}: {e}")

def main():
    # Get the current public IP
    current_ip = get_current_public_ip()
    if not current_ip:
        print("Unable to fetch public IP. Exiting.")
        return

    # Determine the IP format (IPv4 or IPv6)
    if ":" in current_ip:
        current_ip_range = f"{current_ip}/128"  # IPv6 range
    else:
        current_ip_range = f"{current_ip}/32"  # IPv4 range

    print(f"Current public IP: {current_ip_range}")

    # Update firewall rules
    for rule_name, details in FIREWALL_RULES.items():
        source_ips = details["source_ips"]

        # Add current public IP dynamically if the source_ips list is empty
        if not source_ips:
            source_ips = [current_ip_range]

        update_firewall_rule(rule_name, details["ports"], source_ips)

if __name__ == "__main__":
    main()
