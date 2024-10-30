import argparse
import logging
import os
import subprocess

# Command-line sys.argv parser
parser = argparse.ArgumentParser(
    prog="py-ffmpeg", description="Compress all images in a directory with FFMPEG"
)
parser.add_argument("-i", "--input", help="input directory")
parser.add_argument("-o", "--output", help="output directory")
parser.print_help()

args = parser.parse_args()

# Define source and destination directories
SRC_DIR = args.input
DST_DIR = args.output

logging.basicConfig(level=logging.INFO)
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# add the handler to the root logger
logging.getLogger("").addHandler(console)

logger = logging.getLogger(__name__)


def make_directory(directory: str, log_message: str) -> None:
    logger.info(f"{log_message}: {directory}")
    os.makedirs(directory, exist_ok=True)


def uniformize_image_to_jpg(dst_dir: str, img_relative_path: str) -> str:
    if not img_relative_path.lower().endswith(".jpg"):
        return os.path.join(dst_dir, os.path.splitext(img_relative_path)[0] + ".jpg")

    return os.path.join(dst_dir, img_relative_path)


def handle_ffmpeg_process_code(
    result: subprocess.CompletedProcess, src_file: str, dst_file: str
) -> None:
    if result.returncode != 0:
        logger.error(
            f"Error compressing {src_file} to {
                     dst_file} with code {result.returncode}"
        )
        logger.error(
            f"FFmpeg output:\n{result.stdout.decode()}\n{
                     result.stderr.decode()}"
        )
        return

    logger.info(f"Successfully compressed {src_file} to {dst_file}")


def main() -> None:
    # Early exit if source or destination directories are not specified
    if SRC_DIR is None or DST_DIR is None:
        return

    if not os.path.exists(SRC_DIR):
        logger.error(f"Source directory does not exist: {SRC_DIR}")
        return

    if os.path.exists(DST_DIR):
        logger.info(f"Destination directory already exists: {SRC_DIR}")
    else:
        make_directory(DST_DIR, "Creating destination directory")

    for root, dirs, files in os.walk(SRC_DIR):
        for file in files:
            # Skip non-image files
            if not file.lower().endswith((".jpg", ".jpeg", ".png")):
                logger.warning(f"Skipping non-image file: {file}")
                continue

            src_file = os.path.join(root, file)
            logger.info(f"Found image file: {src_file}")

            relative_path = os.path.relpath(src_file, SRC_DIR)
            logger.info(f"Relative path: {relative_path}")

            dst_file = uniformize_image_to_jpg(DST_DIR, relative_path)

            logger.info(f"Destination file path: {dst_file}")

            dst_dir = os.path.dirname(dst_file)
            if not os.path.exists(dst_dir):
                make_directory(dst_dir, "Creating destination sub-directory")

            # Compress the image using ffmpeg
            compression_args = ["-q:v", "5"]  # Medium quality for JPEG

            logger.info(
                f"Compressing {src_file} to {
                        dst_file} with settings {compression_args}"
            )
            result = subprocess.run(
                ["ffmpeg", "-i", src_file] + compression_args + [dst_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Check for successful execution
            handle_ffmpeg_process_code(result, src_file, dst_file)


if __name__ == "__main__":
    main()
