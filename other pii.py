import re
import openpyxl
from openpyxl.styles import Font

# Define the input/output files
input_file = "input.txt"
output_file = "output.xlsx"

# Updated regex patterns with punctuation handling
pii_patterns = {
    "PAN": r"(?<![A-Z0-9])[A-Z]{5}[0-9]{4}[A-Z](?![A-Z0-9])",
    "Email": r"(?<![\w])[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,10}(?![\w])",
    "Mobile": r"(?<!\d)(?:\+91[\-\s]?|91[\-\s]?|91|0)?[6-9]\d{9}(?!\d)",
    "UPI": r"(?<![\w])[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}(?![\w])"
}

# Address key indicators
address_keys = {
    "Address": [
        "address", "full_address", "complete_address", "residential_address", "permanent_address",
        "current_address", "correspondence_address", "present_address", "mailing_address",
        "billing_address", "shipping_address", "registered_address", "home_address",
        "office_address", "work_address", "business_address", "shop_address", "delivery_address", "native_address",
        "house_no", "building_name", "flat_no", "apartment", "door_number", "plot_no", "block",
        "floor", "tower", "unit_number", "address_line1", "address_line2", "street", "street_name",
        "road", "lane", "area", "locality", "colony", "sector", "village", "district",
        "taluk", "mandal", "tehsil", "municipality", "town", "city", "state", "region",
        "zone", "division", "province", "pincode", "pin", "postal_code", "zip", "zip_code",
        "location", "geo_location", "place", "addr", "addr1", "addr2"
    ]
}

# Initialize workbook
workbook = openpyxl.Workbook()
workbook.remove(workbook.active)

# Create a sheet for each PII type
sheets = {}
match_counts = {}
for pii_type in pii_patterns.keys():
    sheet = workbook.create_sheet(title=pii_type)
    sheet.append(["Match", "Line Number", "Context Line"])
    sheets[pii_type] = sheet
    match_counts[pii_type] = 0

# Address sheet
address_sheet = workbook.create_sheet(title="Address")
address_sheet.append(["Keyword", "Line Number", "Context Line"])
match_counts["Address"] = 0

# Initialize line counter
total_lines_scanned = 0

# Read and process the input file
with open(input_file, "r", encoding="utf-8") as file:
    for line_number, line in enumerate(file, start=1):
        total_lines_scanned += 1

        # Regex-based PII detection
        for pii_type, pattern in pii_patterns.items():
            for match in re.finditer(pattern, line):
                matched_text = match.group()
                highlighted = line.replace(matched_text, f"<<{matched_text}>>", 1)
                sheets[pii_type].append([matched_text, line_number, highlighted.strip()])
                match_counts[pii_type] += 1

        # Address keyword detection
        lowered = line.lower()
        for keyword in address_keys["Address"]:
            if keyword.lower() in lowered:
                highlighted = re.sub(f"(?i)({re.escape(keyword)})", r"<<\1>>", line)
                address_sheet.append([keyword, line_number, highlighted.strip()])
                match_counts["Address"] += 1
                break  # Avoid duplicates

# Apply red font to "Context Line"
red_font = Font(color="FF0000")
for sheet in list(sheets.values()) + [address_sheet]:
    for row in sheet.iter_rows(min_row=2, min_col=3, max_col=3):
        cell = row[0]
        if cell.value and "<<" in cell.value:
            text = cell.value
            clean_text = text.replace("<<", "").replace(">>", "")
            cell.value = clean_text
            cell.font = red_font

# Save the workbook
workbook.save(output_file)

# Print summary
print("\n🔍 PII Scan Summary:")
print(f"- Total lines scanned: {total_lines_scanned}")
for pii_type, count in match_counts.items():
    print(f"- {pii_type}: {count} matches found")
print(f"\n✅ Done! PII scan complete. Results saved to '{output_file}'")
