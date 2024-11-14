import xml.etree.ElementTree as ET
import csv
from collections import defaultdict
import re
import os

# File paths for morphology and book map
morph_file_path = "Oshm.xml"
bookMap = {
    "Genesis": "Gen.xml",
    "Exodus": "Exod.xml",
    "Leviticus": "Lev.xml",
    "Numbers": "Num.xml",
    "Deuteronomy": "Deut.xml",
    "Joshua": "Josh.xml",
    "Judges": "Judg.xml",
    "1 Samuel": "1Sam.xml",
    "2 Samuel": "2Sam.xml",
    "1 Kings": "1Kgs.xml",
    "2 Kings": "2Kgs.xml",
    "Isaiah": "Isa.xml",
    "Jeremiah": "Jer.xml",
    "Ezekiel": "Ezek.xml",
    "Hosea": "Hos.xml",
    "Joel": "Joel.xml",
    "Amos": "Amos.xml",
    "Obadiah": "Obad.xml",
    "Jonah": "Jonah.xml",
    "Micah": "Mic.xml",
    "Nahum": "Nah.xml",
    "Habakkuk": "Hab.xml",
    "Zephaniah": "Zeph.xml",
    "Haggai": "Hag.xml",
    "Zechariah": "Zech.xml",
    "Malachi": "Mal.xml",
    "Psalms": "Ps.xml",
    "Proverbs": "Prov.xml",
    "Job": "Job.xml",
    "Song of Songs": "Song.xml",
    "Ruth": "Ruth.xml",
    "Lamentations": "Lam.xml",
    "Ecclesiastes": "Eccl.xml",
    "Esther": "Esth.xml",
    "Daniel": "Dan.xml",
    "Ezra": "Ezra.xml",
    "Nehemiah": "Neh.xml",
    "1 Chronicles": "1Chr.xml",
    "2 Chronicles": "2Chr.xml"
}

# Data structures for morphology descriptions and lemma frequency
morphology_descriptions = {}
lemma_counts = defaultdict(int)
lemma_number_counts = defaultdict(int)
verse_data = []

# Define the namespace for Oshm.xml
morph_namespaces = {'tei': 'http://www.crosswire.org/2008/TEIOSIS/namespace'}

# Load morphology descriptions with comprehensive logging
def load_morphology_descriptions(file_path):
    print(f"Loading morphology descriptions from {file_path}")
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        entries = root.findall(".//tei:entryFree", morph_namespaces)
        
        for entry in entries:
            code = entry.get("n")
            description = entry.text.strip() if entry.text else "No description"
            morphology_descriptions[code] = description
            print(f"[MORPHOLOGY] Loaded entry '{code}' with description '{description}'")
        
        print(f"Total morphology descriptions loaded: {len(morphology_descriptions)}")
    except ET.ParseError as e:
        print(f"[ERROR] Failed to parse {file_path}: {e}")

# Parse the morphology using the descriptions
def parse_morphology(morph_code):
    if morph_code in morphology_descriptions:
        return {morph_code: morphology_descriptions[morph_code]}
    print(f"[INFO] Morph code '{morph_code}' not found in morphology descriptions.")
    return {morph_code: "Unknown"}

# Extract lemma number from lemma text
def extract_lemma_number(lemma):
    match = re.search(r'(\d+)', lemma)
    return match.group(1) if match else "No number found"

# Load verses with detailed logging
def load_verses(file_path, book_name):
    print(f"Loading verses from {file_path} for book '{book_name}'")
    global gen_namespaces
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Detect and set namespace if present
        gen_namespace = root.tag.split("}")[0].strip("{")
        gen_namespaces = {'ns': gen_namespace} if gen_namespace.startswith("http") else {}

        book_count = chapter_count = verse_count = 0
        
        # Adjusting the path to include namespace if present
        book_path = ".//ns:div[@type='book']" if gen_namespaces else ".//div[@type='book']"
        
        for book in root.findall(book_path, gen_namespaces):
            book_id = book.get("osisID")
            book_count += 1
            print(f"[BOOK] Processing book '{book_id}'")
            
            chapter_path = ".//ns:chapter" if gen_namespaces else ".//chapter"
            for chapter in book.findall(chapter_path, gen_namespaces):
                chapter_id = chapter.get("osisID")
                chapter_count += 1
                print(f"  [CHAPTER] Processing chapter '{chapter_id}'")
                
                verse_path = ".//ns:verse" if gen_namespaces else ".//verse"
                for verse in chapter.findall(verse_path, gen_namespaces):
                    verse_id = verse.get("osisID")
                    words_in_verse = []
                    verse_count += 1
                    print(f"    [VERSE] Processing verse '{verse_id}'")
                    
                    word_path = ".//ns:w" if gen_namespaces else ".//w"
                    for word in verse.findall(word_path, gen_namespaces):
                        lemma = word.get("lemma")
                        morph = word.get("morph")
                        word_text = word.text or ""
                        lemma_number = extract_lemma_number(lemma)
                        
                        # Update counts for both lemma and lemma number
                        lemma_counts[lemma] += 1
                        lemma_number_counts[lemma_number] += 1
                        
                        morph_details = parse_morphology(morph)
                        
                        word_data = {
                            "word_text": word_text,
                            "lemma": lemma,
                            "lemma_number": lemma_number,
                            "raw_morph": morph,
                            "parsed_morph": morph_details
                        }
                        words_in_verse.append(word_data)
                        print(f"      [WORD] Lemma: '{lemma}', Lemma Number: '{lemma_number}', Morph: '{morph}', Text: '{word_text}', Parsed Morph: {morph_details}")
                    
                    verse_data.append({"verse_id": verse_id, "words": words_in_verse})
        
        print(f"Total Books Processed: {book_count}, Chapters Processed: {chapter_count}, Verses Processed: {verse_count}")
    except ET.ParseError as e:
        print(f"[ERROR] Failed to parse {file_path}: {e}")

# Load morphology descriptions from Oshm.xml
load_morphology_descriptions(morph_file_path)

# Iterate over all books in bookMap and load each XML file
for book_name, file_name in bookMap.items():
    load_verses(file_name, book_name)

# Write verse morphology to CSV with additional Lemma Number column and hapax information
csv_columns = ["Verse ID", "Lemma", "Lemma Number", "Word Text", "Raw Morph", "Parsed Morph", "Lemma Hapax", "Lemma Number Hapax"]
with open("verse_morphology.csv", "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()
    for verse in verse_data:
        for word in verse["words"]:
            # Check if lemma and lemma number are hapax
            lemma_hapax = "Yes" if lemma_counts[word["lemma"]] == 1 else "No"
            lemma_number_hapax = "Yes" if lemma_number_counts[word["lemma_number"]] == 1 else "No"
            
            writer.writerow({
                "Verse ID": verse["verse_id"],
                "Lemma": word["lemma"],
                "Lemma Number": word["lemma_number"],
                "Word Text": word["word_text"],
                "Raw Morph": word["raw_morph"],
                "Parsed Morph": word["parsed_morph"],
                "Lemma Hapax": lemma_hapax,
                "Lemma Number Hapax": lemma_number_hapax
            })
    print("Verse morphology CSV created successfully with hapax data.")

print("Script completed.")