import streamlit as st
import pandas as pd
import os
from PIL import Image

# Initialize session state for the DataFrame if it doesn't exist
if 'lego' not in st.session_state:
    st.session_state.lego = None

st.title("LEGO Part Image Viewer")

# File uploader for CSV
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# File uploader for images
uploaded_images = st.file_uploader("Upload Part Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Store images in a dictionary
image_dict = {}
if uploaded_images is not None:
    for img_file in uploaded_images:
        # Use the image filename without extension as the key
        image_key = os.path.splitext(img_file.name)[0]  # Get the filename without extension
        image_dict[image_key] = img_file  # Store the uploaded file

if uploaded_file is not None:
    # Read the CSV file
    st.session_state.lego = pd.read_csv(uploaded_file)

if st.session_state.lego is not None:
    # Use the DataFrame stored in session state
    lego = st.session_state.lego

    # Display the DataFrame with highlighted missing pieces
    def highlight_missing(row):
        return ['background-color: yellow' if row["PiecesPresent"] < row["Qty"] else '' for _ in row]

    styled_lego = lego[["SetNumber", "ElementID", "Colour", "ElementName", "Qty", "PiecesPresent"]].style.apply(highlight_missing, axis=1)
    st.write(styled_lego)

    st.write(f"Total number of pieces: {lego['Qty'].sum()}")
    st.write(f"Number of pieces present: {lego['PiecesPresent'].sum()}")

    # Make ElementID the index and convert to string for matching with image names
    lego["ElementID"] = lego["ElementID"].astype(str)  # Convert ElementID to string
    lego.set_index("ElementID", inplace=True)
    
    # Create columns for input fields
    col1, col2, col3 = st.columns(3)

    with col1:
        selected_index = st.selectbox("Select a part number to edit", options=lego.index)
        selected_row = lego.loc[selected_index]
    
    with col2:
        new_qty = st.number_input("Qty", value=int(selected_row["Qty"]), min_value=0)
    
    with col3:
        new_pieces_present = st.number_input("PiecesPresent", value=int(selected_row["PiecesPresent"]), min_value=0)

    # Button to save changes incrementally
    if st.button("Save Changes"):
        lego.at[selected_index, "Qty"] = new_qty
        lego.at[selected_index, "PiecesPresent"] = new_pieces_present
        
        # Update the DataFrame in session state
        st.session_state.lego = lego.copy()  # Keep the updated DataFrame in session state

        st.write("Changes saved!")
        st.write("Updated DataFrame:")
        st.dataframe(lego.style.apply(highlight_missing, axis=1))

        # Save the updated DataFrame back to CSV
        output_file_name = "updated_lego_data.csv"  # Change this to the desired name if needed
        lego.to_csv(output_file_name, index=True)  # Save with index

        # Provide a download link for the updated CSV file
        st.download_button(
            label="Download Updated CSV",
            data=open(output_file_name, "rb").read(),
            file_name=output_file_name,
            mime="text/csv"
        )

    # Construct the image key from the selected part number
    image_key = selected_index  # selected_index is now a string

    if image_key in image_dict:
        # Directly read the uploaded file as an image
        img_file = image_dict[image_key]
        image = Image.open(img_file)  # Open the image directly from the uploaded file
        st.image(image, caption=f"LEGO Part Number: {image_key}")
    else:
        st.write(f"No image found for part number: {image_key}")

    # Display the image file path for debugging
    st.write(f"Image Key: {image_key}")  
# For debugging purposes


