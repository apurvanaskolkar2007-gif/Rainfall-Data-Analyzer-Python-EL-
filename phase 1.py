import matplotlib.pyplot as plt

# Rainfall data in mm
rainfall_data = {
    "Nagpur": {
        "June": 180,
        "July": 250,
        "August": 220,
        "September": 140
    },
    "Mumbai": {
        "June": 500,
        "July": 700,
        "August": 650,
        "September": 300
    },
    "Delhi": {
        "June": 120,
        "July": 280,
        "August": 240,
        "September": 150
    }
}


print("========== RAINFALL DATA ANALYZER ==========\n")


# Display data
print("Rainfall Data:")
print("--------------------------------------------")

for city, months in rainfall_data.items():
    print("\nCity:", city)

    for month, rainfall in months.items():
        print(month, ":", rainfall, "mm")


# Calculate statistics
print("\n\n========== RAINFALL STATISTICS ==========")

for city, months in rainfall_data.items():

    values = list(months.values())

    total = sum(values)
    average = total / len(values)
    maximum = max(values)
    minimum = min(values)

    max_month = max(months, key=months.get)
    min_month = min(months, key=months.get)

    print("\nCity:", city)
    print("Total Rainfall:", total, "mm")
    print("Average Rainfall:", round(average, 2), "mm")
    print("Maximum Rainfall:", maximum, "mm")
    print("Maximum Rainfall Month:", max_month)
    print("Minimum Rainfall:", minimum, "mm")
    print("Minimum Rainfall Month:", min_month)


# Overall rainfall
all_values = []

for city in rainfall_data:
    all_values.extend(rainfall_data[city].values())

print("\n\n========== OVERALL REPORT ==========")

print("Total Rainfall:", sum(all_values), "mm")
print("Average Rainfall:", round(sum(all_values) / len(all_values), 2), "mm")
print("Maximum Rainfall:", max(all_values), "mm")
print("Minimum Rainfall:", min(all_values), "mm")


# Graph for Nagpur
city = "Nagpur"

months = list(rainfall_data[city].keys())
values = list(rainfall_data[city].values())

plt.figure(figsize=(8, 5))

plt.bar(months, values)

plt.title("Monthly Rainfall - " + city)
plt.xlabel("Month")
plt.ylabel("Rainfall (mm)")

plt.tight_layout()
plt.show()