import streamlit as st
import sqlite3
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
from PIL import Image
import io


# Database connection
def init_db():
    conn = sqlite3.connect('pdf_store.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pdf_data (
            id INTEGER PRIMARY KEY,
            file_name TEXT,
            file_data BLOB
        )
    ''')
    conn.commit()
    return conn


# Function to store PDF in SQLite
def store_pdf_in_db(conn, file_name, file_data):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO pdf_data (file_name, file_data) VALUES (?, ?)', (file_name, file_data))
    conn.commit()


# Function to retrieve PDF from SQLite
def retrieve_pdf_from_db(conn, pdf_id):
    cursor = conn.cursor()
    cursor.execute('SELECT file_data FROM pdf_data WHERE id=?', (pdf_id,))
    result = cursor.fetchone()
    return result[0] if result else None


# Function to delete PDF from SQLite
def delete_pdf_from_db(conn, pdf_id):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM pdf_data WHERE id=?', (pdf_id,))
    conn.commit()


# Initialize SQLite database
conn = init_db()

# Set page title, favicon, and layout
st.set_page_config(page_title='RK PDF to Image Converter', page_icon='./favicon.png', layout='wide')

# Title of the Streamlit app
st.title('PDF to Image Converter')

# Upload a PDF file
uploaded_pdf = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_pdf is not None:
    # Store uploaded PDF in SQLite as BLOB
    store_pdf_in_db(conn, uploaded_pdf.name, uploaded_pdf.getvalue())

    # Get the last inserted PDF ID
    pdf_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]

    # Retrieve PDF from database as binary data
    pdf_data = retrieve_pdf_from_db(conn, pdf_id)

    if pdf_data is not None:
        # Load the PDF from memory (BytesIO) directly
        reader = PdfReader(io.BytesIO(pdf_data))

        # Display the number of pages
        st.write(f"Number of pages: {len(reader.pages)}")

        # Convert PDF bytes to images directly from memory
        with st.spinner("Converting PDF to images..."):
            try:
                # Convert PDF to images using pdf2image's convert_from_bytes function
                images = convert_from_bytes(pdf_data, dpi=200)

                # Display each page as an image
                for i, image in enumerate(images):
                    st.image(image, caption=f"Page {i + 1}", use_column_width=True)

                # Option to download each image as PNG
                if st.button("Download Image(s) as PNG"):
                    for i, image in enumerate(images):
                        img_buffer = io.BytesIO()
                        image.save(img_buffer, format='PNG')
                        img_bytes = img_buffer.getvalue()
                        st.download_button(label=f"Download Page {i + 1}",
                                           data=img_bytes,
                                           file_name=f"page_{i + 1}.png",
                                           mime="image/png")

                    # After download, delete the PDF from the SQLite database
                    delete_pdf_from_db(conn, pdf_id)
            except Exception as e:
                st.error(f"An error occurred during conversion: {e}")
    else:
        st.error("Error retrieving PDF from the database.")

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
        background-color: #1e1e1e;
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
