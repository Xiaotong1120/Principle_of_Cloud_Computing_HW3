import numpy as np

def calculate_percentiles(latency_file_path):
    """
    Reads latency data from a file and calculates 90th and 95th percentiles.

    Args:
        latency_file_path (str): Path to the latency data file.

    Returns:
        dict: A dictionary with 90th and 95th percentiles.
    """
    try:
        # Read latency data from file
        with open(latency_file_path, 'r') as file:
            latencies = [float(line.strip()) for line in file if line.strip()]
        
        # Ensure there is data in the file
        if not latencies:
            raise ValueError("Latency file is empty.")
        
        # Calculate percentiles
        percentile_90 = np.percentile(latencies, 90)
        percentile_95 = np.percentile(latencies, 95)
        
        return {
            "90th_percentile": percentile_90,
            "95th_percentile": percentile_95
        }
    except FileNotFoundError:
        print(f"File not found: {latency_file_path}")
        return None
    except ValueError as e:
        print(f"Error processing file: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Call the function and print the output
result = calculate_percentiles("./PA3/latency_data_producer-job-4l22k.txt")
if result:
    print(f"90th Percentile: {result['90th_percentile']}")
    print(f"95th Percentile: {result['95th_percentile']}")