"""
Download relaxation audio files for the Mental Health App
Run this script to download all audio files to the audio folder
"""

import urllib.request
import os

# Create audio directory if it doesn't exist
os.makedirs("audio", exist_ok=True)

# Audio files to download (free from Pixabay)
audio_files = {
    "ocean_waves.mp3": "https://cdn.pixabay.com/download/audio/2022/03/10/audio_4a1ad0b93c.mp3",
    "gentle_rain.mp3": "https://cdn.pixabay.com/download/audio/2022/05/13/audio_2b1d1a6e5e.mp3",
    "forest_birds.mp3": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_c610232532.mp3",
    "crackling_fire.mp3": "https://cdn.pixabay.com/download/audio/2022/03/10/audio_9b0073c0c5.mp3",
    "wind_chimes.mp3": "https://cdn.pixabay.com/download/audio/2021/08/04/audio_12b0c7443c.mp3",
    "soft_piano.mp3": "https://cdn.pixabay.com/download/audio/2022/08/02/audio_0625c1539c.mp3",
    "singing_bowl.mp3": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_4dedf2bf94.mp3",
    "meditation_bell.mp3": "https://cdn.pixabay.com/download/audio/2021/08/04/audio_d1718ab41b.mp3",
    "meditation_music.mp3": "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3",
}

print("=" * 60)
print("  Downloading Relaxation Audio Files")
print("=" * 60)
print()

for filename, url in audio_files.items():
    filepath = os.path.join("audio", filename)
    
    # Skip if file already exists
    if os.path.exists(filepath):
        print(f"✓ {filename} already exists, skipping...")
        continue
    
    try:
        print(f"⬇️  Downloading {filename}...")
        urllib.request.urlretrieve(url, filepath)
        
        # Check file size
        size = os.path.getsize(filepath)
        size_mb = size / (1024 * 1024)
        
        print(f"✅ Downloaded {filename} ({size_mb:.2f} MB)")
        
    except Exception as e:
        print(f"❌ Error downloading {filename}: {str(e)}")
        print(f"   You can manually download from: {url}")

print()
print("=" * 60)
print("  Download Complete!")
print("=" * 60)
print()
print("Audio files saved to: audio/")
print()
print("Next steps:")
print("1. Run: streamlit run enhanced_app.py")
print("2. Go to: Stress Relief Games → Relaxation Sounds")
print("3. Enjoy your local audio files!")
print()
