import gradio as gr
from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip
from pathlib import Path
import traceback
import time

# Create a directory to store the converted videos
output_dir = Path("converted")
output_dir.mkdir(exist_ok=True)

def convert_video_to_ratio(videos, target_ratio_str, progress=gr.Progress(track_tqdm=True)):
    """
    Converts uploaded videos to a user-selected aspect ratio by adding black bars.
    """
    try:
        if not videos:
            raise gr.Error("You must upload at least one video. Please try again.")

        # Show processing animation
        yield {
            video_preview: gr.update(visible=True, value="https://i.gifer.com/ZZ5H.gif"),  # Sample loading gif
            status_text: gr.update(visible=True, value="⏳ **Processing... Please wait.**"),
            download_button: gr.update(visible=False)
        }

        ratio_parts = target_ratio_str.split(' ')[0].split(':')
        target_w_ratio = float(ratio_parts[0])
        target_h_ratio = float(ratio_parts[1])
        target_ratio = target_w_ratio / target_h_ratio

        converted_paths = []
        if not isinstance(videos, list):
            videos = [videos]

        for video_temp_file in progress.tqdm(videos, desc="Processing Videos"):
            input_path = video_temp_file.name
            
            with VideoFileClip(input_path) as clip:
                original_ratio = clip.w / clip.h

                if abs(original_ratio - target_ratio) < 0.01:
                    final_clip = clip
                elif original_ratio > target_ratio:
                    final_width = clip.w
                    final_height = int(clip.w / target_ratio)
                    background = ColorClip(size=(final_width, final_height), color=(0, 0, 0), duration=clip.duration)
                    final_clip = CompositeVideoClip([background, clip.set_position("center")])
                else:
                    final_height = clip.h
                    final_width = int(clip.h * target_ratio)
                    background = ColorClip(size=(final_width, final_height), color=(0, 0, 0), duration=clip.duration)
                    final_clip = CompositeVideoClip([background, clip.set_position("center")])

                output_filename = f"converted_{int(time.time())}_{Path(input_path).name}"
                output_path = str(output_dir / output_filename)
                
                final_clip.write_videofile(
                    output_path, codec="libx264", audio_codec="aac",
                    preset="medium", ffmpeg_params=["-crf", "23"], logger=None
                )
                converted_paths.append(output_path)

        first_video_path = converted_paths[0]
        yield {
            video_preview: gr.update(value=first_video_path, visible=True),
            download_button: gr.update(value=first_video_path, visible=True),
            status_text: gr.update(value="✅ **Conversion Successful!**", visible=True)
        }

    except Exception as e:
        traceback.print_exc()
        yield {
            status_text: gr.Markdown.update(value=f"❌ **Error:** {e}", visible=True),
            video_preview: gr.update(visible=False),
            download_button: gr.update(visible=False)
        }

# Theme
theme = gr.themes.Soft(primary_hue="blue", secondary_hue="sky").set(
    body_background_fill="#f0f2f6",
    block_background_fill="white",
    block_border_width="1px",
    block_shadow="*shadow_drop_lg",
    body_text_color_subdued="#485563"
)

with gr.Blocks(theme=theme, css="""
footer { display: none !important; }
.gr-video video { width: 100% !important; height: auto !important; border-radius: 10px; }
""") as demo:

    gr.Markdown("# 🖼️ Universal Aspect Ratio Converter")
    gr.Markdown("Upload a video, choose a target aspect ratio, and get a perfectly formatted new video. Ideal for social media and content creators.")
    
    with gr.Row(variant="panel"):
        with gr.Column(scale=1):
            gr.Markdown("### Step 1: Upload Your Video(s)")
            file_uploader = gr.File(file_types=["video"], file_count="multiple", label="🎬 Upload Videos")

            gr.Markdown("### Step 2: Choose Target Ratio")
            ratio_dropdown = gr.Dropdown(
                choices=[
                    "9:16 (TikTok, Reels, Shorts)", "4:5 (Instagram Portrait)", "1:1 (Instagram Square)",
                    "4:3 (Classic TV)", "3:2 (Photography)", "16:9 (YouTube, Widescreen)",
                    "1.85:1 (Film)", "2.39:1 (Cinema)"
                ],
                label="Target Aspect Ratio",
                value="9:16 (TikTok, Reels, Shorts)"
            )

            gr.Markdown("### Step 3: Convert!")
            btn_convert = gr.Button("🚀 Convert Video", variant="primary")

        with gr.Column(scale=2):
            gr.Markdown("### 🎞️ Output Preview")
            video_preview = gr.Video(visible=False, label="Converted Video")
            download_button = gr.DownloadButton(label="⬇️ Download Video", visible=False)
            status_text = gr.Markdown(visible=False)

    gr.Markdown("<div style='text-align: center;'>Made with ❤️ by <b>Yash Dhanani</b></div>")

    btn_convert.click(
        fn=convert_video_to_ratio,
        inputs=[file_uploader, ratio_dropdown],
        outputs=[video_preview, download_button, status_text]
    )

if __name__ == "__main__":
    demo.launch()
