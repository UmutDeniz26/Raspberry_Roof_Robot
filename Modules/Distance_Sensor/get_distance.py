import subprocess

def run_sensor_code():
    # Compile and run the C code
    result = subprocess.run(["gcc", "-o", "sensor", "/home/umut/Desktop/Raspberry_Roof_Robot/Tests/Distance_Sensor/VL53L3CX_rasppi/example/main_custom.c"], capture_output=True)
    if result.returncode == 0:
        # Run the compiled executable
        result = subprocess.run(["./sensor"], capture_output=True, text=True)
        if result.returncode == 0:
            # Parse the output to extract the average distance
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if line.startswith("Average Distance:"):
                    average_distance = int(line.split(":")[1].strip().split(" ")[0])
                    return average_distance
        else:
            print("Error running sensor code:", result.stderr)
    else:
        print("Error compiling sensor code:", result.stderr)

# Run the sensor code and get the average distance
average_distance = run_sensor_code()
if average_distance is not None:
    print("Average Distance measured by sensor:", average_distance, "mm")
