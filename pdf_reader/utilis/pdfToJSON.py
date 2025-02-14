import pdfplumber
import json
import os
import fitz  # PyMuPDF


def extract_pdf_data(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        # Initialize text as empty string
        text = ""

        # Get text from all pages
        for page in pdf.pages:
            text += page.extract_text() + "\n"

        # Split text into lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Use PDF filename without extension as title
        title = os.path.splitext(os.path.basename(pdf_path))[0]

        # Initialize data structure as dictionary instead of array
        data = {}

        # Detect report type from filename
        report_type = title.split('_')[0].upper()

        # Process header information
        for line in lines:
            if "nome:" in line.lower():
                data["nome"] = line.replace("nome:", "").strip()
            elif "data:" in line.lower():
                data["data"] = line.replace("Data:", "").strip()

        # Initialize results dictionary
        results = {}

        if report_type == "COMPLEX":
            for line in lines:
                # Skip header lines and empty lines
                if not line.strip() or any(header in line.lower() for header in ["nome:", "data:", "nome risultati", "tellmegen"]):
                    continue

                # Look for disease and risk pattern
                if "Rischio" in line:
                    disease = line.split("Rischio")[0].strip()
                    risk = "Rischio" + line.split("Rischio")[1].strip()
                    if disease and risk:
                        results[disease] = risk
        elif report_type == "MONOGENIC":
            for line in lines:
                # Skip header lines and empty lines
                if not line.strip() or any(header in line.lower() for header in ["nome:", "data:", "nome risultati", "tellmegen"]):
                    continue

                # Look for disease and variant pattern
                if "Variante presente" in line or "Variante assente" in line:
                    if "Variante presente" in line:
                        disease = line.split("Variante presente")[0].strip()
                        if disease:  # Only add if disease name is not empty
                            results[disease] = "Variante presente"
                    else:
                        disease = line.split("Variante assente")[0].strip()
                        if disease:  # Only add if disease name is not empty
                            results[disease] = "Variante assente"
        elif report_type == "PHARMA":
            # Use PyMuPDF for PHARMA reports
            doc = fitz.open(pdf_path)
            current_item = {}

            for page in doc:
                text = page.get_text()
                # Split by newlines and clean up
                lines = [line.strip()
                         for line in text.split('\n') if line.strip()]

                for line in lines:
                    # Skip header lines
                    if any(header in line.lower() for header in ["nome:", "data:", "nome risultati", "tellmegen", "azione", "farmacologica", "risultati"]):
                        continue

                    # Check if line contains any of the known action types
                    action_types = ["Antidepressivi", "Antipsicotici", "Anestetici generali",
                                    "Colinergici", "Antiepiletico", "Chemioprofilassi"]

                    if any(action in line for action in action_types):
                        # This line contains the action
                        if current_item.get('nome'):  # Save previous item if exists
                            results[current_item['nome']] = {
                                "azione_farmacologica": current_item.get('azione_farmacologica', ''),
                                "risultati": current_item.get('risultati', '')
                            }
                        current_item = {'azione_farmacologica': line}
                    elif "(" in line and ")" in line:
                        # This is likely a drug name line
                        current_item = {'nome': line}
                    elif line and current_item.get('nome'):
                        # This must be the results line
                        current_item['risultati'] = line
                        # Save the complete item
                        results[current_item['nome']] = {
                            "azione_farmacologica": current_item.get('azione_farmacologica', ''),
                            "risultati": current_item['risultati']
                        }
                        current_item = {}

            # Save last item if exists
            if current_item.get('nome'):
                results[current_item['nome']] = {
                    "azione_farmacologica": current_item.get('azione_farmacologica', ''),
                    "risultati": current_item.get('risultati', '')
                }

            doc.close()
        elif report_type == "WELLNESS":
            for line in lines:
                if any(keyword in line for keyword in ["Livelli", "Capacità", "Probabilità", "Rischio"]):
                    parts = line.split(" ", 1)
                    if len(parts) == 2:
                        trait = parts[0].strip()
                        value = parts[1].strip()
                        results[trait] = value
        elif report_type == "TRAITS":
            for line in lines:
                if " " in line:
                    parts = line.rsplit(" ", 1)
                    if len(parts) == 2:
                        trait = parts[0].strip()
                        value = parts[1].strip()
                        results[trait] = value
        elif report_type == "ANCESTRY":
            for line in lines:
                if '%' in line or 'R1b' in line or 'H' in line:
                    parts = line.rsplit(None, 1)
                    if len(parts) == 2:
                        category = parts[0].strip()
                        value = parts[1].strip()
                        results[category] = value
                elif line.strip():
                    results[line.strip()] = ""

        # Add results to main data structure
        data["results"] = results

        return {
            "title": title,
            "data": data
        }


def process_pdfs_in_directory():
    # Process all PDF files in current directory
    for filename in os.listdir('.'):
        if filename.endswith('.pdf'):
            pdf_path = filename
            json_path = filename.replace('.pdf', '.json')

            try:
                # Extract data from PDF
                data = extract_pdf_data(pdf_path)

                # Save to JSON file
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                print(f"Successfully processed {filename} -> {json_path}")

            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")


if __name__ == "__main__":
    process_pdfs_in_directory()
