#!/usr/bin/env python3
"""
Detailed BOM Generation Test for RA Workshop
Tests different material systems, opening types, and configurations
"""

import requests
import json

BASE_URL = "https://doorpro.preview.emergentagent.com/api"

def test_detailed_bom_scenarios():
    """Test BOM generation with detailed scenarios"""
    
    # Get available systems and glass types
    systems_response = requests.get(f"{BASE_URL}/material-systems")
    glass_response = requests.get(f"{BASE_URL}/glass")
    
    if systems_response.status_code != 200 or glass_response.status_code != 200:
        print("❌ Failed to get basic data")
        return
    
    systems = systems_response.json()
    glass_types = glass_response.json()
    
    print("🔍 Available Material Systems:")
    for system in systems:
        print(f"  • {system['name']} ({system['material_type']}) - Compatible: {system['compatible_openings']}")
    
    print(f"\n🔍 Available Glass Types:")
    for glass in glass_types:
        print(f"  • {glass['description']} - {glass['glass_type']} - €{glass['cost_per_m2']}/m²")
    
    # Test scenarios with different material systems
    test_scenarios = [
        {
            "name": "Aluminum Casement - Standard Residential",
            "config": {
                "width": 1200,
                "height": 1400,
                "opening_type": "casement",
                "system_id": next(s['id'] for s in systems if s['material_type'] == 'aluminum'),
                "glass_id": glass_types[0]['id'],  # Standard double glazing
                "leaves": 1,
                "mullions": 0,
                "transoms": 0
            }
        },
        {
            "name": "uPVC Sliding - Large Patio Door",
            "config": {
                "width": 2400,
                "height": 2100,
                "opening_type": "sliding",
                "system_id": next(s['id'] for s in systems if s['material_type'] == 'upvc'),
                "glass_id": next(g['id'] for g in glass_types if g['glass_type'] == 'triple'),  # Triple glazing
                "leaves": 2,
                "mullions": 0,
                "transoms": 0
            }
        },
        {
            "name": "Wood Turn-Tilt - Premium Window",
            "config": {
                "width": 1000,
                "height": 1200,
                "opening_type": "turn_tilt",
                "system_id": next(s['id'] for s in systems if s['material_type'] == 'wood'),
                "glass_id": next(g['id'] for g in glass_types if g['glass_type'] == 'laminated'),  # Security glass
                "leaves": 1,
                "mullions": 0,
                "transoms": 0
            }
        },
        {
            "name": "Aluminum Awning - Small Bathroom Window",
            "config": {
                "width": 600,
                "height": 400,
                "opening_type": "awning",
                "system_id": next(s['id'] for s in systems if s['material_type'] == 'aluminum'),
                "glass_id": glass_types[1]['id'],  # Standard double glazing
                "leaves": 1,
                "mullions": 0,
                "transoms": 0
            }
        }
    ]
    
    print(f"\n{'='*80}")
    print("🧪 DETAILED BOM GENERATION TESTS")
    print(f"{'='*80}")
    
    for scenario in test_scenarios:
        print(f"\n📋 Testing: {scenario['name']}")
        print(f"   Configuration: {scenario['config']['width']}x{scenario['config']['height']}mm, {scenario['config']['opening_type']}")
        
        try:
            response = requests.post(f"{BASE_URL}/calculate", json=scenario['config'])
            
            if response.status_code == 200:
                calculation = response.json()
                
                print(f"   ✅ SUCCESS")
                print(f"   📊 Summary:")
                print(f"      • Total Weight: {calculation['weight']:.1f} kg")
                print(f"      • Glass Area: {calculation['glass_area']:.2f} m²")
                print(f"      • Material Cost: €{calculation['total_material_cost']:.2f}")
                print(f"      • Labor Cost: €{calculation['labor_cost']:.2f}")
                print(f"      • Final Price: €{calculation['final_price']:.2f}")
                print(f"      • Margin: {calculation['margin_percent']:.1f}%")
                
                print(f"   🔧 BOM Items ({len(calculation['bom_items'])} items):")
                
                # Group BOM items by type
                profiles = [item for item in calculation['bom_items'] if item['item_type'] == 'profile']
                glass_items = [item for item in calculation['bom_items'] if item['item_type'] == 'glass']
                hardware_items = [item for item in calculation['bom_items'] if item['item_type'] == 'hardware']
                
                if profiles:
                    print(f"      📏 Profiles:")
                    for item in profiles:
                        print(f"         • {item['description']}: {item['quantity']:.2f} {item['unit']} @ €{item['unit_cost']:.2f} = €{item['total_cost']:.2f}")
                
                if glass_items:
                    print(f"      🪟 Glass:")
                    for item in glass_items:
                        print(f"         • {item['description']}: {item['quantity']:.2f} {item['unit']} @ €{item['unit_cost']:.2f} = €{item['total_cost']:.2f}")
                
                if hardware_items:
                    print(f"      🔧 Hardware:")
                    for item in hardware_items:
                        print(f"         • {item['description']}: {item['quantity']:.0f} {item['unit']} @ €{item['unit_cost']:.2f} = €{item['total_cost']:.2f}")
                
                # Validate calculations
                calculated_material_total = sum(item['total_cost'] for item in calculation['bom_items'])
                if abs(calculated_material_total - calculation['total_material_cost']) > 0.01:
                    print(f"   ⚠️  Material cost mismatch: BOM sum={calculated_material_total:.2f}, reported={calculation['total_material_cost']:.2f}")
                
                expected_labor = calculation['total_material_cost'] * 0.10
                if abs(expected_labor - calculation['labor_cost']) > 0.01:
                    print(f"   ⚠️  Labor cost mismatch: expected={expected_labor:.2f}, reported={calculation['labor_cost']:.2f}")
                
                expected_final = (calculation['total_material_cost'] + calculation['labor_cost']) * (1 + calculation['margin_percent'] / 100)
                if abs(expected_final - calculation['final_price']) > 0.01:
                    print(f"   ⚠️  Final price mismatch: expected={expected_final:.2f}, reported={calculation['final_price']:.2f}")
                
            else:
                print(f"   ❌ FAILED: Status {response.status_code}")
                print(f"      Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {str(e)}")
    
    print(f"\n{'='*80}")
    print("✨ BOM Generation Testing Complete!")
    print(f"{'='*80}")

if __name__ == "__main__":
    test_detailed_bom_scenarios()