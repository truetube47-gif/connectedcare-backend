import requests
import json

# Sample of common drugs to populate the database
drugs_to_add = [
    {"trade_name": "Aspirin", "strength": "81mg", "dosage_form": "Tablets", "manufacturer": "Bayer"},
    {"trade_name": "Ibuprofen", "strength": "400mg", "dosage_form": "Tablets", "manufacturer": "Advil"},
    {"trade_name": "Acetaminophen", "strength": "500mg", "dosage_form": "Tablets", "manufacturer": "Tylenol"},
    {"trade_name": "Amoxicillin", "strength": "500mg", "dosage_form": "Capsules", "manufacturer": "Generic"},
    {"trade_name": "Lisinopril", "strength": "10mg", "dosage_form": "Tablets", "manufacturer": "Generic"},
    {"trade_name": "Metformin", "strength": "500mg", "dosage_form": "Tablets", "manufacturer": "Generic"},
    {"trade_name": "Amlodipine", "strength": "5mg", "dosage_form": "Tablets", "manufacturer": "Norvasc"},
    {"trade_name": "Atorvastatin", "strength": "20mg", "dosage_form": "Tablets", "manufacturer": "Lipitor"},
    {"trade_name": "Omeprazole", "strength": "20mg", "dosage_form": "Capsules", "manufacturer": "Prilosec"},
    {"trade_name": "Simvastatin", "strength": "40mg", "dosage_form": "Tablets", "manufacturer": "Zocor"},
    {"trade_name": "Losartan", "strength": "50mg", "dosage_form": "Tablets", "manufacturer": "Cozaar"},
    {"trade_name": "Albuterol", "strength": "90mcg", "dosage_form": "Inhaler", "manufacturer": "ProAir"},
    {"trade_name": "Prednisone", "strength": "5mg", "dosage_form": "Tablets", "manufacturer": "Generic"},
    {"trade_name": "Gabapentin", "strength": "300mg", "dosage_form": "Capsules", "manufacturer": "Neurontin"},
    {"trade_name": "Sertraline", "strength": "50mg", "dosage_form": "Tablets", "manufacturer": "Zoloft"},
    {"trade_name": "Tramadol", "strength": "50mg", "dosage_form": "Tablets", "manufacturer": "Ultram"},
    {"trade_name": "Citalopram", "strength": "20mg", "dosage_form": "Tablets", "manufacturer": "Celexa"},
    {"trade_name": "Tamsulosin", "strength": "0.4mg", "dosage_form": "Capsules", "manufacturer": "Flomax"},
    {"trade_name": "Levothyroxine", "strength": "100mcg", "dosage_form": "Tablets", "manufacturer": "Synthroid"},
    {"trade_name": "Warfarin", "strength": "5mg", "dosage_form": "Tablets", "manufacturer": "Coumadin"}
]

print("This script would populate the drugs database.")
print("In production, you would:")
print("1. Import FDA drug database")
print("2. Use pharmacy database APIs")
print("3. Load from CSV/Excel files")
print(f"\nSample drugs to add: {len(drugs_to_add)} items")
for drug in drugs_to_add[:5]:
    print(f"  - {drug['trade_name']} {drug['strength']} ({drug['dosage_form']})")
