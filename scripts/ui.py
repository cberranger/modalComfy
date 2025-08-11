"""Streamlit dashboard for managing ComfyUI on Modal."""

import streamlit as st
import modal


st.set_page_config(page_title="ComfyUI Modal Dashboard", layout="wide")

st.title("ComfyUI Modal Dashboard")
st.caption("Local interface for interacting with the Modal deployment of ComfyUI")

# Modal function handles
client = modal.Client()
putfile = modal.Function.lookup("comfyui-app", "putfile")
list_models_fn = modal.Function.lookup("comfyui-app", "list_models")
server_handle = modal.Function.lookup("comfyui-app", "ComfyUIServer.asgi_app")

tabs = st.tabs(["Server", "Models"])

with tabs[0]:
    st.subheader("ComfyUI Server")
    st.write("Open the web UI served from Modal.")
    if st.button("Open ComfyUI"):
        try:
            url = server_handle.web_url
            st.success("Server running")
            st.markdown(f"[Launch ComfyUI]({url})")
        except Exception as e:
            st.error(f"Could not retrieve server URL: {e}")
            st.info("Make sure the server is running via `modal serve app.py` or deployed.")

with tabs[1]:
    st.subheader("Model Management")
    allowed_dirs = ["unet", "lora", "text_encoders", "vae", "diffusion_models"]
    subdir = st.selectbox("Model subdirectory", allowed_dirs, index=2)

    try:
        files = list_models_fn.call(subdir)
    except Exception as e:
        files = []
        st.error(f"Unable to list models: {e}")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Existing files")
        if files:
            st.write(files)
        else:
            st.write("(no files found)")

    with col2:
        st.markdown("### Download new model")
        url = st.text_input("Model URL")
        filename = st.text_input("Filename")
        if st.button("Download") and url and filename:
            with st.spinner("Downloading..."):
                try:
                    putfile.call(url, filename, subdir)
                    st.success("Download complete")
                except Exception as e:
                    st.error(f"Failed to download: {e}")
