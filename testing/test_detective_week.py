#!/usr/bin/env python3
"""
Test script for Detective Channel - Full Week Prime Time.
Verifies the daily themed rotation.
"""
import sys
import os
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, install_mocks
install_mocks()

from scripts.channels import detective

def run_test():
    print("Testing Detective Channel - Prime Time Week")
    print("="*60)
    
    # Start on a Monday
    start_date = date(2026, 10, 5) # Monday
    
    sim = ChannelSimulator(detective)
    
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        day_name = current_date.strftime("%A")
        print(f"\n{day_name} ({current_date})")
        print("-" * 40)
        
        schedule = sim.simulate_day(current_date)
        
        # Filter for Prime Time (20:00 - 23:00)
        prime_items = [e for e in schedule if 20 <= e['time'].hour < 23 and e['type'] == 'content']
        
        if not prime_items:
            print("❌ No prime time content found.")
        else:
            for item in prime_items:
                print(f"{item['time'].strftime('%H:%M')} | {item['content']}")

    print("\n" + "="*60)

if __name__ == "__main__":
    run_test()