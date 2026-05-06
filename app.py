import gradio as gr
from moviepy.editor import VideoFileClip, CompositeVideoClip, ColorClip
from pathlib import Path
import traceback
import time

# Create output directory
output_dir = Path("converted")
output_dir.mkdir(exist_ok=True)


def convert_video_to_ratio(videos, target_ratio_str, progress=gr.Progress()):
    """
    Convert uploaded videos to selected aspect ratio
    by adding black padding bars.
    """

    try:
        if not videos:
            raise gr.Error("Please upload at least one video.")

        # Initial UI state
        yield (
            gr.update(visible=False),  # video preview
            gr.update(visible=False),  # download button
            gr.update(
                value="⏳ Processing videos... Please wait.",
                visible=True
            )  # status text
        )

        # Parse target ratio
        ratio_parts = target_ratio_str.split(" ")[0].split(":")
        target_w_ratio = float(ratio_parts[0])
        target_h_ratio = float(ratio_parts[1])
        target_ratio = target_w_ratio / target_h_ratio

        converted_paths = []

        # Ensure videos is always a list
        if not isinstance(videos, list):
            videos = [videos]

        for index, video_temp_file in enumerate(videos):

            progress(
                (index + 1) / len(videos),
                desc=f"Processing {Path(video_temp_file.name).name}"
            )

            input_path = video_temp_file.name

            with VideoFileClip(input_path) as clip:

                original_ratio = clip.w / clip.h

                # If ratio already matches
                if abs(original_ratio - target_ratio) < 0.01:
                    final_clip = clip

                # Video is wider than target
                elif original_ratio > target_ratio:

                    final_width = clip.w
                    final_height = int(clip.w / target_ratio)

                    background = ColorClip(
                        size=(final_width, final_height),
                        color=(0, 0, 0),
                        duration=clip.duration
                    )

                    final_clip = CompositeVideoClip([
                        background,
                        clip.set_position("center")
                    ])

                # Video is taller than target
                else:

                    final_height = clip.h
                    final_width = int(clip.h * target_ratio)

                    background = ColorClip(
                        size=(final_width, final_height),
                        color=(0, 0, 0),
                        duration=clip.duration
                    )

                    final_clip = CompositeVideoClip([
                        background,
                        clip.set_position("center")
                    ])

                # Output path
                output_filename = (
                    f"converted_{int(time.time())}_"
                    f"{Path(input_path).stem}.mp4"
                )

                output_path = str(output_dir / output_filename)

                # Export video
                final_clip.write_videofile(
                    output_path,
                    codec="libx264",
                    audio_codec="aac",
                    preset="medium",
                    ffmpeg_params=["-crf", "23"],
                    logger=None
                )

                converted_paths.append(output_path)

        # Final output
        first_video_path = converted_paths[0]

        yield (
            gr.update(
                value=first_video_path,
                visible=True
            ),
            gr.update(
                value=first_video_path,
                visible=True
            ),
            gr.update(
                value="✅ Conversion Successful!",
                visible=True
            )
        )

    except Exception as e:

        traceback.print_exc()

        yield (
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(
                value=f"❌ Error: {str(e)}",
                visible=True
            )
        )


# ---------------- UI ---------------- #

theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="sky"
).set(
    body_background_fill="#f0f2f6",
    block_background_fill="white",
    block_border_width="1px",
    body_text_color_subdued="#485563"
)


custom_css = """
footer {
    display: none !important;
}

.gr-video video {
    width: 100% !important;
    height: auto !important;
    border-radius: 12px;
}
"""


with gr.Blocks(theme=theme, css=custom_css) as demo:

    gr.Markdown("# 🖼️ Universal Aspect Ratio Converter")

    gr.Markdown(
        """
        Upload videos and convert them into different aspect ratios
        for TikTok, Reels, Shorts, YouTube, Cinema, and more.
        """
    )

    with gr.Row():

        # Left Panel
        with gr.Column(scale=1):

            gr.Markdown("## 🎬 Upload Video(s)")

            file_uploader = gr.File(
                file_types=["video"],
                file_count="multiple",
                label="Upload Videos"
            )

            gr.Markdown("## 📐 Select Aspect Ratio")

            ratio_dropdown = gr.Dropdown(
                choices=[
                    "9:16 (TikTok, Reels, Shorts)",
                    "4:5 (Instagram Portrait)",
                    "1:1 (Instagram Square)",
                    "4:3 (Classic TV)",
                    "3:2 (Photography)",
                    "16:9 (YouTube, Widescreen)",
                    "1.85:1 (Film)",
                    "2.39:1 (Cinema)"
                ],
                value="9:16 (TikTok, Reels, Shorts)",
                label="Target Aspect Ratio"
            )

            convert_btn = gr.Button(
                "🚀 Convert Video",
                variant="primary"
            )

        # Right Panel
        with gr.Column(scale=2):

            gr.Markdown("## 🎞️ Preview")

            video_preview = gr.Video(
                label="Converted Video",
                visible=False
            )

            download_button = gr.DownloadButton(
                label="⬇️ Download Video",
                visible=False
            )

            status_text = gr.Markdown(
                visible=False
            )

    gr.Markdown(
        """
        <div style='text-align:center; margin-top:20px;'>
            Made with ❤️ by <b>Yash Dhanani</b>
        </div>
        """
    )

    convert_btn.click(
        fn=convert_video_to_ratio,
        inputs=[
            file_uploader,
            ratio_dropdown
        ],
        outputs=[
            video_preview,
            download_button,
            status_text
        ]
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0")
