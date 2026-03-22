import streamlit as st
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip
import os

st.set_page_config(page_title="Pro Media Downloader", layout="wide")

st.title("📲 Pro Media Downloader")
st.markdown("Download single videos with trim options, or batch download multiple links!")

# Mode Selection
mode = st.radio("Mode Select Karein:", ["Single Video (Preview & Trim)", "Batch Download (Multiple Links)"])

# ---------------- SINGLE VIDEO MODE ----------------
if mode == "Single Video (Preview & Trim)":
    url = st.text_input("Link Paste Karein:")
    
    if url:
        st.subheader("📺 Video Preview")
        # Streamlit ka built-in video player directly YouTube links support karta hai
        try:
            st.video(url)
        except:
            st.warning("Preview is link ke liye available nahi hai, par download kaam karega.")

        col1, col2 = st.columns(2)
        format_choice = col1.selectbox("Format:", ["MP4 (Video)", "MP3 (Audio)"])
        
        st.write("✂️ **Trim Settings (Optional)**")
        t_col1, t_col2 = st.columns(2)
        start_time = t_col1.number_input("Start Time (seconds):", min_value=0, value=0)
        end_time = t_col2.number_input("End Time (seconds):", min_value=1, value=60)

        if st.button("Download Single File"):
            with st.spinner("Processing... Please wait."):
                try:
                    ydl_opts = {'format': 'best', 'outtmpl': 'temp_video.%(ext)s'}
                    with YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        filename = ydl.prepare_filename(info)

                    # Trimming and Conversion
                    clip = VideoFileClip(filename).subclip(start_time, end_time)
                    out_file = "output.mp3" if "MP3" in format_choice else "output.mp4"
                    
                    if "MP3" in format_choice:
                        clip.audio.write_audiofile(out_file)
                    else:
                        clip.write_videofile(out_file, codec="libx264")

                    # Download Button
                    with open(out_file, "rb") as file:
                        st.download_button(f"⬇️ Download {format_choice}", data=file, file_name=out_file)
                    
                    clip.close()
                    os.remove(filename)
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
            st.write(f"Total files: {len(urls)}")
            
            for index, link in enumerate(urls):
                with st.spinner(f"Downloading {index + 1} of {len(urls)}..."):
                    try:
                        # Logic for MP3 vs MP4
                        if "MP3" in batch_format:
                            ydl_opts = {
                                'format': 'bestaudio/best',
                                'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}],
                                'outtmpl': f'batch_download_{index+1}.%(ext)s'
                            }
                        else:
                            ydl_opts = {'format': 'best', 'outtmpl': f'batch_download_{index+1}.%(ext)s'}

                        with YoutubeDL(ydl_opts) as ydl:
                            ydl.download([link])
                            
                        st.success(f"File {index + 1} downloaded successfully! (Check your project folder)")
                    except Exception as e:
                        st.error(f"Failed to download link {index + 1}: {e}")
                
                # Update progress
                progress_bar.progress((index + 1) / len(urls))
            
            st.balloons()
            st.success("Batch Download Complete! Files aapke project folder mein save ho gayi hain.")
