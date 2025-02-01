import streamlit as st
import pandas as pd
from io import BytesIO

def run():
    st.header("EU SKU Validation")
    
    # EU-specific constants
    REQUIRED_ATTRIBUTES = [
        "Family Id", "Import Family Id", "US Hierarchy Category V2", "Material Bank SKU",
        "Material Url", "Product Type", "Configurable Color", "Primary Child", "Configurable Variation Labels",
        "Product Categories", "Product Websites", "Hide From Product View EU", "Visibility EU", "Batch Number",
        "Product Name", "Manufacturer Sku EU", "Color Name", "Color Number", "MBID", "Manufacturer", "Price Range",
        "Commercial & Residential", "Attribute Set Code", "Taxonomy Node", "California Prop 65", "Retired Sku",
        "Serial Sku", "Stealth SKU", "Indoor & Outdoor", "Set as New SKU", "Item Type", "Description", "Color Variety",
        "Color Saturation", "Primary Color Family", "Secondary Color Family", "Pattern", "Pattern Scale",
        "Metallic Color", "Stone Pattern", "Style", "Color Term", "Motif"
    ]
    
    NECESSARY_FIELDS = [
        "Commercial & Residential", "Color Name", "Color Number", "Price Range", 
        "Indoor & Outdoor", "CatalogItemID", "Product Name", "Set as New SKU", "Product Finish Type"
    ]

    def check_attributes_in_excel(df, required_attributes):
        """EU-specific attribute validation"""
        columns_in_sheet = df.columns.tolist()
        missing_attributes = [attr for attr in required_attributes if attr not in columns_in_sheet]
        
        if not missing_attributes:
            st.success("All required EU attributes are present.")
        else:
            st.error("Missing EU-specific attributes:")
            for attr in missing_attributes:
                st.write(f"- {attr}")

    def load_file(uploaded_file):
        """Load uploaded file into DataFrame"""
        try:
            if uploaded_file.name.endswith('.xlsx'):
                return pd.read_excel(uploaded_file, engine='openpyxl')
            elif uploaded_file.name.endswith('.csv'):
                return pd.read_csv(uploaded_file)
            else:
                st.error("Unsupported file type. Please upload .xlsx or .csv")
                return None
        except Exception as e:
            st.error(f"Error loading file: {e}")
            return None

    def review_field_values(main_df, sku_df, match_field, necessary_fields):
        """EU-specific field value comparison"""
        try:
            # Convert SKU fields to string
            main_df[match_field] = main_df[match_field].astype(str)
            sku_df[match_field] = sku_df[match_field].astype(str)

            # SKU comparisons
            main_skus = set(main_df[match_field])
            sku_skus = set(sku_df[match_field])

            with st.expander("EU SKU Comparison Results"):
                # Check mismatches
                missing_in_main = sku_skus - main_skus
                if missing_in_main:
                    st.warning("EU SKUs missing in main file:")
                    st.write(list(missing_in_main))

                extra_in_main = main_skus - sku_skus
                if extra_in_main:
                    st.warning("Extra EU SKUs in main file:")
                    st.write(list(extra_in_main))

            # Merge dataframes
            merged_df = pd.merge(main_df, sku_df, on=match_field, suffixes=("_ImportFile", "_SkuList"))

            # Field comparisons
            mismatches = []
            for field in necessary_fields:
                col_main = f"{field}_ImportFile"
                col_sku = f"{field}_SkuList"
                
                if col_main in merged_df.columns and col_sku in merged_df.columns:
                    mismatch = merged_df[merged_df[col_main] != merged_df[col_sku]]
                    if not mismatch.empty:
                        mismatches.append((field, mismatch))

            # Display results
            if not mismatches:
                st.success("All EU fields match between files!")
            else:
                st.error("EU field mismatches detected:")
                for field, df in mismatches:
                    with st.expander(f"Mismatches in {field}"):
                        st.dataframe(df[[match_field, col_main, col_sku]])

        except Exception as e:
            st.error(f"EU comparison error: {str(e)}")

    # Streamlit UI Components
    st.subheader("File Uploads")
    st.markdown("Before uploading files, make sure the necessary Field Names for review, matches in both files")
    
    # File uploaders
    main_file = st.file_uploader("EU Import File (Excel/CSV)", type=["xlsx", "csv"], key="eu_main")
    sku_file = st.file_uploader("EU SKU List File (Excel/CSV)", type=["xlsx", "csv"], key="eu_sku")

    if main_file and sku_file:
        st.subheader("EU Validation Results")
        
        # Load files
        with st.spinner("Processing EU files..."):
            main_df = load_file(main_file)
            sku_df = load_file(sku_file)

        if main_df is not None and sku_df is not None:
            # Attribute check
            st.write("### EU Required Attributes Check")
            check_attributes_in_excel(main_df, REQUIRED_ATTRIBUTES)

            # Field comparison
            st.write("### EU Field Value Comparison")
            review_field_values(main_df, sku_df, "Manufacturer Sku EU", NECESSARY_FIELDS)