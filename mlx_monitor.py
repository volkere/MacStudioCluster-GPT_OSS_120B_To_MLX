#!/usr/bin/env python3
"""
MLX Monitoring Tool
Überwacht MLX Memory-Usage, Device-Status und Performance
"""

import mlx.core as mx
import time
import sys
from typing import Dict, Any
import json

class MLXMonitor:
    def __init__(self):
        self.start_time = time.time()
        
    def get_memory_info(self) -> Dict[str, Any]:
        """Gibt MLX Memory-Informationen zurück"""
        try:
            # MLX Memory-Info (wenn verfügbar)
            if hasattr(mx.metal, 'get_memory_info'):
                info = mx.metal.get_memory_info()
                return {
                    'allocated': info.get('allocated', 0),
                    'cached': info.get('cached', 0),
                    'total': info.get('total', 0),
                    'available': info.get('available', 0)
                }
            else:
                # Fallback: System-Info
                return {
                    'allocated': 'N/A',
                    'cached': 'N/A',
                    'total': 'N/A',
                    'available': 'N/A',
                    'note': 'Detailed memory info not available'
                }
        except Exception as e:
            return {'error': str(e)}
    
    def get_device_info(self) -> Dict[str, Any]:
        """Gibt Device-Informationen zurück"""
        device = mx.default_device()
        return {
            'default_device': str(device),
            'device_type': device.device_type if hasattr(device, 'device_type') else 'unknown',
            'device_id': device.device_id if hasattr(device, 'device_id') else 0
        }
    
    def format_bytes(self, bytes_val: Any) -> str:
        """Formatiert Bytes in lesbares Format"""
        if isinstance(bytes_val, str) or bytes_val is None:
            return str(bytes_val)
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.2f} PB"
    
    def print_status(self, format_type: str = 'human'):
        """Druckt aktuellen MLX-Status"""
        memory_info = self.get_memory_info()
        device_info = self.get_device_info()
        uptime = time.time() - self.start_time
        
        if format_type == 'json':
            status = {
                'uptime_seconds': uptime,
                'device': device_info,
                'memory': memory_info,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            print(json.dumps(status, indent=2))
        else:
            print("\n" + "="*60)
            print("MLX Monitoring Status")
            print("="*60)
            print(f"Uptime: {uptime:.2f} seconds")
            print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n--- Device Info ---")
            print(f"Default Device: {device_info['default_device']}")
            print(f"Device Type: {device_info['device_type']}")
            print(f"Device ID: {device_info['device_id']}")
            print("\n--- Memory Info ---")
            if 'error' in memory_info:
                print(f"Error: {memory_info['error']}")
            else:
                if 'allocated' in memory_info and memory_info['allocated'] != 'N/A':
                    print(f"Allocated: {self.format_bytes(memory_info.get('allocated', 0))}")
                    print(f"Cached: {self.format_bytes(memory_info.get('cached', 0))}")
                    print(f"Total: {self.format_bytes(memory_info.get('total', 0))}")
                    if 'available' in memory_info:
                        print(f"Available: {self.format_bytes(memory_info.get('available', 0))}")
                else:
                    print("Detailed memory info not available")
                    print("Note: Use Activity Monitor or system tools for memory monitoring")
            print("="*60 + "\n")
    
    def monitor_loop(self, interval: float = 1.0, duration: float = None):
        """Überwacht MLX kontinuierlich"""
        end_time = time.time() + duration if duration else None
        
        try:
            while True:
                # Clear screen (optional)
                if sys.stdout.isatty():
                    print("\033[2J\033[H", end="")  # ANSI escape codes
                
                self.print_status()
                
                if end_time and time.time() >= end_time:
                    break
                    
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user")
    
    def test_performance(self, iterations: int = 100):
        """Führt einen einfachen Performance-Test durch"""
        print("\nRunning MLX Performance Test...")
        print(f"Iterations: {iterations}")
        
        # Einfacher Test: Matrix-Multiplikation
        size = 1000
        a = mx.random.normal((size, size))
        b = mx.random.normal((size, size))
        
        # Warmup
        for _ in range(10):
            _ = mx.matmul(a, b)
        mx.eval()
        
        # Timing
        start = time.time()
        for _ in range(iterations):
            c = mx.matmul(a, b)
        mx.eval()
        end = time.time()
        
        elapsed = end - start
        ops_per_sec = iterations / elapsed
        
        print(f"\nPerformance Results:")
        print(f"  Matrix Size: {size}x{size}")
        print(f"  Iterations: {iterations}")
        print(f"  Total Time: {elapsed:.4f} seconds")
        print(f"  Operations/sec: {ops_per_sec:.2f}")
        print(f"  Time per operation: {(elapsed/iterations)*1000:.4f} ms")
        print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='MLX Monitoring Tool')
    parser.add_argument('--monitor', '-m', action='store_true',
                        help='Start continuous monitoring')
    parser.add_argument('--interval', '-i', type=float, default=1.0,
                        help='Monitoring interval in seconds (default: 1.0)')
    parser.add_argument('--duration', '-d', type=float,
                        help='Monitoring duration in seconds (default: infinite)')
    parser.add_argument('--json', '-j', action='store_true',
                        help='Output in JSON format')
    parser.add_argument('--test', '-t', action='store_true',
                        help='Run performance test')
    parser.add_argument('--iterations', type=int, default=100,
                        help='Number of iterations for performance test')
    
    args = parser.parse_args()
    
    monitor = MLXMonitor()
    
    if args.test:
        monitor.test_performance(args.iterations)
    elif args.monitor:
        monitor.monitor_loop(args.interval, args.duration)
    else:
        monitor.print_status('json' if args.json else 'human')


if __name__ == '__main__':
    main()

