import streamlit as st
import pandas as pd
from io import BytesIO

""" Code structure:

Streamlit UI Setup**: The `run()` function initializes the UI, defines constants, and handles file uploads.

File Loading**: The `load_file` function reads Excel or CSV files.

Attribute Check**: `check_attributes_in_excel` verifies if all required columns are present.

Field Comparison**: `review_field_values` merges dataframes, checks for mismatches, and handles configurable products appropriately.

Handling Configurable Products**: The logic skips CatalogItemID validation for configurable products by filtering those rows during comparison. """

def run():
    st.header("US SKU Validation")
    
    # Define constants
    REQUIRED_ATTRIBUTES = [
        "CatalogItemID", "Family Id", "Import Family Id", "US Hierarchy Category V2", "Material Bank SKU",
        "Material Url", "Product Type", "Configurable Color", "Primary Child", "Configurable Variation Labels",
        "Product Categories", "Product Websites", "Hide From Product View", "Visibility", "Batch Number",
        "Product Name", "Manufacturer Sku", "Color Name", "Color Number", "MBID", "Manufacturer", "Price Range",
        "Commercial & Residential", "Attribute Set Code", "Taxonomy Node", "California Prop 65", "Retired Sku",
        "Serial Sku", "Stealth SKU", "Indoor & Outdoor", "Set as New SKU", "Item Type", "Description", "Color Variety",
        "Color Saturation", "Primary Color Family", "Secondary Color Family", "Pattern", "Pattern Scale",
        "Metallic Color", "Stone Pattern", "Style", "Color Term", "Motif"
    ]
    
    NECESSARY_FIELDS = [
        "Commercial & Residential", "Color Name", "Color Number", "Price Range", 
        "California Prop 65", "Indoor & Outdoor", "CatalogItemID", "Product Name", 
        "Set as New SKU"
    ]

    def check_attributes_in_excel(df, required_attributes):
        """Check for missing attributes in the uploaded file"""
        columns_in_sheet = df.columns.tolist()
        missing_attributes = [attr for attr in required_attributes if attr not in columns_in_sheet]
        
        if not missing_attributes:
            st.success("All required attributes are present in the sheet.")
        else:
            st.error("Missing attributes detected:")
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
        """Compare values between Import file and SKU list"""
        try:
            # Convert matching field to string type
            main_df[match_field] = main_df[match_field].astype(str)
            sku_df[match_field] = sku_df[match_field].astype(str)

            
            # Identify configurable rows but keep CatalogItemID in necessary_fields
            configurable_mask = None
            if 'Product Type' in main_df.columns:
             configurable_mask = main_df['Product Type'].str.lower() == 'configurable'


            # SKU comparisons
            main_skus = set(main_df[match_field])
            sku_skus = set(sku_df[match_field])

            with st.expander("SKU Comparison Results"):
                # Check missing SKUs in Import file
                missing_in_main = sku_skus - main_skus
                if missing_in_main:
                    st.warning("SKUs missing in the Import file:")
                    st.write(list(missing_in_main))

                # Check extra SKUs in Import file
                extra_in_main = main_skus - sku_skus
                if extra_in_main:
                    st.warning("Extra SKUs in the Import file:")
                    st.write(list(extra_in_main))

            # Merge dataframes
            merged_df = pd.merge(main_df, sku_df, on=match_field, suffixes=("_ImportFile", "_SkuList"))
            
            # Force string type for CatalogItemID comparison
            if 'CatalogItemID_ImportFile' in merged_df.columns:
             merged_df['CatalogItemID_ImportFile'] = merged_df['CatalogItemID_ImportFile'].astype(str)
            if 'CatalogItemID_SkuList' in merged_df.columns:
             merged_df['CatalogItemID_SkuList'] = merged_df['CatalogItemID_SkuList'].astype(str)

            mismatches = []
            for field in necessary_fields:
             col_main = f"{field}_ImportFile"
             col_sku = f"{field}_SkuList"
            
             if col_main in merged_df.columns and col_sku in merged_df.columns:
                 # Handle CatalogItemID specially for configurable products
                if field == 'CatalogItemID' and configurable_mask is not None:
                    # Only validate NON-configurable rows for CatalogItemID
                    temp_df = merged_df[~configurable_mask.reindex(merged_df.index, fill_value=False)]
                else:
                    temp_df = merged_df
                
                # Find mismatches
                mismatch = temp_df[temp_df[col_main] != temp_df[col_sku]]
                
                # mismatch = merged_df[merged_df[col_main] != merged_df[col_sku]]
                if not mismatch.empty:
                    # Store field-specific columns
                    mismatches.append((
                        field, 
                        mismatch[[match_field, col_main, col_sku]]
                    ))

            # Display results
            if not mismatches:
             st.success("All necessary fields match between files!")
            else:
             st.error("Field mismatches detected:")
             for field, mismatch_df in mismatches:
                with st.expander(f"Mismatches in {field}"): 
                    st.write(f"Comparison between Import File and SKU List for {field}")
                    st.dataframe(mismatch_df)

        except Exception as e:
            st.error(f"Comparison error: {str(e)}")

    # Streamlit UI Components
    st.subheader("File Uploads")
    
    with st.expander("📋 **Upload Instructions (Click to Expand)**", expanded=True):
        st.markdown("""
        ### Essential Checks Before Uploading:
        
        🔍 **Field Name Consistency**  
        Ensure these fields match **exactly** in both files:
        """)
        
        # Column layout for field list
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            - Commercial & Residential
            - Color Name
            - Color Number
            - Price Range
            - California Prop 65
            """)
        
        with col2:
            st.markdown("""
            - Indoor & Outdoor
            - CatalogItemID
            - Product Name
            - Set as New SKU
            """)
        
        st.markdown("""
        ### Field Renaming Guide
        ⚠️ **Important:** If your SKU List contains these columns, rename them:
        """)
        
        # Renaming table
        st.markdown("""
        | Original Name | Rename To |
        |---------------|-----------|
        | Updated Product Name | Product Name |
        | Updated Color Name | Color Name |
        | Updated Manufacturer Sku | Manufacturer Sku |
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.caption("💡 Tip: Use Excel's 'Find & Replace' to standardize column names before uploading")
    
    # File uploaders
    main_file = st.file_uploader("Upload the Import File (Excel/CSV)", type=["xlsx", "csv"])
    sku_file = st.file_uploader("Upload the SKU List File (Excel/CSV)", type=["xlsx", "csv"])

    if main_file and sku_file:
        st.subheader("Validation Results")
        
        # Load files
        with st.spinner("Loading files..."):
            main_df = load_file(main_file)
            sku_df = load_file(sku_file)

        if main_df is not None and sku_df is not None:
            # Attribute check
            st.write("### Required Attributes Check")
            check_attributes_in_excel(main_df, REQUIRED_ATTRIBUTES)

            # Field comparison
            st.write("### Field Value Comparison")
            review_field_values(main_df, sku_df, "Manufacturer Sku", NECESSARY_FIELDS)