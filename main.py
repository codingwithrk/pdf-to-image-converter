import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image
import io

st.set_page_config(page_title='RK PDF to Image Converter', page_icon='./favicon.png')

# Title of the Streamlit app
st.title('PDF to Image Converter')

# Upload a PDF file
uploaded_pdf = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_pdf is not None:
    # Load the uploaded PDF into a PyPDF2 PdfReader
    reader = PdfReader(uploaded_pdf)

    # Display the number of pages
    st.write(f"Number of pages: {len(reader.pages)}")

    # Convert the uploaded PDF to images
    with st.spinner("Converting PDF to images..."):
        # Save the uploaded PDF to a temporary file
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_pdf.getbuffer())

        # Convert PDF pages to images
        images = convert_from_path("temp.pdf", dpi=200)

        # Display each page as an image
        for i, image in enumerate(images):
            st.image(image, caption=f"Page {i + 1}", use_column_width=True)

        # Option to download the image as PNG
        if st.button("Download Image(s) as PNG"):
            for i, image in enumerate(images):
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='PNG')
                img_bytes = img_buffer.getvalue()
                st.download_button(label=f"Download Page {i + 1}",
                                   data=img_bytes,
                                   file_name=f"page_{i + 1}.png",
                                   mime="image/png")


# Footer
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 10px;
        color: #f1f1f1;
        border-top: 1px solid #e1e1e1;
        font-size: 12px;
    }
    a {
        text-decoration: none;
        color: #f1f1f1 !important;
    }
    </style>
    <div class="footer">
        Developed By ❤️ <a href="https://codingwithrk.com/" target="_blank">CodingwithRK</a>
    </div>
    """,
    unsafe_allow_html=True
)