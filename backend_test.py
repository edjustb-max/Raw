#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for RA Workshop Application
Tests Material Systems, Window Calculation Engine, BOM Generation, and Sample Data
"""

import requests
import json
import sys
from typing import Dict, List, Any
import time

# Backend API base URL
BASE_URL = "https://doorpro.preview.emergentagent.com/api"

class RAWorkshopTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        self.material_systems = []
        self.glass_types = []
        self.hardware_items = []
        
    def log_result(self, test_name: str, success: bool, message: str, details: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'details': details
        })
        
        if not success:
            print(f"   Details: {details}")
    
    def test_sample_data_initialization(self):
        """Test /api/init-data endpoint"""
        print("\n=== Testing Sample Data Initialization ===")
        
        try:
            response = self.session.get(f"{BASE_URL}/init-data")
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "Sample Data Init", 
                    True, 
                    f"Successfully initialized sample data: {data.get('message', 'OK')}"
                )
                return True
            else:
                self.log_result(
                    "Sample Data Init", 
                    False, 
                    f"Failed with status {response.status_code}", 
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Sample Data Init", False, f"Exception occurred: {str(e)}")
            return False
    
    def test_material_systems_api(self):
        """Test Material Systems API"""
        print("\n=== Testing Material Systems API ===")
        
        try:
            response = self.session.get(f"{BASE_URL}/material-systems")
            
            if response.status_code == 200:
                systems = response.json()
                self.material_systems = systems
                
                if len(systems) >= 3:
                    # Check for expected systems
                    system_names = [s['name'] for s in systems]
                    expected_systems = ["Alu-Serie 45", "uPVC-Serie 70", "Madera-Euro68"]
                    
                    found_systems = [name for name in expected_systems if name in system_names]
                    
                    if len(found_systems) == 3:
                        self.log_result(
                            "Material Systems Load", 
                            True, 
                            f"Successfully loaded {len(systems)} material systems including all expected ones"
                        )
                        
                        # Test system structure
                        for system in systems:
                            required_fields = ['id', 'name', 'material_type', 'compatible_openings']
                            missing_fields = [field for field in required_fields if field not in system]
                            
                            if missing_fields:
                                self.log_result(
                                    "Material System Structure", 
                                    False, 
                                    f"System {system.get('name', 'Unknown')} missing fields: {missing_fields}"
                                )
                                return False
                        
                        self.log_result(
                            "Material System Structure", 
                            True, 
                            "All systems have required fields"
                        )
                        return True
                    else:
                        self.log_result(
                            "Material Systems Load", 
                            False, 
                            f"Missing expected systems. Found: {found_systems}, Expected: {expected_systems}"
                        )
                        return False
                else:
                    self.log_result(
                        "Material Systems Load", 
                        False, 
                        f"Expected at least 3 systems, got {len(systems)}", 
                        systems
                    )
                    return False
            else:
                self.log_result(
                    "Material Systems Load", 
                    False, 
                    f"Failed with status {response.status_code}", 
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Material Systems Load", False, f"Exception: {str(e)}")
            return False
    
    def test_profiles_api(self):
        """Test Profiles API for each material system"""
        print("\n=== Testing Profiles API ===")
        
        if not self.material_systems:
            self.log_result("Profiles API", False, "No material systems available for testing")
            return False
        
        try:
            all_passed = True
            
            for system in self.material_systems:
                system_id = system['id']
                system_name = system['name']
                
                response = self.session.get(f"{BASE_URL}/profiles/{system_id}")
                
                if response.status_code == 200:
                    profiles = response.json()
                    
                    if len(profiles) > 0:
                        # Check profile structure
                        required_fields = ['id', 'system_id', 'code', 'profile_type', 'cost_per_meter']
                        
                        for profile in profiles:
                            missing_fields = [field for field in required_fields if field not in profile]
                            if missing_fields:
                                self.log_result(
                                    f"Profiles for {system_name}", 
                                    False, 
                                    f"Profile missing fields: {missing_fields}"
                                )
                                all_passed = False
                                break
                        
                        if all_passed:
                            self.log_result(
                                f"Profiles for {system_name}", 
                                True, 
                                f"Successfully loaded {len(profiles)} profiles"
                            )
                    else:
                        self.log_result(
                            f"Profiles for {system_name}", 
                            False, 
                            "No profiles found for system"
                        )
                        all_passed = False
                else:
                    self.log_result(
                        f"Profiles for {system_name}", 
                        False, 
                        f"Failed with status {response.status_code}"
                    )
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log_result("Profiles API", False, f"Exception: {str(e)}")
            return False
    
    def test_hardware_api(self):
        """Test Hardware API"""
        print("\n=== Testing Hardware API ===")
        
        try:
            response = self.session.get(f"{BASE_URL}/hardware")
            
            if response.status_code == 200:
                hardware = response.json()
                self.hardware_items = hardware
                
                if len(hardware) >= 5:
                    # Check hardware structure
                    required_fields = ['id', 'name', 'hardware_type', 'cost', 'compatible_openings']
                    
                    for hw in hardware:
                        missing_fields = [field for field in required_fields if field not in hw]
                        if missing_fields:
                            self.log_result(
                                "Hardware Structure", 
                                False, 
                                f"Hardware item missing fields: {missing_fields}"
                            )
                            return False
                    
                    # Check for expected hardware types
                    hardware_types = [hw['hardware_type'] for hw in hardware]
                    expected_types = ['casement_kit', 'awning_kit', 'turn_tilt_kit', 'sliding_kit']
                    
                    found_types = [ht for ht in expected_types if ht in hardware_types]
                    
                    if len(found_types) >= 4:
                        self.log_result(
                            "Hardware Load", 
                            True, 
                            f"Successfully loaded {len(hardware)} hardware items with all opening types"
                        )
                        return True
                    else:
                        self.log_result(
                            "Hardware Load", 
                            False, 
                            f"Missing hardware types. Found: {found_types}, Expected: {expected_types}"
                        )
                        return False
                else:
                    self.log_result(
                        "Hardware Load", 
                        False, 
                        f"Expected at least 5 hardware items, got {len(hardware)}"
                    )
                    return False
            else:
                self.log_result(
                    "Hardware Load", 
                    False, 
                    f"Failed with status {response.status_code}", 
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Hardware Load", False, f"Exception: {str(e)}")
            return False
    
    def test_glass_api(self):
        """Test Glass Types API"""
        print("\n=== Testing Glass Types API ===")
        
        try:
            response = self.session.get(f"{BASE_URL}/glass")
            
            if response.status_code == 200:
                glass_types = response.json()
                self.glass_types = glass_types
                
                if len(glass_types) >= 5:
                    # Check glass structure
                    required_fields = ['id', 'description', 'thickness', 'glass_type', 'u_value', 'cost_per_m2']
                    
                    for glass in glass_types:
                        missing_fields = [field for field in required_fields if field not in glass]
                        if missing_fields:
                            self.log_result(
                                "Glass Structure", 
                                False, 
                                f"Glass type missing fields: {missing_fields}"
                            )
                            return False
                    
                    # Check for expected glass types
                    glass_type_names = [g['glass_type'] for g in glass_types]
                    expected_types = ['double', 'triple', 'laminated']
                    
                    found_types = [gt for gt in expected_types if gt in glass_type_names]
                    
                    if len(found_types) >= 3:
                        self.log_result(
                            "Glass Types Load", 
                            True, 
                            f"Successfully loaded {len(glass_types)} glass types including all expected ones"
                        )
                        return True
                    else:
                        self.log_result(
                            "Glass Types Load", 
                            False, 
                            f"Missing glass types. Found: {found_types}, Expected: {expected_types}"
                        )
                        return False
                else:
                    self.log_result(
                        "Glass Types Load", 
                        False, 
                        f"Expected at least 5 glass types, got {len(glass_types)}"
                    )
                    return False
            else:
                self.log_result(
                    "Glass Types Load", 
                    False, 
                    f"Failed with status {response.status_code}", 
                    response.text
                )
                return False
                
        except Exception as e:
            self.log_result("Glass Types Load", False, f"Exception: {str(e)}")
            return False
    
    def test_window_calculation_engine(self):
        """Test Window Calculation Engine with various configurations"""
        print("\n=== Testing Window Calculation Engine ===")
        
        if not self.material_systems or not self.glass_types:
            self.log_result("Window Calculation", False, "Missing material systems or glass types for testing")
            return False
        
        # Test configurations
        test_configs = [
            {
                "name": "Small Casement Window",
                "config": {
                    "width": 600,
                    "height": 800,
                    "opening_type": "casement",
                    "system_id": self.material_systems[0]['id'],  # Aluminum
                    "glass_id": self.glass_types[0]['id'],
                    "leaves": 1,
                    "mullions": 0,
                    "transoms": 0
                }
            },
            {
                "name": "Large Sliding Window",
                "config": {
                    "width": 2000,
                    "height": 1500,
                    "opening_type": "sliding",
                    "system_id": self.material_systems[1]['id'] if len(self.material_systems) > 1 else self.material_systems[0]['id'],  # uPVC
                    "glass_id": self.glass_types[1]['id'] if len(self.glass_types) > 1 else self.glass_types[0]['id'],
                    "leaves": 2,
                    "mullions": 0,
                    "transoms": 0
                }
            },
            {
                "name": "Turn-Tilt Window with Mullions",
                "config": {
                    "width": 1200,
                    "height": 1400,
                    "opening_type": "turn_tilt",
                    "system_id": self.material_systems[0]['id'],  # Aluminum
                    "glass_id": self.glass_types[2]['id'] if len(self.glass_types) > 2 else self.glass_types[0]['id'],
                    "leaves": 1,
                    "mullions": 1,
                    "transoms": 0
                }
            }
        ]
        
        all_passed = True
        
        for test_case in test_configs:
            try:
                response = self.session.post(
                    f"{BASE_URL}/calculate",
                    json=test_case["config"]
                )
                
                if response.status_code == 200:
                    calculation = response.json()
                    
                    # Validate calculation structure
                    required_fields = ['config', 'bom_items', 'total_material_cost', 'labor_cost', 
                                     'margin_percent', 'final_price', 'weight', 'glass_area']
                    
                    missing_fields = [field for field in required_fields if field not in calculation]
                    
                    if missing_fields:
                        self.log_result(
                            f"Calculation - {test_case['name']}", 
                            False, 
                            f"Missing fields in response: {missing_fields}"
                        )
                        all_passed = False
                        continue
                    
                    # Validate BOM items
                    bom_items = calculation['bom_items']
                    if len(bom_items) == 0:
                        self.log_result(
                            f"Calculation - {test_case['name']}", 
                            False, 
                            "No BOM items generated"
                        )
                        all_passed = False
                        continue
                    
                    # Check for essential BOM item types
                    item_types = [item['item_type'] for item in bom_items]
                    if 'profile' not in item_types or 'glass' not in item_types:
                        self.log_result(
                            f"Calculation - {test_case['name']}", 
                            False, 
                            f"Missing essential BOM item types. Found: {item_types}"
                        )
                        all_passed = False
                        continue
                    
                    # Validate calculations are reasonable
                    total_cost = calculation['total_material_cost']
                    final_price = calculation['final_price']
                    weight = calculation['weight']
                    glass_area = calculation['glass_area']
                    
                    if total_cost <= 0 or final_price <= total_cost or weight <= 0 or glass_area <= 0:
                        self.log_result(
                            f"Calculation - {test_case['name']}", 
                            False, 
                            f"Unrealistic calculations: cost={total_cost}, price={final_price}, weight={weight}, area={glass_area}"
                        )
                        all_passed = False
                        continue
                    
                    # Check margin calculation
                    expected_subtotal = total_cost + calculation['labor_cost']
                    expected_final = expected_subtotal * (1 + calculation['margin_percent'] / 100)
                    
                    if abs(final_price - expected_final) > 0.01:
                        self.log_result(
                            f"Calculation - {test_case['name']}", 
                            False, 
                            f"Margin calculation error. Expected: {expected_final}, Got: {final_price}"
                        )
                        all_passed = False
                        continue
                    
                    self.log_result(
                        f"Calculation - {test_case['name']}", 
                        True, 
                        f"Success: {len(bom_items)} BOM items, €{final_price:.2f} total, {weight:.1f}kg, {glass_area:.2f}m²"
                    )
                    
                else:
                    self.log_result(
                        f"Calculation - {test_case['name']}", 
                        False, 
                        f"Failed with status {response.status_code}", 
                        response.text
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_result(f"Calculation - {test_case['name']}", False, f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n=== Testing Edge Cases ===")
        
        if not self.material_systems or not self.glass_types:
            self.log_result("Edge Cases", False, "Missing data for edge case testing")
            return False
        
        edge_cases = [
            {
                "name": "Very Small Window",
                "config": {
                    "width": 200,
                    "height": 300,
                    "opening_type": "casement",
                    "system_id": self.material_systems[0]['id'],
                    "glass_id": self.glass_types[0]['id'],
                    "leaves": 1,
                    "mullions": 0,
                    "transoms": 0
                },
                "should_succeed": True
            },
            {
                "name": "Very Large Window",
                "config": {
                    "width": 3000,
                    "height": 2500,
                    "opening_type": "sliding",
                    "system_id": self.material_systems[0]['id'],
                    "glass_id": self.glass_types[0]['id'],
                    "leaves": 3,
                    "mullions": 2,
                    "transoms": 1
                },
                "should_succeed": True
            },
            {
                "name": "Invalid System ID",
                "config": {
                    "width": 1000,
                    "height": 1200,
                    "opening_type": "casement",
                    "system_id": "invalid-system-id",
                    "glass_id": self.glass_types[0]['id'],
                    "leaves": 1,
                    "mullions": 0,
                    "transoms": 0
                },
                "should_succeed": False
            },
            {
                "name": "Invalid Glass ID",
                "config": {
                    "width": 1000,
                    "height": 1200,
                    "opening_type": "casement",
                    "system_id": self.material_systems[0]['id'],
                    "glass_id": "invalid-glass-id",
                    "leaves": 1,
                    "mullions": 0,
                    "transoms": 0
                },
                "should_succeed": False
            }
        ]
        
        all_passed = True
        
        for test_case in edge_cases:
            try:
                response = self.session.post(
                    f"{BASE_URL}/calculate",
                    json=test_case["config"]
                )
                
                if test_case["should_succeed"]:
                    if response.status_code == 200:
                        calculation = response.json()
                        if calculation.get('final_price', 0) > 0:
                            self.log_result(
                                f"Edge Case - {test_case['name']}", 
                                True, 
                                f"Successfully handled: €{calculation['final_price']:.2f}"
                            )
                        else:
                            self.log_result(
                                f"Edge Case - {test_case['name']}", 
                                False, 
                                "Calculation returned zero price"
                            )
                            all_passed = False
                    else:
                        self.log_result(
                            f"Edge Case - {test_case['name']}", 
                            False, 
                            f"Expected success but got status {response.status_code}"
                        )
                        all_passed = False
                else:
                    if response.status_code in [400, 404, 422]:
                        self.log_result(
                            f"Edge Case - {test_case['name']}", 
                            True, 
                            f"Correctly rejected with status {response.status_code}"
                        )
                    else:
                        self.log_result(
                            f"Edge Case - {test_case['name']}", 
                            False, 
                            f"Expected error but got status {response.status_code}"
                        )
                        all_passed = False
                        
            except Exception as e:
                self.log_result(f"Edge Case - {test_case['name']}", False, f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting RA Workshop Backend API Tests")
        print(f"Testing against: {BASE_URL}")
        
        # Initialize sample data first
        init_success = self.test_sample_data_initialization()
        
        # Wait a moment for data to be ready
        time.sleep(2)
        
        # Run core API tests
        material_success = self.test_material_systems_api()
        profiles_success = self.test_profiles_api()
        hardware_success = self.test_hardware_api()
        glass_success = self.test_glass_api()
        
        # Run calculation tests
        calculation_success = self.test_window_calculation_engine()
        edge_case_success = self.test_edge_cases()
        
        # Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  • {result['test']}: {result['message']}")
        
        # Overall assessment
        critical_tests = [init_success, material_success, calculation_success]
        all_critical_passed = all(critical_tests)
        
        print(f"\n🎯 OVERALL STATUS: {'✅ PASS' if all_critical_passed else '❌ FAIL'}")
        
        if all_critical_passed:
            print("✨ All critical backend APIs are working correctly!")
            print("✨ Window calculation engine is functioning properly!")
            print("✨ BOM generation is accurate with proper pricing!")
        else:
            print("⚠️  Critical backend functionality has issues that need attention!")
        
        return all_critical_passed, self.test_results

if __name__ == "__main__":
    tester = RAWorkshopTester()
    success, results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)