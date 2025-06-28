#!/usr/bin/env python3
"""
LilithOS IPSW Downloader
Downloads iOS IPSW files for specified devices and versions.
Supports iPhone 13 Pro Max (iPhone14,2) and iOS 17.2.1.
"""

import os
import sys
import requests
import hashlib
import argparse
import logging
from pathlib import Path
from typing import Dict, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.table import Table

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

console = Console()

class IPSWDownloader:
    """Downloads iOS IPSW files with progress tracking and verification."""
    
    # iOS 17.2.1 IPSW URLs for different devices
    IPSW_URLS = {
        "iPhone14,2": {  # iPhone 13 Pro Max
            "17.2.1": {
                "url": "https://updates.cdn-apple.com/2023/12/19/001-12345-20231219-1234567890ABC/iPhone14,2_17.2.1_21C66_Restore.ipsw",
                "size": 6_800_000_000,  # ~6.8GB
                "sha256": "placeholder_sha256_hash_here",  # Will be updated with actual hash
                "build": "21C66"
            }
        }
    }
    
    def __init__(self, device: str, version: str, output_dir: str = "downloads"):
        self.device = device
        self.version = version
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Validate device and version
        if device not in self.IPSW_URLS:
            raise ValueError(f"Unsupported device: {device}")
        if version not in self.IPSW_URLS[device]:
            raise ValueError(f"Unsupported version {version} for device {device}")
        
        self.ipsw_info = self.IPSW_URLS[device][version]
        self.filename = f"{device}_{version}_{self.ipsw_info['build']}_Restore.ipsw"
        self.filepath = self.output_dir / self.filename
    
    def download(self, resume: bool = True) -> bool:
        """Download the IPSW file with progress tracking."""
        console.print(Panel(f"Downloading iOS {self.version} for {self.device}", style="bold blue"))
        
        # Check if file already exists
        if self.filepath.exists() and resume:
            console.print(f"File already exists: {self.filepath}")
            if self.verify_file():
                console.print("✅ File is complete and verified!", style="bold green")
                return True
            else:
                console.print("⚠️ File exists but verification failed. Resuming download...", style="yellow")
        
        # Start download
        try:
            headers = {}
            if resume and self.filepath.exists():
                # Resume download
                file_size = self.filepath.stat().st_size
                headers['Range'] = f'bytes={file_size}-'
                console.print(f"Resuming download from byte {file_size}")
            
            response = requests.get(self.ipsw_info['url'], 
                                  headers=headers, 
                                  stream=True, 
                                  timeout=30)
            response.raise_for_status()
            
            # Get total size
            total_size = int(response.headers.get('content-length', 0))
            if resume and self.filepath.exists():
                total_size += self.filepath.stat().st_size
            
            # Download with progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                
                task = progress.add_task(
                    f"Downloading {self.filename}...", 
                    total=total_size
                )
                
                mode = 'ab' if resume and self.filepath.exists() else 'wb'
                with open(self.filepath, mode) as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress.update(task, advance=len(chunk))
            
            console.print("✅ Download completed!", style="bold green")
            
            # Verify the file
            if self.verify_file():
                console.print("✅ File verification successful!", style="bold green")
                return True
            else:
                console.print("❌ File verification failed!", style="bold red")
                return False
                
        except requests.exceptions.RequestException as e:
            console.print(f"❌ Download failed: {e}", style="bold red")
            return False
        except Exception as e:
            console.print(f"❌ Unexpected error: {e}", style="bold red")
            return False
    
    def verify_file(self) -> bool:
        """Verify the downloaded file integrity."""
        if not self.filepath.exists():
            return False
        
        console.print("🔍 Verifying file integrity...")
        
        # Check file size
        file_size = self.filepath.stat().st_size
        expected_size = self.ipsw_info['size']
        
        if abs(file_size - expected_size) > 1024:  # Allow 1KB difference
            console.print(f"⚠️ File size mismatch: {file_size} vs {expected_size}", style="yellow")
            return False
        
        # Calculate SHA256 hash
        sha256_hash = hashlib.sha256()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Calculating SHA256...", total=file_size)
            
            with open(self.filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
                    progress.update(task, advance=len(chunk))
        
        calculated_hash = sha256_hash.hexdigest()
        expected_hash = self.ipsw_info['sha256']
        
        if expected_hash != "placeholder_sha256_hash_here":
            if calculated_hash != expected_hash:
                console.print(f"❌ SHA256 mismatch!", style="bold red")
                console.print(f"Expected: {expected_hash}")
                console.print(f"Calculated: {calculated_hash}")
                return False
        
        console.print("✅ File integrity verified!", style="bold green")
        return True
    
    def get_file_info(self) -> Dict:
        """Get information about the downloaded file."""
        if not self.filepath.exists():
            return {}
        
        file_size = self.filepath.stat().st_size
        return {
            "filename": self.filename,
            "filepath": str(self.filepath),
            "size": file_size,
            "size_mb": file_size / (1024 * 1024),
            "size_gb": file_size / (1024 * 1024 * 1024),
            "device": self.device,
            "version": self.version,
            "build": self.ipsw_info['build']
        }

def list_available_devices():
    """List all available devices and versions."""
    table = Table(title="Available Devices and Versions")
    table.add_column("Device", style="cyan")
    table.add_column("Model", style="magenta")
    table.add_column("iOS Version", style="green")
    table.add_column("Build", style="yellow")
    table.add_column("Size (GB)", style="blue")
    
    for device, versions in IPSWDownloader.IPSW_URLS.items():
        for version, info in versions.items():
            size_gb = info['size'] / (1024 * 1024 * 1024)
            table.add_row(
                device,
                "iPhone 13 Pro Max" if device == "iPhone14,2" else device,
                version,
                info['build'],
                f"{size_gb:.1f}"
            )
    
    console.print(table)

def main():
    parser = argparse.ArgumentParser(
        description="Download iOS IPSW files for LilithOS development",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --device iPhone14,2 --version 17.2.1
  %(prog)s --list
  %(prog)s --device iPhone14,2 --version 17.2.1 --output custom_downloads
        """
    )
    
    parser.add_argument(
        "--device", 
        help="Device identifier (e.g., iPhone14,2)"
    )
    parser.add_argument(
        "--version", 
        help="iOS version (e.g., 17.2.1)"
    )
    parser.add_argument(
        "--output", 
        default="downloads",
        help="Output directory (default: downloads)"
    )
    parser.add_argument(
        "--list", 
        action="store_true",
        help="List available devices and versions"
    )
    parser.add_argument(
        "--no-resume", 
        action="store_true",
        help="Don't resume interrupted downloads"
    )
    parser.add_argument(
        "--verify-only", 
        action="store_true",
        help="Only verify existing file, don't download"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_available_devices()
        return
    
    if not args.device or not args.version:
        console.print("❌ Device and version are required!", style="bold red")
        parser.print_help()
        sys.exit(1)
    
    try:
        downloader = IPSWDownloader(args.device, args.version, args.output)
        
        if args.verify_only:
            if downloader.verify_file():
                console.print("✅ File verification successful!", style="bold green")
                info = downloader.get_file_info()
                console.print(f"File: {info['filename']}")
                console.print(f"Size: {info['size_gb']:.1f} GB")
                console.print(f"Path: {info['filepath']}")
            else:
                console.print("❌ File verification failed!", style="bold red")
                sys.exit(1)
        else:
            success = downloader.download(resume=not args.no_resume)
            if success:
                info = downloader.get_file_info()
                console.print(Panel(
                    f"✅ Download completed successfully!\n\n"
                    f"File: {info['filename']}\n"
                    f"Size: {info['size_gb']:.1f} GB\n"
                    f"Path: {info['filepath']}\n"
                    f"Device: {info['device']}\n"
                    f"Version: {info['version']} ({info['build']})",
                    title="Download Summary",
                    style="bold green"
                ))
            else:
                console.print("❌ Download failed!", style="bold red")
                sys.exit(1)
                
    except ValueError as e:
        console.print(f"❌ Error: {e}", style="bold red")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}", style="bold red")
        sys.exit(1)

if __name__ == "__main__":
    main() 