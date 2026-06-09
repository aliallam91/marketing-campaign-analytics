import streamlit as st
import os

# Load custom CSS
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("d:/Depi Project/style.css")

# Excel Header Banner (Rounded Rectangle 14 + Graphics 16, 20, 22, 25)
st.markdown("""<div class="excel-header">
<h1 class="excel-header-title">Marketing Campaign Analytics</h1>
</div>""", unsafe_allow_html=True)

# Main container for cover and credits
col1, col2 = st.columns([7, 5])

with col1:
    st.markdown("<h3 style='color: #50164A; margin-bottom: 15px;'>Project Presentation Cover</h3>", unsafe_allow_html=True)
    intro_bg_path = "d:/Depi Project/assets/Intro_img_0.jpeg"
    if os.path.exists(intro_bg_path):
        st.image(intro_bg_path, width='stretch')
    else:
        st.info("Presentation graphic is loading...")

with col2:
    st.markdown("<h3 style='color: #50164A; margin-bottom: 15px;'>Project Credits</h3>", unsafe_allow_html=True)
    
    # Recreate Shape 7 (Rectangle 31: Credits text frame) and Shape 8, 9 (Stars)
    # Aligning every line to the left margin (0 leading spaces) to prevent markdown code block rendering
    st.markdown("""<div class="intro-container">
<div class="intro-meta-box">
<h4 style="color: #50164A; margin-bottom: 5px; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 0.05em;">
🎓 Supervisor
</h4>
<p style="font-size: 1.3rem; font-weight: 700; color: #1C355E; margin-bottom: 25px; padding-left: 5px;">
DR. Amal Mahmoud
</p>
<h4 style="color: #50164A; margin-bottom: 12px; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 0.05em;">
👥 Prepared By
</h4>
<div style="font-size: 1.15rem; line-height: 2.2; color: #2D3748; font-weight: 600; padding-left: 5px;">
<div style="display: flex; align-items: center; gap: 8px;">
<span style="color: #78206E; font-size: 1.2rem;">★</span> Ali Waleed Muhammad
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span style="color: #78206E; font-size: 1.2rem;">★</span> Carol Amir Maher
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span style="color: #78206E; font-size: 1.2rem;">★</span> Meriam Maged Zaki
</div>
<div style="display: flex; align-items: center; gap: 8px;">
<span style="color: #78206E; font-size: 1.2rem;">★</span> Martina Marco Dawood
</div>
</div>
</div>
<div style="margin-top: 30px; border-top: 1px dashed #B0CBE5; padding-top: 20px; text-align: center;">
</div>
</div>""", unsafe_allow_html=True)
