#!/usr/bin/env python3
"""
Verification script for all channels after migration.
Ensures that the new Block/Program structures are correctly integrated
and that schedules generate without runtime errors.
"""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scripts.testing.simulator import ChannelSimulator, install_mocks
install_mocks()

from scripts.channels import cartoon_network, detective, sitcoms, classic_movies

def test_channel(module, name):
    print(f"\nTesting {name}...")
    print("-" * 40)
    try:
        sim = ChannelSimulator(module)
        # Simulate a Monday (standard) and a Saturday (special blocks)
        monday = datetime(2026, 10, 5)
        saturday = datetime(2026, 10, 10)
        
        print("  Simulating Monday...")
        sched_mon = sim.simulate_day(monday)
        items_mon = [e for e in sched_mon if e['type'] == 'content']
        if not items_mon:
            print("  ❌ Monday generated 0 items!")
            return False
        print(f"  ✅ Monday generated {len(items_mon)} items.")
        
        print("  Simulating Saturday...")
        sched_sat = sim.simulate_day(saturday)
        items_sat = [e for e in sched_sat if e['type'] == 'content']
        if not items_sat:
            print("  ❌ Saturday generated 0 items!")
            return False
        print(f"  ✅ Saturday generated {len(items_sat)} items.")
        
        return True
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all():
    print("Channel Migration Verification")
    print("="*60)
    
    results = []
    results.append(test_channel(cartoon_network, "Cartoon Network"))
    results.append(test_channel(detective, "Detective"))
    results.append(test_channel(sitcoms, "Sitcoms"))
    results.append(test_channel(classic_movies, "Classic Movies"))
    
    if all(results):
        print("\n🎉 All channels passed verification!")
    else:
        print("\n⚠️ Some channels failed.")

if __name__ == "__main__":
    run_all()