import streamlit as st
import pdfplumber
import pandas as pd
import re
import io

st.set_page_config(page_title="Payables Duplicate Checker", layout="wide")
st.title("📄 Payables Duplicate Invoice Checker")

uploaded_file = st.file_uploader("Upload Payables PDF", type="pdf")

if uploaded_file:
    with st.spinner("Analyzing PDF..."):
        invoice_records = []
        current_carrier = None

        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                lines = text.split("\n")
                for line in lines:
                    if re.match(r"^[A-Z0-9].+ - [A-Z]$", line.strip()):
                        current_carrier = line.strip()

                    match = re.search(r"(\d{5,10}-\d{5,10}-\d+)", line)
                    if current_carrier and match:
                        full_invoice = match.group(1)
                        carrier_invoice = full_invoice.split("-")[0]
                        invoice_records.append({
                            "Carrier": current_carrier,
                            "FullInvoice": full_invoice,
                            "CarrierInvoice": carrier_invoice
                        })

        df = pd.DataFrame(invoice_records)
        duplicates = df[df.duplicated(subset=["Carrier", "CarrierInvoice"], keep=False)]

        if duplicates.empty:
            st.success("✅ No duplicate invoice numbers found.")
        else:
            st.error("❌ Duplicate Invoices Detected")
            st.dataframe(duplicates)

        if not df.empty:
            with st.expander("🔍 View All Extracted Invoices"):
                st.dataframe(df)
