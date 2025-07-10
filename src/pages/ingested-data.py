# Basic streamlit page

import streamlit as st

st.title("Ingested Data")

st.write(
    """
    The historic CDD documents are critical for the success of the project and are yet to be provided.

    The files that are to be used as context for the CDD agent need to be normalized and converted to markdown because Excel (or PowerPoint, or whatever) is not a friendly format for AI to work with.

    The data I used for this demo is just a basic sample. A real-world example of such documents is yet to be provided and will most likely contain more contextual data, rules, and constraints that need to be followed when building the document.
    """
)

# Print the text as markdown
st.markdown(
    """
## Source ERP Table

| ERP Name | Column Name   | Data Type   | Required | Description                     | Sample Data        |
|:---------|:-------------|:------------|:---------|:--------------------------------|:-------------------|
| Alpha    | CustomerID   | INT         | YES      | Unique numeric customer ID      | 12345              |
| Alpha    | SupplierName | VARCHAR(30) | YES      | Name of the supplier            | Contoso Inc.       |
| Alpha    | FirstName    | VARCHAR(30) | NO       | Contact person's first name     | John               |
| Alpha    | LastName     | VARCHAR(30) | NO       | Contact person's last name      | Smith              |
| Alpha    | Email        | VARCHAR(50) | YES      | Contact email address           | John@Contoso.com   |
| Alpha    | Phone        | VARCHAR(20) | NO       | Contact phone (varied formats)  | (206) 555-1234     |
"""
)

st.markdown("""
## Target ERP Table

| ERP System   | Column Name   | Data Type   | Required   | Business Rule / Constraint                                                | Sample Data         |
|:-------------|:--------------|:------------|:-----------|:--------------------------------------------------------------------------|:--------------------|
| Beta         | AccountNumber | VARCHAR(20) | YES        | Must start with CUST- followed by numeric ID; total length <= 20          | CUST-12345          |
| nan          | Supplier      | VARCHAR(40) | YES        | Supplier's name                                                           | Contoso Inc.        |
| nan          | ContactName   | VARCHAR(60) | NO         | The name of the person to contact                                         | Steve Smith         |
| nan          | ContactEmail  | VARCHAR(60) | YES        | Email of the person to contact, must be lowercase                         | steve.smith@xyz.com |
| nan          | ContactPhone  | VARCHAR(25) | NO         | Phone of the person to contact, using E.164 standard (e.g., +12065551234) | +12065551234        |
""")
