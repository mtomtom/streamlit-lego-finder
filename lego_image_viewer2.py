import streamlit as st
import pandas as pd
import os
from PIL import Image, UnidentifiedImageError

# Load the broken link image
broken_link_image_path = "sadface.png"  # Specify your broken link image path
broken_link_image = Image.open(broken_link_image_path)  # Load the broken link image once

st.title("LEGO Part Image Viewer")

# File uploader for CSV
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
# File uploader for images
uploaded_images = st.file_uploader("Upload Part Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Store images in a dictionary
image_dict = {}
if uploaded_images is not None:
    for img_file in uploaded_images:
        image_key = os.path.splitext(img_file.name)[0]  # Get the filename without extension
        try:
            # Open the image directly from the uploaded file
            image_data = Image.open(img_file)
            image_dict[image_key] = image_data  # Store the image object directly
        except UnidentifiedImageError:
            # Store the broken link image if there's an error
            #st.warning(f"Cannot identify image file {img_file.name}. Using a placeholder image.")
            image_dict[image_key] = broken_link_image

# Read the uploaded CSV file and store it in session state
if uploaded_file is not None:
    lego = pd.read_csv(uploaded_file)

    # Highlight missing pieces
    def highlight_missing(row):
        return ['background-color: yellow' if row["PiecesPresent"] < row["Qty"] else '' for _ in row]

    # Convert ElementID to string for matching with image names
    lego["ElementID"] = lego["ElementID"].astype(str)
    lego.set_index("ElementID", inplace=True)

    # Display the total number of parts and the number found so far
    st.write(f"Total number of parts: {lego['Qty'].sum()}")
    st.write(f"Number of parts found: {lego['PiecesPresent'].sum()}")

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
        # Update the DataFrame
        lego.at[selected_index, "Qty"] = new_qty
        lego.at[selected_index, "PiecesPresent"] = new_pieces_present

        # Save the updated DataFrame to CSV
        output_file_name = "updated_lego_data.csv"
        lego.to_csv(output_file_name, index=True)

        # Provide the updated CSV for download
        st.download_button(
            label="Download Updated Data",
            data=lego.to_csv(index=True),
            file_name='updated_lego_data.csv',
            mime='text/csv'
        )

        st.success("Changes saved!")

    st.write("Inventory (Incomplete entries highlighted):")
    styled_lego = lego[["ElementName", "Colour", "Qty", "PiecesPresent"]].style.apply(highlight_missing, axis=1)
    st.dataframe(styled_lego)

    # Display all images where not all pieces have been found
    missing_images = [(index, row) for index, row in lego.iterrows() if row['PiecesPresent'] < row['Qty']]

    if missing_images:
        num_columns = 5  # Number of columns for the grid
        cols = st.columns(num_columns)  # Create columns for the grid

        for idx, (image_key, row) in enumerate(missing_images):
            col_idx = idx % num_columns  # Determine the current column index
            with cols[col_idx]:  # Display in the corresponding column
                # Display the corresponding image
                image = image_dict.get(image_key, broken_link_image)  # Use broken link if not found
                st.image(image, caption=f"LEGO Part Number: {image_key} - Missing: {row['Qty'] - row['PiecesPresent']}, Colour: {row['Colour']}", width=100)  # Set width for smaller images

    else:
        st.write("All pieces have been found!")

    # Debugging information
    st.write("Image Dictionary Keys:", list(image_dict.keys()))  # Display keys for debugging

