import streamlit as st
import pandas as pd
import os

st.title("LEGO Part Image Viewer")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the CSV file
    lego = pd.read_csv(uploaded_file)
    
    # Display the DataFrame
    # Apply styling to highlight rows where PiecesPresent < Qty
    def highlight_missing(row):
        return ['background-color: yellow' if row["PiecesPresent"] < row["Qty"] else '' for _ in row]

    styled_lego = lego[["SetNumber","ElementID","Colour","ElementName","Qty","PiecesPresent"]].style.apply(highlight_missing, axis=1)
    
    # Display the styled DataFrame
    st.write(styled_lego)


    # Print total number of pieces in the set, along with how many are missing
    st.write(f"Total number of pieces: {lego['Qty'].sum()}")
    st.write(f"Number of pieces present: {lego['PiecesPresent'].sum()}")

    # Make ElementID the index
    lego.set_index("ElementID", inplace=True)
    
    # Create columns for input fields
    col1, col2, col3 = st.columns(3)

    # Input fields for each column in the selected row organized in a single row
    with col1:
        selected_index = st.selectbox("Select a part number to edit", options=lego.index)
        # Display the selected row data for editing
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
        
        # Display updated DataFrame
        st.write("Updated DataFrame:")
        st.dataframe(lego.style.apply(highlight_missing, axis=1))

    # Dialogue to navigate to the images folder
    image_folder = st.text_input("Image Folder Path", "images")
    # Get the image file path
    image_path = os.path.join(image_folder, f"{selected_index}.jpg")

    # Check if the image file exists
    if os.path.exists(image_path):
        # Display the image
        st.image(image_path, caption=f"LEGO Part Number: {selected_index}")
    else:
        st.write(f"No image found for part number: {selected_index}")

    # Display the image file path for debugging
    st.write(f"Image Path: {image_path}")
