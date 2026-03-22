import streamlit as st
from yt_dlp import YoutubeDL
import os

st.set_page_config(page_title="Pro Media Downloader", layout="wide")

st.title("⚡ Super-Fast Media Downloader")
st.markdown("Download and Trim instantly without downloading the full video!")

mode = st.radio("Mode Select Karein:", ["Single Video (Preview & Trim)", "Batch Download (Multiple Links)"])

# ---------------- SINGLE VIDEO MODE ----------------
if mode == "Single Video (Preview & Trim)":
    url = st.text_input("Link Paste Karein:")
    
    if url:
        st.subheader("📺 Video Preview")
        try:
            st.video(url)
        except:
            st.warning("Preview available nahi hai, par download kaam karega.")

        col1, col2 = st.columns(2)
        format_choice = col1.selectbox("Format:", ["MP4 (Video)", "MP3 (Audio)"])
        
        st.write("✂️ **Trim Settings (Optional)**")
        t_col1, t_col2 = st.columns(2)
        start_time = t_col1.number_input("Start Time (seconds):", min_value=0, value=0)
        end_time = t_col2.number_input("End Time (seconds):", min_value=1, value=60)

        if st.button("🚀 Process & Download"):
            with st.spinner("Processing lightning fast..."):
                try:
                    # Optimized yt-dlp options
                    ydl_opts = {
                        'outtmpl': 'final_output.%(ext)s',
                        'quiet': True,
                        'nocheckcertificate': True
                    }

                    # Handle MP3 vs MP4
                    if "MP3" in format_choice:
                        ydl_opts['format'] = 'bestaudio/best'
                        ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }]
                        final_file = 'final_output.mp3'
                        mime_type = 'audio/mpeg'
                    else:
                        ydl_opts['format'] = 'best'
                        final_file = 'final_output.mp4'
                        mime_type = 'video/mp4'

                    # The Magic Trick: Only download the trimmed part!
                    if start_time >= 0 and end_time > start_time:
                        ydl_opts['external_downloader'] = 'ffmpeg'
                        ydl_opts['external_downloader_args'] = ['-ss', str(start_time), '-to', str(end_time)]

                    # Download exactly what we need
                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])

                    # Show Download Button
                    if os.path.exists(final_file):
                        with open(final_file, "rb") as file:
                            st.download_button(f"⬇️ Download {format_choice}", data=file, file_name=final_file, mime=mime_type)
                        
                        # Cleanup after providing download button
                        os.remove(final_file)
                    else:
                        st.error("File create nahi ho saki. Kripya link check karein.")

                except Exception as e:
                    st.error(f"Error: {e}")

# ---------------- BATCH DOWNLOAD MODE ----------------
else:
    st.info("💡 Har line mein ek link paste karein.")
    urls_text = st.text_area("Links Paste Karein:", height=150)
    batch_format = st.selectbox("Batch Format:", ["MP4 (Video)", "MP3 (Audio)"])
    
    if st.button("Start Batch Download"):
        urls = [link.strip() for link in urls_text.split('\n') if link.strip()]
        
        if not urls:
            st.warning("Pehle links enter karein!")
        else:
            progress_bar = st.progress(0)
            
            for index, link in enumerate(urls):
                with st.spinner(f"Downloading {index + 1} of {len(urls)}..."):
                    try:
                        ydl_opts = {
                            'outtmpl': f'batch_download_{index+1}.%(ext)s',
                            'quiet': True
                        }
                        
                        if "MP3" in batch_format:
                            ydl_opts['format'] = 'bestaudio/best'
                            ydl_opts['postprocessors'] = [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                            }]
                        else:
                            ydl_opts['format'] = 'best'

                        with YoutubeDL(ydl_opts) as ydl:
                            ydl.download([link])
                            
                        st.success(f"Link {index + 1} Done!")
                    except Exception as e:
                        st.error(f"Failed to download link {index + 1}: {e}")
                
                progress_bar.progress((index + 1) / len(urls))
            
            st.success("Batch Download Complete! (Check your files)")
