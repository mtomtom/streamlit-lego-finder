import streamlit as st
import pandas as pd
import os
from PIL import Image

# Initialize session state for DataFrame and current index
if 'lego' not in st.session_state:
    st.session_state.lego = None
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'selected_index' not in st.session_state:
    st.session_state.selected_index = None

st.title("LEGO Part Image Viewer")

# File uploader for CSV
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
# File uploader for images
uploaded_images = st.file_uploader("Upload Part Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Store images in a dictionary
image_dict = {}
if uploaded_images:
    for img_file in uploaded_images:
        # Use the image filename without extension as the key
        image_key = os.path.splitext(img_file.name)[0]
        image_dict[image_key] = img_file  # Store the uploaded file

# Read the uploaded CSV file and store it in session state
if uploaded_file is not None:
    st.session_state.lego = pd.read_csv(uploaded_file)
    st.session_state.lego["ElementID"] = st.session_state.lego["ElementID"].astype(str)  # Convert ElementID to string
    st.session_state.lego.set_index("ElementID", inplace=True)
    st.session_state.current_index = 0  # Reset index when new file is uploaded
    st.session_state.selected_index = st.session_state.lego.index[st.session_state.current_index]

def main():
    if st.session_state.lego is not None:
        lego = st.session_state.lego

        # Highlight missing pieces
        def highlight_missing(row):
            return ['background-color: yellow' if row["PiecesPresent"] < row["Qty"] else '' for _ in row]

        # Get the current index and selected row
        selected_index = st.session_state.selected_index
        if selected_index is not None:
            selected_row = lego.loc[selected_index]

            # Create columns for input fields
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"Editing part number: {selected_index}")

            with col2:
                new_qty = st.number_input("Qty", value=int(selected_row["Qty"]), min_value=0, key='qty_input')

            with col3:
                new_pieces_present = st.number_input("PiecesPresent", value=int(selected_row["PiecesPresent"]), min_value=0, key='pieces_present_input')

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
                    data=lego.to_csv(index=True),  # Convert DataFrame to CSV string
                    file_name='updated_lego_data.csv',
                    mime='text/csv'
                )

                st.success("Changes saved!")

            # Dropdown to select a specific part number
            selected_index_from_dropdown = st.selectbox("Jump to Part Number:", options=lego.index, index=st.session_state.current_index)
            if selected_index_from_dropdown != selected_index:
                st.session_state.selected_index = selected_index_from_dropdown
                st.session_state.current_index = lego.index.get_loc(selected_index_from_dropdown)
                st.experimental_rerun()  # Force a re-render

            # Buttons for navigation
            col_next, col_prev = st.columns([1, 1])
            with col_next:
                if st.button("Next Part"):
                    st.session_state.current_index = (st.session_state.current_index + 1) % len(lego.index)
                    st.session_state.selected_index = lego.index[st.session_state.current_index]
                    st.experimental_rerun()  # Force a re-render
            with col_prev:
                if st.button("Previous Part"):
                    st.session_state.current_index = (st.session_state.current_index - 1) % len(lego.index)
                    st.session_state.selected_index = lego.index[st.session_state.current_index]
                    st.experimental_rerun()  # Force a re-render

            st.write("Updated DataFrame:")
            styled_lego = lego.style.apply(highlight_missing, axis=1)
            st.dataframe(styled_lego)

            # Construct the image key from the selected part number
            image_key = selected_index

            # Display the corresponding image if available
            if image_key in image_dict:
                img_file = image_dict[image_key]
                image = Image.open(img_file)
                st.image(image, caption=f"LEGO Part Number: {image_key}")
            else:
                st.write(f"No image found for part number: {image_key}")

            # Debugging information
            st.write(f"Image Key: {image_key}")
        else:
            st.write("No part selected.")

if __name__ == "__main__":
    main()