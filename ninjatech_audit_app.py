import streamlit as st
import platform
import socket
import subprocess
import datetime
from fpdf import FPDF
import os

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

def clean_temp_files():
    if platform.system() == "Windows":
        return subprocess.getoutput("del /q/f/s %TEMP%\*")
    else:
        return subprocess.getoutput("rm -rf /tmp/*")

def scan_sensitive_files():
    keywords = ["password", "secret", "credential", "ssn", "tax", "confidential"]
    found_files = []
    search_dir = os.path.expanduser("~")
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            try:
                if file.lower().endswith(('.txt', '.docx', '.pdf', '.csv')):
                    full_path = os.path.join(root, file)
                    with open(full_path, 'r', errors='ignore') as f:
                        contents = f.read().lower()
                        if any(keyword in contents for keyword in keywords):
                            found_files.append(full_path)
            except:
                continue
    return found_files

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

    pdf.section_title("Temporary Files Cleanup")
    cleanup_result = clean_temp_files()
    pdf.section_body("Temporary files cleanup completed.\n")

    pdf.section_title("Sensitive File Scan")
    sensitive_files = scan_sensitive_files()
    if sensitive_files:
        pdf.section_body("Potential sensitive files found:\n" + "\n".join(sensitive_files[:10]) + ("\n...and more" if len(sensitive_files) > 10 else ""))
    else:
        pdf.section_body("No sensitive files detected.")

    filename = f"digital_hygiene_audit_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(filename)
    return filename

st.title("Ninjatech Digital Hygiene Audit")
st.write("Click the button below to run the system audit, clean up temp files, scan for sensitive files, and download your PDF report.")

if st.button("Run Full Audit & Generate Report"):
    with st.spinner("Running full system audit and cleanup, generating report..."):
        report_file = generate_report()
        with open(report_file, "rb") as f:
            st.success("Audit completed! Download your report below:")
            st.download_button(
                label="📄 Download Report",
                data=f,
                file_name=report_file,
                mime="application/pdf"
            )

# Embedded link snippet for website HTML (copy into your main site)
embed_html = '''
<section id="audit-tool">
  <h2 class="section-title" data-aos="fade-up">Try Our Free Audit Tool</h2>
  <div class="cta-box" data-aos="zoom-in">
    <p>Run a full system health check, clean up junk files, and detect sensitive information instantly.</p>
    <a href="https://audit.ninjatech.io" target="_blank" class="button">Launch Audit App</a>
  </div>
</section>
'''

st.markdown("""---
### Embed This App Into Your Website
Copy this HTML snippet and paste it into your website:
""")
st.code(embed_html, language='html'
