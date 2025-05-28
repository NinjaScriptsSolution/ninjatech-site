import streamlit as st
import platform
import socket
import subprocess
import datetime
from fpdf import FPDF

class ReportPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Ninjatech Solutions - Digital Hygiene Audit Report", ln=True, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title):
        self.set_font("Arial", "B", 12)
        self.ln(10)
        self.cell(0, 10, title, ln=True)

    def section_body(self, body):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 10, body)

def get_hostname():
    return socket.gethostname()

def check_firewall():
    if platform.system() == "Windows":
        output = subprocess.getoutput("netsh advfirewall show allprofiles")
        return "ON" in output
    else:
        return subprocess.getoutput("sudo ufw status")

def check_updates():
    if platform.system() == "Windows":
        return "Check Windows Update manually"
    else:
        return subprocess.getoutput("sudo apt list --upgradable")

def check_users():
    if platform.system() == "Windows":
        return subprocess.getoutput("net user")
    else:
        return subprocess.getoutput("cut -d: -f1 /etc/passwd")

def scan_open_ports():
    import socket
    common_ports = [22, 80, 443, 3389]
    results = {}
    for port in common_ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(("127.0.0.1", port))
            results[port] = (result == 0)
    return results

def generate_report():
    pdf = ReportPDF()
    pdf.add_page()

    pdf.section_title("System Information")
    pdf.section_body(f"Hostname: {get_hostname()}")
    pdf.section_body(f"Platform: {platform.system()} {platform.release()}")

    pdf.section_title("Firewall Status")
    pdf.section_body(str(check_firewall()))

    pdf.section_title("Available Updates")
    pdf.section_body(str(check_updates()))

    pdf.section_title("User Accounts")
    pdf.section_body(str(check_users()))

    pdf.section_title("Open Ports")
    ports = scan_open_ports()
    port_summary = "\n".join([f"Port {port}: {'OPEN' if status else 'CLOSED'}" for port, status in ports.items()])
    pdf.section_body(port_summary)

    filename = f"digital_hygiene_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

st.title("Ninjatech Digital Hygiene Audit")
st.write("Click the button below to run the system audit and download your PDF report.")

if st.button("Run Audit & Generate Report"):
    with st.spinner("Running audit and generating report..."):
        report_file = generate_report()
        with open(report_file, "rb") as f:
            st.success("Audit completed! Download your report below:")
            st.download_button(
                label="📄 Download Report",
                data=f,
                file_name=report_file,
                mime="application/pdf"
            )