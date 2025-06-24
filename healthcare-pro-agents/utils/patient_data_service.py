import requests

CLOUD_FUNCTION_URL = "https://your-cloud-run-url/lookup_patient_data"  # Replace with actual

def fetch_pro_history(patient_id: str):
    try:
        response = requests.post(
            CLOUD_FUNCTION_URL,
            json={"patient_id": patient_id},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get("pro_history", [])
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print("Cloud function error:", str(e))
        return []
