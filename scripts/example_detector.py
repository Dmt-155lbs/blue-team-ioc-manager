"""
Example script: IOC Detector Integration
Demonstrates how to send IOCs to the API from external tools/scripts.

Usage:
    python example_detector.py

This simulates an automated detection system sending IOCs to the manager.
"""

import requests
import random
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/api/threats"

# Sample data for demonstration
SAMPLE_IPS = [
    "192.168.1.100", "10.0.0.50", "172.16.0.25", 
    "203.0.113.42", "198.51.100.17", "192.0.2.88"
]

SAMPLE_HASHES = [
    "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3",
    "5eb63bbbe01eeed093cb22bb8f5acdc3",
    "d8e8fca2dc0f896fd7cb4cb0031ba249"
]

SAMPLE_URLS = [
    "http://malware-site.evil/payload.exe",
    "https://phishing.bad/login",
    "http://c2server.net:8080/beacon"
]

SAMPLE_DOMAINS = [
    "malware-c2.com", "phishing-site.net", "bad-domain.org"
]

SOURCES = ["Firewall-01", "IDS-Suricata", "SIEM-Alert", "VirusTotal", "AbuseIPDB"]
SEVERITIES = ["High", "Medium", "Low"]


def report_ioc(ioc_type: str, value: str, severity: str, source: str) -> dict:
    """
    Send an IOC to the API.
    
    Args:
        ioc_type: Type of IOC (IP, Hash, URL, Domain)
        value: The indicator value
        severity: Threat level (High, Medium, Low)
        source: Detection source
    
    Returns:
        API response as dict
    """
    payload = {
        "type": ioc_type,
        "value": value,
        "severity": severity,
        "source": source
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ IOC registered: [{ioc_type}] {value} (ID: {data['id']})")
            return data
        elif response.status_code == 409:
            print(f"⚠️  IOC already exists: [{ioc_type}] {value}")
            return response.json()
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return {"error": response.text}
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to API at {API_URL}")
        return {"error": "Connection failed"}


def simulate_detections(count: int = 5):
    """
    Simulate automated IOC detections.
    """
    print(f"\n🔍 Simulating {count} IOC detections...\n")
    print("-" * 60)
    
    samples = {
        "IP": SAMPLE_IPS,
        "Hash": SAMPLE_HASHES,
        "URL": SAMPLE_URLS,
        "Domain": SAMPLE_DOMAINS
    }
    
    for i in range(count):
        ioc_type = random.choice(list(samples.keys()))
        value = random.choice(samples[ioc_type])
        severity = random.choice(SEVERITIES)
        source = random.choice(SOURCES)
        
        report_ioc(ioc_type, value, severity, source)
    
    print("-" * 60)
    print(f"\n✅ Simulation complete. Check the dashboard at http://localhost:8000")


def get_all_threats():
    """
    Retrieve all threats from the API.
    """
    try:
        response = requests.get(API_URL)
        threats = response.json()
        
        print(f"\n📊 Total IOCs in database: {len(threats)}\n")
        
        for t in threats[:10]:  # Show first 10
            print(f"  [{t['type']:6}] {t['value'][:40]:<40} | {t['severity']:6} | {t['source'] or 'N/A'}")
        
        if len(threats) > 10:
            print(f"  ... and {len(threats) - 10} more")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to API at {API_URL}")


if __name__ == "__main__":
    print("=" * 60)
    print("🛡️  IOC Manager - Example Detector Script")
    print("=" * 60)
    
    # Simulate some detections
    simulate_detections(8)
    
    # Show current state
    print("\n")
    get_all_threats()
