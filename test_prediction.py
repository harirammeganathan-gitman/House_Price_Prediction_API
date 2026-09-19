import requests
import pandas as pd

#url = "http://127.0.0.1:5000/predict"
url = "https://uptor-ml-ai-api-workflow-1.onrender.com/predict"

# Send multiple sizes
data = {
    "sizes": [1000, 1500, 1700, 2000]
}

response = requests.post(url, json=data)

if response.status_code == 200:
    results = response.json()

    # Print results neatly
    for item in results:
        print(f"Size: {item['size']} → Predicted Price: {item['predicted_price']}")

    # Save results to CSV
    df = pd.DataFrame(results)
    df.to_csv("predictions.csv", index=False)
    print("\n✅ Results saved to predictions.csv")

else:
    print(f"Error {response.status_code}: {response.text}")
