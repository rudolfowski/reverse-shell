import argparse

from .server import Server

def main():
    parser = argparse.ArgumentParser(description="Reverse shell server")

    parser.add_argument(
        "-l",
        "--listen",
        action='store_true',
        help="Listen",
    )

    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=4444,
        help="Port to listen on (default: 4444)",
    )
    
    parser.add_argument(
        "-s",
        "--secret",
        type=str,
        help="Secret key to authenticate the connection",
    )

    parser.add_argument(
        "-a",
        "--allowed",
        type=str,
        help="Allowed IP address to connect",
    )

    args = parser.parse_args()
    
    s = Server(args)
    s.run()


if __name__ == "__main__":
    main()
