import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("accident_prediction_india.csv")

# Clean column names
df.columns = df.columns.str.strip()

# Select required columns
df = df[['Accident Severity', 'Weather Conditions', 'Road Type',
         'Lighting Conditions', 'Time of Day',
         'City Name', 'State Name']]

# Clean text
df['State Name'] = df['State Name'].astype(str).str.strip()
df['City Name'] = df['City Name'].astype(str).str.strip()

# ---------------- TELANGANA DATA ----------------
df_telangana = df[df['State Name'].str.contains('Telangana', case=False, na=False)]

print("Telangana Data Shape:", df_telangana.shape)

# ---------------- WEATHER (TELANGANA) ----------------
weather_counts = df_telangana['Weather Conditions'].value_counts()

weather_counts.plot(kind='bar')

plt.title("Telangana Accidents by Weather Condition")
plt.xlabel("Weather")
plt.ylabel("Number of Accidents")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ---------------- SEVERITY (TELANGANA) ----------------
severity_counts = df_telangana['Accident Severity'].value_counts()
print("Telangana Severity:\n", severity_counts)

severity_counts.plot(kind='bar')

plt.title("Telangana Accident Severity Distribution")
plt.xlabel("Severity")
plt.ylabel("Count")
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

# ---------------- CITY ANALYSIS (ALL INDIA) ----------------
df_clean_city = df[df['City Name'].str.lower() != 'unknown']

location_counts = df_clean_city['City Name'].value_counts().head(10)

location_counts.plot(kind='bar')

plt.title("Top Cities with Most Accidents (India)")
plt.xlabel("City")
plt.ylabel("Number of Accidents")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Save cleaned dataset
df.to_csv("cleaned_accident_data.csv", index=False)