import ec.interface_tk
import ec.interface_cli
from sys import argv


def main():
    if len(argv) == 1 or len(argv) == 2 and argv[1].lower() == 'tk':
        ec.interface_tk.main()
    elif len(argv) == 2 and argv[1].lower() == 'cli':
        ec.interface_cli.Interface()
    else:
        print("Invalid arguments. Need 'cli' or 'tk'.")

if __name__ == '__main__':
    main()
