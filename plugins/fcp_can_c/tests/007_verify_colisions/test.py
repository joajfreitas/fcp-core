import re
import os
from pathlib import Path
import pytest

base_dir = os.path.abspath(__file__).replace("/test.py", "")
cwd = os.getcwd().split("/")[-1]

def get_path(test_name: str) -> str:
    return f"{base_dir}/{test_name}"

EXPECTED_DEVICE_SERVICES = {
    "dash": {
        "can": {"change_led_status", "snake_leds"},
    },
    "suspot": {
        "can": {"calibrate_pots"}
    }
}

TEST_PARAMS = [
    (device, protocol, services)
    for device, protocols in EXPECTED_DEVICE_SERVICES.items()
    for protocol, services in protocols.items()
]

@pytest.mark.parametrize("device_name, protocol, expected_services", TEST_PARAMS)
def test_all_generated_files_strictly_match_fcp(device_name, protocol, expected_services):
    output_path = get_path("generated_code")
    
    device_files = list(Path(output_path).glob(f"{device_name}_{protocol}_rpc.h"))
    
    assert len(device_files) > 0, f"No generated files found for {device_name}!"

    for filepath in device_files:
        with filepath.open("r") as file:
            generated_code = file.read()
            
        regex_pattern = rf"{device_name}_{protocol}_service_handle_([a-zA-Z0-9_]+)\("
        found_services = set(re.findall(regex_pattern, generated_code))
        
        assert found_services == expected_services, (
            f"Service mismatch in {filepath.name}! "
            f"Extra or missing services: {found_services ^ expected_services}"
        )
