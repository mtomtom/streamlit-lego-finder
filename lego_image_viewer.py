import streamlit as st
import pandas as pd
import os
from PIL import Image

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
    lego = pd.read_csv(uploaded_file)

    # Display the DataFrame with highlighted missing pieces
    def highlight_missing(row):
        return ['background-color: yellow' if row["PiecesPresent"] < row["Qty"] else '' for _ in row]

    styled_lego = lego[["SetNumber","ElementID","Colour","ElementName","Qty","PiecesPresent"]].style.apply(highlight_missing, axis=1)
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

    # Button to save changes
    if st.button("Save Changes"):
        lego.at[selected_index, "Qty"] = new_qty
        lego.at[selected_index, "PiecesPresent"] = new_pieces_present
        st.write("Updated DataFrame:")
        st.dataframe(lego.style.apply(highlight_missing, axis=1))

    # Construct the image key from the selected part number
    image_key = selected_index  # selected_index is now a string

    # Check if the image file exists in the uploaded files
    if image_key in image_dict:
        # Open the image using PIL
        image = Image.open(image_dict[image_key])
        st.image(image, caption=f"LEGO Part Number: {image_key}")
    else:
        st.write(f"No image found for part number: {image_key}")

    # Display the image file path for debugging
    st.write(f"Image Key: {image_key}")  # For debugging purposes


