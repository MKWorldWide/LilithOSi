#!/usr/bin/env python3
"""
LilithOS Boot Animation Generator
Creates custom boot animations for iPhone 13 Pro Max with 120Hz ProMotion support.
"""

import os
import sys
import math
import argparse
import logging
import random  # Use dedicated RNG for reproducible particle effects
from pathlib import Path
from typing import Tuple, List, Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

console = Console()

class LilithOSBootAnimation:
    """Generates custom boot animations for LilithOS."""
    
    def __init__(self, output_dir: str = "resources/boot_animation"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # iPhone 13 Pro Max specifications
        self.width = 2778
        self.height = 1284
        self.fps = 120  # 120Hz ProMotion
        self.duration = 3.2  # seconds
        
        # Animation parameters
        self.total_frames = int(self.fps * self.duration)
        self.frame_duration = 1.0 / self.fps
        
        # Colors (LilithOS theme)
        self.colors = {
            "background": (0, 0, 0),  # Black
            "primary": (138, 43, 226),  # Purple
            "secondary": (75, 0, 130),  # Dark purple
            "accent": (255, 255, 255),  # White
            "glow": (138, 43, 226, 128)  # Purple with alpha
        }
        
        # Animation phases
        self.phases = {
            "fade_in": 0.3,      # 30% of duration
            "main_animation": 0.5,  # 50% of duration
            "fade_out": 0.2      # 20% of duration
        }
    
    def create_logo(self, size: Tuple[int, int]) -> Image.Image:
        """Create the LilithOS logo."""
        logo = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(logo)
        
        # Logo dimensions
        logo_width, logo_height = size
        center_x, center_y = logo_width // 2, logo_height // 2
        
        # Create stylized "L" logo
        # Main vertical line
        line_width = max(20, logo_width // 20)
        line_height = logo_height * 0.7
        
        # Vertical line
        draw.rectangle([
            center_x - line_width // 2,
            center_y - line_height // 2,
            center_x + line_width // 2,
            center_y + line_height // 2
        ], fill=self.colors["primary"])
        
        # Horizontal line
        h_line_width = logo_width * 0.4
        h_line_height = line_width
        
        draw.rectangle([
            center_x - h_line_width // 2,
            center_y + line_height // 2 - h_line_height,
            center_x + h_line_width // 2,
            center_y + line_height // 2
        ], fill=self.colors["primary"])
        
        # Add glow effect
        glow_radius = line_width * 2
        glow = logo.filter(ImageFilter.GaussianBlur(glow_radius))
        
        # Combine glow and logo
        result = Image.new('RGBA', size, (0, 0, 0, 0))
        result.paste(glow, (0, 0), glow)
        result.paste(logo, (0, 0), logo)
        
        return result
    
    def create_text(self, text: str, size: int = 72) -> Image.Image:
        """Create text with custom styling."""
        # Try to use system font, fallback to default
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size)
            except:
                font = ImageFont.load_default()
        
        # Create text image
        text_img = Image.new('RGBA', (self.width, size * 2), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_img)
        
        # Get text bounds
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center text
        x = (self.width - text_width) // 2
        y = (text_img.height - text_height) // 2
        
        # Draw text with glow effect
        glow_color = self.colors["glow"]
        for offset in range(5, 0, -1):
            draw.text((x + offset, y + offset), text, font=font, fill=glow_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=self.colors["accent"])
        
        return text_img
    
    def create_particle_system(
        self,
        frame: int,
        total_frames: int,
        num_particles: int = 50,
        seed: Optional[int] = None,
    ) -> Image.Image:
        """Create animated particle system.

        Using ``random.Random`` with an optional seed keeps particle motion
        deterministic per frame while allowing callers to tweak density.

        Args:
            frame: Current frame index.
            total_frames: Total number of frames in the animation.
            num_particles: How many particles to render.
            seed: Optional seed for reproducible randomness.
        """
        rng = random.Random(seed if seed is not None else frame)
        particles = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(particles)

        particle_size = 3
        max_velocity = 2
        progress = frame / total_frames

        for _ in range(num_particles):
            # Pseudo-random starting position
            x = rng.randint(0, self.width - 1)
            y = rng.randint(0, self.height - 1)

            # Animate particles with a sine wave for subtle movement
            wave = math.sin(progress * math.pi * 2 + rng.random() * 0.1)
            x = (x + wave * max_velocity * 10) % self.width
            y = (y + progress * max_velocity * 5) % self.height

            opacity = int(255 * (1 - abs(wave)))
            color = (*self.colors["primary"][:3], opacity)
            draw.ellipse(
                [x - particle_size, y - particle_size, x + particle_size, y + particle_size],
                fill=color,
            )

        return particles
    
    def create_frame(self, frame: int, total_frames: int) -> Image.Image:
        """Create a single animation frame."""
        # Create base image
        frame_img = Image.new('RGBA', (self.width, self.height), self.colors["background"])
        
        # Calculate animation progress
        progress = frame / total_frames
        
        # Determine animation phase
        if progress < self.phases["fade_in"]:
            phase = "fade_in"
            phase_progress = progress / self.phases["fade_in"]
        elif progress < self.phases["fade_in"] + self.phases["main_animation"]:
            phase = "main_animation"
            phase_progress = (progress - self.phases["fade_in"]) / self.phases["main_animation"]
        else:
            phase = "fade_out"
            phase_progress = (progress - self.phases["fade_in"] - self.phases["main_animation"]) / self.phases["fade_out"]
        
        # Create logo
        logo_size = (400, 400)
        logo = self.create_logo(logo_size)
        
        # Position logo
        logo_x = (self.width - logo_size[0]) // 2
        logo_y = (self.height - logo_size[1]) // 2 - 100
        
        # Apply phase-specific effects
        if phase == "fade_in":
            # Fade in effect
            alpha = int(255 * phase_progress)
            logo.putalpha(alpha)
            
            # Scale effect
            scale = 0.5 + 0.5 * phase_progress
            new_size = (int(logo_size[0] * scale), int(logo_size[1] * scale))
            logo = logo.resize(new_size, Image.Resampling.LANCZOS)
            
        elif phase == "main_animation":
            # Main animation phase
            # Add pulsing effect
            pulse = 1.0 + 0.1 * math.sin(phase_progress * math.pi * 4)
            new_size = (int(logo_size[0] * pulse), int(logo_size[1] * pulse))
            logo = logo.resize(new_size, Image.Resampling.LANCZOS)
            
        else:  # fade_out
            # Fade out effect
            alpha = int(255 * (1 - phase_progress))
            logo.putalpha(alpha)
        
        # Add particle system
        particles = self.create_particle_system(frame, total_frames, seed=frame)
        
        # Create text
        text = self.create_text("LilithOS", 72)
        text_y = logo_y + logo_size[1] + 50
        
        # Apply text effects
        if phase == "fade_in":
            text_alpha = int(255 * phase_progress)
            text.putalpha(text_alpha)
        elif phase == "fade_out":
            text_alpha = int(255 * (1 - phase_progress))
            text.putalpha(text_alpha)
        
        # Composite all elements
        frame_img.paste(particles, (0, 0), particles)
        frame_img.paste(logo, (logo_x, logo_y), logo)
        frame_img.paste(text, (0, text_y), text)
        
        return frame_img
    
    def generate_animation(self) -> str:
        """Generate the complete boot animation."""
        console.print("🎬 Generating LilithOS boot animation...")
        
        frames = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            task = progress.add_task("Creating frames...", total=self.total_frames)
            
            for frame in range(self.total_frames):
                # Create frame
                frame_img = self.create_frame(frame, self.total_frames)
                frames.append(frame_img)
                
                progress.update(task, advance=1)
        
        # Save as GIF
        output_path = self.output_dir / "boot_animation.gif"
        
        console.print("💾 Saving animation...")
        
        # Convert frames to RGB for GIF
        rgb_frames = []
        for frame in frames:
            # Convert RGBA to RGB with black background
            rgb_frame = Image.new('RGB', frame.size, self.colors["background"])
            rgb_frame.paste(frame, (0, 0), frame)
            rgb_frames.append(rgb_frame)
        
        # Save as GIF with optimized settings
        imageio.mimsave(
            output_path,
            rgb_frames,
            duration=self.frame_duration,
            optimize=True,
            quality=85
        )
        
        # Create plist file for iOS
        plist_path = self.output_dir / "BootAnimation.plist"
        self.create_plist(plist_path)
        
        console.print(f"✅ Boot animation created: {output_path}")
        console.print(f"📄 Plist file created: {plist_path}")
        
        return str(output_path)
    
    def create_plist(self, plist_path: Path):
        """Create BootAnimation.plist file for iOS."""
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>UIBackgroundModes</key>
    <array>
        <string>background</string>
    </array>
    <key>CFBundleDisplayName</key>
    <string>LilithOS Boot Animation</string>
    <key>CFBundleIdentifier</key>
    <string>com.lilithos.bootanimation</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
    <key>UISupportedInterfaceOrientations</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
    </array>
    <key>UISupportedInterfaceOrientations~ipad</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
        <string>UIInterfaceOrientationPortraitUpsideDown</string>
        <string>UIInterfaceOrientationLandscapeLeft</string>
        <string>UIInterfaceOrientationLandscapeRight</string>
    </array>
    <key>MinimumOSVersion</key>
    <string>17.0</string>
    <key>DeviceFamily</key>
    <array>
        <integer>1</integer>
        <integer>2</integer>
    </array>
    <key>UIRequiredDeviceCapabilities</key>
    <array>
        <string>armv7</string>
    </array>
    <key>UISupportedDevices</key>
    <array>
        <string>iPhone14,2</string>
    </array>
</dict>
</plist>"""
        
        with open(plist_path, 'w') as f:
            f.write(plist_content)

def main():
    parser = argparse.ArgumentParser(
        description="Generate LilithOS boot animation for iPhone 13 Pro Max",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --output custom_animation
  %(prog)s --fps 60 --duration 5.0
        """
    )
    
    parser.add_argument(
        "--output", 
        default="resources/boot_animation",
        help="Output directory (default: resources/boot_animation)"
    )
    parser.add_argument(
        "--fps", 
        type=int,
        default=120,
        help="Animation FPS (default: 120 for ProMotion)"
    )
    parser.add_argument(
        "--duration", 
        type=float,
        default=3.2,
        help="Animation duration in seconds (default: 3.2)"
    )
    parser.add_argument(
        "--width", 
        type=int,
        default=2778,
        help="Animation width (default: 2778 for iPhone 13 Pro Max)"
    )
    parser.add_argument(
        "--height", 
        type=int,
        default=1284,
        help="Animation height (default: 1284 for iPhone 13 Pro Max)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Create boot animation generator
        generator = LilithOSBootAnimation(args.output)
        
        # Override default parameters if specified
        if args.fps != 120:
            generator.fps = args.fps
            generator.total_frames = int(generator.fps * generator.duration)
            generator.frame_duration = 1.0 / generator.fps
        
        if args.duration != 3.2:
            generator.duration = args.duration
            generator.total_frames = int(generator.fps * generator.duration)
        
        if args.width != 2778:
            generator.width = args.width
        
        if args.height != 1284:
            generator.height = args.height
        
        # Generate animation
        output_path = generator.generate_animation()
        
        console.print(f"🎉 Boot animation generation completed!")
        console.print(f"📁 Output directory: {args.output}")
        console.print(f"🎬 Animation file: {output_path}")
        console.print(f"⚡ FPS: {generator.fps}")
        console.print(f"⏱️ Duration: {generator.duration}s")
        console.print(f"📐 Resolution: {generator.width}x{generator.height}")
        
    except Exception as e:
        console.print(f"❌ Error generating boot animation: {e}", style="bold red")
        sys.exit(1)

if __name__ == "__main__":
    main() 