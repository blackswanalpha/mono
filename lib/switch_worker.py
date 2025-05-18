"""
Switch Worker - Worker process for running Switch applications

This module provides a worker process for running Switch applications.
It is used by the Switch CLI to run applications with multiple worker processes.
"""

import os
import sys
import argparse
import signal
import time
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import the Switch modules
from lib.switch_interpreter import SwitchInterpreter

def main():
    """Main entry point for the worker process."""
    # Parse arguments
    parser = argparse.ArgumentParser(description="Switch Worker")
    parser.add_argument("file", help="Mono script file to run")
    parser.add_argument("--worker-id", type=int, default=0, help="Worker ID")
    parser.add_argument("--ssr", action="store_true", help="Enable server-side rendering")
    parser.add_argument("--hmr", action="store_true", help="Enable hot module replacement")
    parser.add_argument("--no-kits", action="store_true", help="Disable kit integration")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Set environment variables
    os.environ["SWITCH_WORKER_ID"] = str(args.worker_id)
    
    # Handle signals
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    
    # Create the Switch interpreter
    interpreter = SwitchInterpreter(
        use_ssr=args.ssr,
        use_hmr=args.hmr,
        use_kits=not args.no_kits,
        debug=args.debug
    )
    
    # Parse the file
    try:
        interpreter.parse_file(args.file)
        
        # Run the interpreter
        interpreter.run()
        
        # Keep the process running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nWorker stopped")
        return 0
    except Exception as e:
        if args.debug:
            # Print detailed error information in debug mode
            import traceback
            print(f"Worker {args.worker_id} error: {str(e)}")
            print(traceback.format_exc())
        else:
            # Print simple error message in production mode
            print(f"Worker {args.worker_id} error: {str(e)}")
            print("Run with --debug for more information.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
