import os
import re
import json
import uuid
import logging
from pathlib import Path

try:
    import pandas as pd
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from fpdf import FPDF
except ImportError:
    pass

logger = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

def process_dynamic_files(llm_response: str, host_url: str) -> str:
    """
    Parses LLM response for `<GENERATE_XXX>` tags, creates the files, 
    and replaces tags with markdown links.
    """
    
    # 1. Process CSV
    csv_pattern = re.compile(r"<GENERATE_CSV>(.*?)</GENERATE_CSV>", re.DOTALL | re.IGNORECASE)
    for match in csv_pattern.finditer(llm_response):
        raw_csv = match.group(1).strip()
        filename = f"generated_data_{uuid.uuid4().hex[:6]}.csv"
        file_path = STATIC_DIR / filename
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(raw_csv)
            url = f"{host_url}/static/{filename}"
            link_md = f"\n\n**[📥 Download Generated CSV Data File]({url})**\n\n"
            llm_response = llm_response.replace(match.group(0), link_md)
        except Exception as e:
            logger.error("Failed to generate CSV: %s", e)
            llm_response = llm_response.replace(match.group(0), "\n\n*(Failed to generate CSV)*\n\n")

    # 2. Process Chart
    chart_pattern = re.compile(r"<GENERATE_CHART>(.*?)</GENERATE_CHART>", re.DOTALL | re.IGNORECASE)
    for match in chart_pattern.finditer(llm_response):
        raw_json = match.group(1).strip()
        filename = f"generated_chart_{uuid.uuid4().hex[:6]}.jpg"
        file_path = STATIC_DIR / filename
        try:
            # Groq might add markdown code blocks inside the tag
            raw_json = raw_json.replace("```json", "").replace("```", "").strip()
            data = json.loads(raw_json)
            plt.figure(figsize=(8, 5))
            
            if "series" in data:
                for s in data["series"]:
                    plt.plot(s.get("x", []), s.get("y", []), marker='o', label=s.get("name", "Data"))
            else:
                plt.plot(data.get("x", []), data.get("y", []), marker='o')
                
            plt.title(data.get("title", "Generated Chart"))
            plt.xlabel(data.get("x_label", ""))
            plt.ylabel(data.get("y_label", ""))
            if "series" in data and len(data["series"]) > 0:
                plt.legend()
                
            plt.tight_layout()
            plt.savefig(file_path)
            plt.close()
            
            url = f"{host_url}/static/{filename}"
            img_md = f"\n\n![Generated Chart]({url})\n\n"
            llm_response = llm_response.replace(match.group(0), img_md)
        except Exception as e:
            logger.error("Failed to generate chart: %s", e)
            llm_response = llm_response.replace(match.group(0), "\n\n*(Failed to generate Chart. Ensure the AI provided valid JSON data)*\n\n")

    # 3. Process PDF
    pdf_pattern = re.compile(r"<GENERATE_PDF>(.*?)</GENERATE_PDF>", re.DOTALL | re.IGNORECASE)
    for match in pdf_pattern.finditer(llm_response):
        raw_text = match.group(1).strip()
        filename = f"generated_report_{uuid.uuid4().hex[:6]}.pdf"
        file_path = STATIC_DIR / filename
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=11)
            # Remove Markdown boldness since FPDF doesn't natively parse MD strings easily
            clean_text = raw_text.replace("**", "").replace("*", "")
            pdf.multi_cell(0, 7, txt=clean_text.encode('latin-1', 'replace').decode('latin-1'))
            pdf.output(str(file_path))
            
            url = f"{host_url}/static/{filename}"
            link_md = f"\n\n**[📄 Download Official Generated PDF Report]({url})**\n\n"
            llm_response = llm_response.replace(match.group(0), link_md)
        except Exception as e:
            logger.error("Failed to generate PDF: %s", e)
            llm_response = llm_response.replace(match.group(0), "\n\n*(Failed to generate PDF)*\n\n")

    return llm_response
